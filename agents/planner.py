from typing import Dict, Any
import json
import os
from agents.gemini_client import GeminiChatSession, DEFAULT_MODEL


class PlannerAgent:
    """
    Interprets user input and creates a structured analysis plan
    """
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.session = GeminiChatSession(model=model_name)
        self.model = model_name
    
    def create_plan(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create analysis plan from user input
        """
        system_prompt = """You are a data analysis planner for a business location advisor system.

Given user input about a business type and preferences, create a structured JSON plan that includes:
1. Business type
2. Data sources to collect
3. Metrics to compute
4. Filters to apply

Return ONLY valid JSON with this structure:
{
    "business_type": "string",
    "data_sources": ["source1", "source2", "source3"],
    "metrics_to_compute": ["metric1", "metric2", "metric3"],
    "filters": {
        "borough": ["borough1", "borough2"] or "ALL",
        "min_population": number or null
    },
    "analysis_focus": "string describing what to prioritize"
}

Data sources available:
- nyc_businesses: NYC business licenses
- restaurants: Restaurant inspection data
- census: Population, income, rent data by zip code
- mta: Subway ridership for foot traffic proxy
- demographics: Neighborhood demographics

Key metrics to consider:
- competition_count: Number of existing businesses
- median_income: Average income level
- population_density: Population per area
- foot_traffic_score: Subway ridership proxy
- rent_proxy: Cost of doing business
- demand_score: Population-based demand estimate
"""
        
        # ========== BOROUGH FILTERING FIX ==========
        # Extract borough filter from user input
        borough_filter = user_input.get('borough_filter')
        
        # Create geography string for the prompt
        if borough_filter and len(borough_filter) > 0:
            borough_str = f"Specific boroughs: {', '.join(borough_filter)}"
            borough_instruction = f'Set filters.borough to {json.dumps(borough_filter)}'
        else:
            borough_str = "ALL boroughs (search city-wide)"
            borough_instruction = 'Set filters.borough to "ALL"'
        # ============================================
        
        user_message = f"""Create an analysis plan for:

Business Type: {user_input.get('business_type', 'general business')}
Geography: {borough_str}

User Priorities: 
- Demand weight: {user_input.get('weight_demand', 0.25)}
- Foot traffic weight: {user_input.get('weight_foot_traffic', 0.20)}
- Income weight: {user_input.get('weight_income', 0.20)}
- Competition weight: {user_input.get('weight_competition', 0.20)}
- Rent weight: {user_input.get('weight_rent', 0.15)}

IMPORTANT: {borough_instruction}
"""
        
        messages = [{"role": "user", "content": user_message}]
        
        response = self.session.create_message(
            system=system_prompt,
            messages=messages,
            max_tokens=1000,
        )
        
        # Extract text from response
        response_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                response_text += block.text
        
        # Robust JSON extraction
        import re
        def extract_first_json(text):
            # 1. Strip markdown code blocks if they exist
            # Matches ```json { ... } ``` or simply ``` { ... } ```
            md_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if md_match:
                text = md_match.group(1)
            
            # 2. Try to find the first complete { ... } block
            # Balanced bracket approach
            start = text.find('{')
            if start == -1:
                return None
            
            bracket_count = 0
            for i in range(start, len(text)):
                if text[i] == '{':
                    bracket_count += 1
                elif text[i] == '}':
                    bracket_count -= 1
                    if bracket_count == 0:
                        return text[start:i+1]
            return None

        try:
            content = extract_first_json(response_text)
            if not content:
                # Fallback to pure regex if bracket count failed
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                content = json_match.group(0) if json_match else response_text.strip()
                
            plan = json.loads(content)
            
            # Ensure borough filter is correct
            if 'filters' not in plan:
                plan['filters'] = {}
            
            if borough_filter and len(borough_filter) > 0:
                plan['filters']['borough'] = borough_filter
            else:
                plan['filters']['borough'] = "ALL"
            
            print(f"📋 Planner: Created plan with borough filter: {plan['filters'].get('borough')}")
            return plan
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ Planner: JSON parse error ({str(e)}), attempting manual recovery...")
            # Fallback to a very simple plan if all parsing fails
            fallback_plan = {
                "business_type": user_input.get('business_type', 'business'),
                "data_sources": ["nyc_businesses", "census", "mta"],
                "metrics_to_compute": ["competition_count", "median_income", "population_density"],
                "filters": {
                    "borough": borough_filter if (borough_filter and len(borough_filter) > 0) else "ALL",
                    "min_population": 1000
                },
                "analysis_focus": "Balanced analysis based on user priorities"
            }
            return fallback_plan


def create_analysis_plan(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standalone function to create analysis plan
    """
    planner = PlannerAgent()
    return planner.create_plan(user_input)