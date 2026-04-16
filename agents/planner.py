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
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "set_analysis_plan",
                "description": "Set the structured analysis plan for the business location study",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "business_type": {"type": "string", "description": "Type of business being analyzed"},
                        "data_sources": {
                            "type": "array", 
                            "items": {"type": "string"},
                            "description": "List of data sources to fetch (nyc_businesses, census, mta, etc.)"
                        },
                        "metrics_to_compute": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key metrics to compute during EDA"
                        },
                        "filters": {
                            "type": "object",
                            "properties": {
                                "borough": {"type": "any", "description": "List of boroughs or 'ALL'"},
                                "min_population": {"type": "number"}
                            }
                        },
                        "analysis_focus": {"type": "string", "description": "Primary goal/focus of the analysis"}
                    },
                    "required": ["business_type", "data_sources", "metrics_to_compute", "filters"]
                }
            }
        ]

    def create_plan(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create analysis plan from user input via Tool Calling
        """
        system_prompt = """You are a data analysis planner for a business location advisor system.
        
Definitively set the analysis plan by calling the 'set_analysis_plan' tool.
Do not provide a textual response, only the tool call."""
        
        # ========== BOROUGH FILTERING FIX ==========
        borough_filter = user_input.get('borough_filter')
        if borough_filter and len(borough_filter) > 0:
            borough_str = f"Specific boroughs: {', '.join(borough_filter)}"
            borough_instruction = f"Filters.borough MUST be set to {json.dumps(borough_filter)}"
        else:
            borough_str = "ALL boroughs"
            borough_instruction = 'Filters.borough MUST be set to "ALL"'
        # ============================================

        user_message = f"""Draft a plan for:
- Business: {user_input.get('business_type', 'business')}
- Geography: {borough_str}
- Priorities: {json.dumps(user_input)}

IMPORTANT: {borough_instruction}"""

        messages = [{"role": "user", "content": user_message}]
        
        response = self.session.create_message(
            system=system_prompt,
            messages=messages,
            tools=self._get_tools(),
            max_tokens=1000,
        )
        
        # Process Tool Call
        for block in response.content:
            if hasattr(block, "type") and block.type == "tool_use":
                if block.name == "set_analysis_plan":
                    plan = block.input
                    print(f"📋 Planner Agent invoked tool [set_analysis_plan] with focus: {plan.get('analysis_focus')}")
                    # Ensure borough filter is consistent with input
                    if borough_filter and len(borough_filter) > 0:
                        plan['filters']['borough'] = borough_filter
                    else:
                        plan['filters']['borough'] = "ALL"
                    return plan

        # Fallback if no tool call was made
        return {
            "business_type": user_input.get('business_type', 'business'),
            "data_sources": ["nyc_businesses", "census", "mta"],
            "metrics_to_compute": ["competition_count", "median_income"],
            "filters": {"borough": borough_filter or "ALL"},
            "analysis_focus": "Standard business location analysis"
        }


def create_analysis_plan(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standalone function to create analysis plan
    """
    planner = PlannerAgent()
    return planner.create_plan(user_input)