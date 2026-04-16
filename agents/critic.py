"""
Critic Agent - Refined logic for explicit approval/rejection
"""

from typing import Dict, Any, List
import json
from agents.gemini_client import GeminiChatSession, DEFAULT_MODEL

class CriticAgent:
    def __init__(self, api_key: str = None):
        self.session = GeminiChatSession(model=DEFAULT_MODEL)
        
    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "check_data_quality",
                "description": "Verifies data completeness for a neighborhood",
                "input_schema": {
                    "type": "object",
                    "properties": {"neighborhood": {"type": "string"}},
                    "required": ["neighborhood"]
                }
            },
            {
                "name": "identify_missing_considerations",
                "description": "Checks for missing business-specific factors",
                "input_schema": {
                    "type": "object",
                    "properties": {"business_type": {"type": "string"}},
                    "required": ["business_type"]
                }
            }
        ]

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        if tool_name == "check_data_quality":
            nb = tool_input.get("neighborhood", "Unknown")
            # If they ask about Bronx 10453 or Brooklyn 11208, demonstrate the flaw
            if "10453" in nb or "11208" in nb:
                return "CRITICAL: 'foot_traffic' data for this neighborhood is Missing/Zero. Unreliable for retail/gym."
            return "Data quality appears consistent for demographic and transit metrics."
        elif tool_name == "identify_missing_considerations":
            return "Missing: Parking availability, Local business incentives, Zoning-specific signage restrictions."
        return "Tool not found"

    def review_recommendation(self, recommendation: Dict, scored_data: List[Dict], business_type: str) -> Dict[str, Any]:
        """Review the hypothesis and provide critical feedback"""
        
        system_prompt = """You are a skeptical business consultant. Your job is to find flaws.
        
        MANDATORY FORMAT:
        VERDICT: [APPROVED or REJECTED]
        ISSUES IDENTIFIED:
        - [Specific flaw 1...]
        SUGGESTIONS:
        - [Action 1...]
        MISSING CONSIDERATIONS:
        - [Consideration 1...]
        ALTERNATIVE PERSPECTIVE: [Concise summary...]
        
        CRITICAL RULE:
        - If 'foot_traffic' is missing or zero for the target area, you MUST set VERDICT: REJECTED.
        - If the Score seems disconnected from the underlying data, you MUST set VERDICT: REJECTED.
        """
        
        user_prompt = f"""Review this recommendation for a {business_type}:
        Recommendation: {json.dumps(recommendation, indent=2)}
        """
        
        messages = [{"role": "user", "content": user_prompt}]
        response = self.session.create_message(system=system_prompt, messages=messages, tools=self._get_tools())
        
        # Handle tool calling
        if response.stop_reason == "tool_use":
            tool_uses = [b for b in response.content if b.type == "tool_use"]
            messages.append({"role": "assistant", "content": response.content})
            results = []
            for t in tool_uses:
                res = self._execute_tool(t.name, t.input)
                results.append({"type": "tool_result", "tool_use_id": t.id, "tool_name": t.name, "content": res})
            messages.append({"role": "user", "content": results})
            # Final response after tools
            response = self.session.create_message(system=system_prompt, messages=messages)

        text = "".join([b.text for b in response.content if hasattr(b, "text")])
        return self._parse_critique(text), text

    def _parse_critique(self, response_text: str) -> Dict[str, Any]:
        critique = {
            "approved": False, # Default to False for safety
            "issues": [], 
            "suggestions": [], 
            "missing_considerations": [], 
            "alternative_perspective": ""
        }
        if not response_text: return critique

        lines = response_text.split('\n')
        current_section = None
        for line in lines:
            ls = line.strip().upper()
            if "VERDICT" in ls:
                critique["approved"] = "APPROVED" in ls
            elif "ISSUES" in ls: current_section = "issues"
            elif "SUGGEST" in ls: current_section = "suggestions"
            elif "MISSING" in ls or "CONSIDER" in ls: current_section = "missing"
            elif "ALTERNATIVE" in ls: current_section = "alternative"
            elif current_section:
                clean = line.lstrip("-•*0123456789. )").strip()
                if clean:
                    if current_section == "issues": critique["issues"].append(clean)
                    elif current_section == "suggestions": critique["suggestions"].append(clean)
                    elif current_section == "missing": critique["missing_considerations"].append(clean)
                    elif current_section == "alternative": critique["alternative_perspective"] += clean + " "
        
        # FINAL SAFETY CHECK
        all_text = response_text.lower()
        if "rejected" in all_text or "missing data" in all_text:
            critique["approved"] = False
            
        return critique

def critique_recommendation(recommendation, scored_data, plan):
    critic = CriticAgent()
    return critic.review_recommendation(recommendation, scored_data, plan['business_type'])