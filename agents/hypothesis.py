from typing import Dict, Any, List
import json
import os
from anthropic import Anthropic


class HypothesisAgent:
    """
    Produces final recommendation with evidence-based reasoning
    """
    
    def __init__(self, model_name: str = "claude-sonnet-4-20250514"):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = model_name
    
    def generate_recommendation(
        self,
        eda_results: Dict[str, Any],
        business_type: str
    ) -> Dict[str, Any]:
        """
        Generate final recommendation based on EDA results
        """
        top_neighborhoods = eda_results.get('top_neighborhoods', [])
        summary = eda_results.get('summary', {})
        
        system_prompt = """You are a business location advisor expert. 

Given analysis results, provide a final recommendation for the best location to open a business in NYC.

Your response must be valid JSON with this structure:
{
    "best_location": "neighborhood name",
    "borough": "borough name",
    "score": float,
    "reasoning": [
        "reason 1 with specific data",
        "reason 2 with specific data",
        "reason 3 with specific data"
    ],
    "trade_offs": [
        "trade-off 1",
        "trade-off 2"
    ],
    "top_alternatives": [
        {"name": "alternative 1", "score": float, "key_strength": "what makes it good"},
        {"name": "alternative 2", "score": float, "key_strength": "what makes it good"}
    ],
    "confidence": "high/medium/low",
    "key_insights": "2-3 sentence summary of the analysis"
}

Base your recommendation on concrete data. Reference specific metrics like competition count, median income, population density, etc.
"""
        
        user_message = f"""Recommend the best location for a {business_type} based on this analysis:

TOP NEIGHBORHOODS:
{json.dumps(top_neighborhoods[:5], indent=2)}

SUMMARY STATISTICS:
- Total neighborhoods analyzed: {summary.get('total_neighborhoods', 'N/A')}
- Average score: {summary.get('avg_score', 'N/A')}
- Average competition: {summary.get('metrics', {}).get('avg_competition', 'N/A')}
- Average median income: {summary.get('metrics', {}).get('avg_income', 'N/A')}
- Average rent: {summary.get('metrics', {}).get('avg_rent', 'N/A')}

Provide a clear recommendation with specific data points and honest trade-offs.
"""
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        
        response_text = message.content[0].text
        
        try:
            recommendation = json.loads(response_text)
            return recommendation
        except json.JSONDecodeError:
            content = response_text.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
    
    def explain_reasoning(self, recommendation: Dict[str, Any]) -> str:
        """
        Generate a human-readable explanation of the recommendation
        """
        explanation = f"""
🎯 RECOMMENDATION: {recommendation['best_location']}, {recommendation['borough']}
Score: {recommendation['score']:.3f}
Confidence: {recommendation['confidence'].upper()}

📊 WHY THIS LOCATION:
"""
        for i, reason in enumerate(recommendation['reasoning'], 1):
            explanation += f"{i}. {reason}\n"
        
        explanation += "\n⚖️ TRADE-OFFS TO CONSIDER:\n"
        for i, tradeoff in enumerate(recommendation['trade_offs'], 1):
            explanation += f"{i}. {tradeoff}\n"
        
        explanation += "\n🏆 TOP ALTERNATIVES:\n"
        for i, alt in enumerate(recommendation['top_alternatives'], 1):
            explanation += f"{i}. {alt['name']} (Score: {alt['score']:.3f}) - {alt['key_strength']}\n"
        
        explanation += f"\n💡 KEY INSIGHT:\n{recommendation['key_insights']}\n"
        
        return explanation


def generate_hypothesis(
    eda_results: Dict[str, Any],
    business_type: str
) -> tuple:
    """
    Standalone function to generate recommendation
    Returns (recommendation_dict, explanation_text)
    """
    agent = HypothesisAgent()
    recommendation = agent.generate_recommendation(eda_results, business_type)
    explanation = agent.explain_reasoning(recommendation)
    
    return recommendation, explanation