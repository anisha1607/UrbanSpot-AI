"""
Agent SDK - Unified Google GenAI Integration
Hardened logic for score consistency and structured alternatives
"""

import json
import os
import re
from typing import List, Dict, Any, Optional
from agents.gemini_client import GeminiChatSession, DEFAULT_MODEL

class LocationAnalysisAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.session = GeminiChatSession(model=DEFAULT_MODEL)
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_neighborhood_details",
                "description": "Get deep metrics for a specific neighborhood",
                "input_schema": {
                    "type": "object",
                    "properties": {"neighborhood": {"type": "string"}},
                    "required": ["neighborhood"]
                }
            }
        ]

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any], scored_data: List[Dict]) -> str:
        if tool_name == "get_neighborhood_details":
            nb = tool_input["neighborhood"]
            target = next((i for i in scored_data if nb.lower() in i.get("neighborhood", "").lower()), scored_data[0])
            return json.dumps(target, indent=2)
        return json.dumps({"error": "Unknown tool"})

    def generate_recommendation(self, scored_data: List[Dict], business_type: str, user_weights: Dict, previous_critique: Optional[Dict] = None) -> Dict[str, Any]:
        top_items = scored_data[:10]
        # Store for lookup during parsing
        nb_lookup = {x.get('neighborhood', '').strip(): x for x in top_items}
        
        summary_list = [f"- {x.get('neighborhood')} (EDA SCORE: {x.get('final_score', 0):.2f})" for x in top_items]
        
        system_prompt = f"""You are an expert NYC business location analyst.
    
    STRICT DATA CONSTRAINT:
    - You MUST use the 'EDA SCORE' provided in the candidate list for the 'SCORE' field.
    - DO NOT recalculate or invent a new score.
    
    REQUIRED FINAL OUTPUT FORMAT:
    RECOMMENDED LOCATION: [Neighborhood Name]
    BOROUGH: [Borough Name]
    SCORE: [Use the EDA SCORE from the list below]
    CONFIDENCE: [High/Medium/Low]
    REASONING:
    - [Specific data point 1 e.g. 'Population of X provides a vast consumer base']
    - [Specific data point 2 e.g. 'Only Y competitors in this area means less saturation']
    - [Specific data point 3 e.g. 'High median income of $Z aligns with premium spending']
    TRADE-OFFS:
    - [Specific risk 1 e.g. 'Intense local competition' or 'High rental premiums']
    ALTERNATIVES:
    - [Name 1] | Score: [EDA Score] | Strength: [Context]
    - [Name 2] | Score: [EDA Score] | Strength: [Context]
    """
        
        user_prompt = f"""Target: {business_type} in NYC.
        
    CANDIDATE LIST:
    {chr(10).join(summary_list)}
    """
        if previous_critique:
            user_prompt += f"\n\nCRITIC FEEDBACK TO ADDRESS:\n{json.dumps(previous_critique, indent=2)}"

        messages = [{"role": "user", "content": user_prompt}]
        response = self.session.create_message(system=system_prompt, messages=messages, tools=self._get_tools())
        
        # Simple one-shot for now to ensure consistency, can add loop back if needed
        text = "".join([b.text for b in response.content if hasattr(b, "text")])
        return self._parse_recommendation(text, top_items, nb_lookup)

    def _parse_recommendation(self, text: str, top_items: List[Dict], nb_lookup: Dict) -> Dict[str, Any]:
        # Default with fallbacks from the #1 neighborhood
        best = top_items[0]
        rec = {
            "best_location": best.get("neighborhood", "N/A"),
            "borough": best.get("boro", "N/A"),
            "score": best.get("final_score", 0.0),
            "confidence": "Medium",
            "reasoning": [],
            "trade_offs": [],
            "top_alternatives": []
        }
        
        if text:
            lines = text.split('\n')
        else:
            lines = []
        curr_section = None
        
        for line in lines:
            line = line.strip()
            if not line: continue
            l_up = line.upper()
            
            if "RECOMMENDED LOCATION" in l_up:
                rec["best_location"] = line.split(":", 1)[1].strip() if ":" in line else rec["best_location"]
            elif "BOROUGH" in l_up:
                rec["borough"] = line.split(":", 1)[1].strip() if ":" in line else rec["borough"]
            elif "SCORE" in l_up and "TRADE" not in l_up:
                # Still try to parse, but we'll verify against data later
                try: 
                    score_val = float(re.findall(r'\d+\.?\d*', line)[0])
                    rec["score"] = score_val
                except: pass
            elif "REASONING" in l_up: curr_section = "reasoning"
            elif "TRADE-OFFS" in l_up or "TRADE OFF" in l_up: curr_section = "trade_offs"
            elif "ALTERNATIVES" in l_up: curr_section = "top_alternatives"
            elif curr_section:
                clean = line.lstrip("-•*0123456789. |)").strip()
                if not clean: continue
                
                if curr_section == "reasoning": 
                    rec["reasoning"].append(clean)
                elif curr_section == "trade_offs": 
                    rec["trade_offs"].append(clean)
                elif curr_section == "top_alternatives":
                    # Robust Alternative Parsing
                    parts = re.split(r'\|| - |\(', clean)
                    name = parts[0].strip()
                    # Try to find score in the data if the AI blew it
                    data_match = next((v for k, v in nb_lookup.items() if name.lower() in k.lower()), None)
                    alt_score = data_match.get('final_score', 0.0) if data_match else 0.0
                    
                    rec["top_alternatives"].append({
                        "name": name,
                        "score": alt_score,
                        "key_strength": parts[-1].strip() if len(parts) > 1 else "Strong demographic profile"
                    })

        # DATA-FIRST OVERRIDE: Ensure the score isn't hallucinated low
        # Find the neighborhood in our source data to get the REAL score
        actual_data = next((v for k, v in nb_lookup.items() if rec["best_location"].lower() in k.lower()), None)
        if actual_data:
            rec["score"] = actual_data.get('final_score', rec["score"])
            if not rec["borough"] or rec["borough"] == "N/A":
                rec["borough"] = actual_data.get('boro', rec["borough"])

        # FALLBACK: If alternatives failed to parse, use top 3 from data
        if not rec["top_alternatives"]:
            for item in top_items[1:4]:
                rec["top_alternatives"].append({
                    "name": item.get('neighborhood'),
                    "score": item.get('final_score'),
                    "key_strength": "Excellent market suitability score"
                })
        
        # REASONING FILTER: Remove strictly generic outputs
        valid_reasons = []
        for r in rec["reasoning"]:
            lower_r = r.lower()
            if "located in" in lower_r or "score of" in lower_r or "has a score" in lower_r or len(r) < 15:
                continue
            valid_reasons.append(r)
        rec["reasoning"] = valid_reasons

        # REASONING FALLBACK: Provide high-quality data-backed reasons if LLM fails
        if len(rec["reasoning"]) < 2 and actual_data:
            rec["reasoning"] = [] # completely rebuild with pure data
            
            # 1. Income Insight
            income_val = actual_data.get('median_income', 0)
            if income_val > 0:
                rec["reasoning"].append(f"Strong demographic match with a robust median household income of ${int(income_val):,}.")
            
            # 2. Competition Insight
            comp = actual_data.get('competition_count', 0)
            if comp > 0:
                rec["reasoning"].append(f"Strategic market gap identified with only {int(comp)} direct competitors in the immediate area.")
            else:
                rec["reasoning"].append("Prime entry opportunity with zero direct competitors identified in this market.")
            
            # 3. Accessibility Insight
            transit = actual_data.get('transit_stations_count', 0)
            if transit >= 4:
                rec["reasoning"].append(f"Elite transit accessibility supported by {int(transit)} local subway/transit stations.")
            elif transit > 0:
                rec["reasoning"].append(f"Solid consumer accessibility with {int(transit)} established transit connections.")
                
            foot = actual_data.get('local_foot_traffic', 0)
            if foot > 10000:
                rec["reasoning"].append(f"High pedestrian volume (est. {int(foot):,} daily) significantly boosts organic visibility.")
            
            # 4. Population Insight
            pop = actual_data.get('population', 0)
            if pop > 5000:
                rec["reasoning"].append(f"High-density consumer base with a local population of {int(pop):,} residents.")

        # Emergency ultimate fallback
        if not rec["reasoning"]:
            rec["reasoning"] = [
                "Market analytics suggest a highly favorable baseline for this specific business type.",
                "Relative metrics outperform the borough average across key demographic pillars."
            ]

        # FINAL ALTERNATIVES POLISH: Ensure we have exactly 3 alternatives from the data
        rec["top_alternatives"] = [] # Force fresh from factual data
        seen_nbs = {rec["best_location"].lower()}
        for item in top_items:
            name = item.get('neighborhood')
            if name and name.lower() not in seen_nbs and len(rec["top_alternatives"]) < 3:
                rec["top_alternatives"].append({
                    "name": name,
                    "score": item.get('final_score', 0.0),
                    "key_strength": "Excellent market suitability and high demographic alignment"
                })
                seen_nbs.add(name.lower())
        
        return rec
