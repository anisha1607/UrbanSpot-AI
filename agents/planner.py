from typing import Dict, Any
import json
import os
from anthropic import Anthropic


class PlannerAgent:
    """
    Interprets user input and creates a structured analysis plan
    """
    
    def __init__(self, model_name: str = "claude-sonnet-4-20250514"):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
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
        "borough": ["borough1", "borough2"] or null,
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
        
        user_message = f"""Create an analysis plan for:
Business Type: {user_input.get('business_type', 'general business')}
Borough Filter: {user_input.get('borough_filter', 'None - all boroughs')}
User Priorities: 
- Demand weight: {user_input.get('weight_demand', 0.25)}
- Foot traffic weight: {user_input.get('weight_foot_traffic', 0.20)}
- Income weight: {user_input.get('weight_income', 0.20)}
- Competition weight: {user_input.get('weight_competition', 0.20)}
- Rent weight: {user_input.get('weight_rent', 0.15)}
"""
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        
        response_text = message.content[0].text
        
        try:
            plan = json.loads(response_text)
            return plan
        except json.JSONDecodeError:
            content = response_text.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())


def create_analysis_plan(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standalone function to create analysis plan
    """
    planner = PlannerAgent()
    return planner.create_plan(user_input)