from typing import Dict, Any, List
import json
import os
from agents.gemini_client import GeminiChatSession, DEFAULT_MODEL


class HypothesisAgent:
    """
    Produces final recommendation with evidence-based reasoning
    """
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.session = GeminiChatSession(model=model_name)
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
        
        system_prompt = """You are a senior business location advisor. Your goal is to provide clear, actionable advice to a business owner who is NOT a data scientist.

Follow these communication rules:
1. USE ACCESSIBLE LANGUAGE: Avoid or explain technical jargon. Use plain English.
2. USE ANALOGIES: For close rankings, use terms like "photo finish", "neck-and-neck", or "a statistical tie".
3. BE CONCISE: Get straight to the point.
4. FOCUS ON THE 'WHY': Explain how the data translates to business success (e.g., "More foot traffic means more potential walk-in customers").

Your response must be valid JSON with this structure:
{
    "best_location": "Zip / Neighborhood name (e.g. 'Brooklyn - 11208')",
    "borough": "Borough name",
    "score": float,
    "reasoning": [
        "Plain English reason with a specific data point",
        "Plain English reason with a specific data point",
        "Plain English reason with a specific data point"
    ],
    "trade_offs": [
        "Simple trade-off statement",
        "Simple trade-off statement"
    ],
    "top_alternatives": [
        {"name": "alternative 1", "score": float, "key_strength": "Plain English benefit"},
        {"name": "alternative 2", "score": float, "key_strength": "Plain English benefit"}
    ],
    "confidence": "high/medium/low",
    "confidence_reasoning": "A simple sentence explaining your confidence (e.g., 'The data is very strong in this area.')",
    "key_insights": "2-3 sentence executive summary avoiding jargon."
}
"""
        
        user_message = f"""Advise the business owner on the best location for a {business_type} based on this analysis:

TOP NEIGHBORHOODS:
{json.dumps(top_neighborhoods[:5], indent=2)}

SENSITIVITY FINDINGS (TESTING IF THE RANKING HOLDS):
{json.dumps(summary.get('sensitivity_analysis', {}), indent=2)}

Note: If the top locations are within 2 points of each other, explain that it's a "photo finish" where any of the top choices are excellent options. If the sensitivity analysis shows the lead is "fragile", explain that while Manhattan leads on paper, Brooklyn is a very strong and stable runner-up.
"""
        if "coffee" in business_type.lower():
            user_message += """
IMPORTANT FOR COFFEE SHOPS: 
You MUST recommend the location that has the absolute highest overall `score` mathematically. The scores already perfectly encapsulate the weighted preferences for income, demand, and foot traffic. Do not override the mathematical ranking! Do not recommend a location simply because it has higher income if its overall score is lower than the top rank. ALWAYS recommend the #1 top-scoring option.
"""
        
        messages = [{"role": "user", "content": user_message}]
        
        response = self.session.create_message(
            system=system_prompt,
            messages=messages,
            max_tokens=2000,
        )
        
        # Extract text from response
        response_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                response_text += block.text
        
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

📊 WHY THIS LOCATION:
"""
        for i, reason in enumerate(recommendation['reasoning'], 1):
            explanation += f"{i}. {reason}\n"
        
        explanation += "\n⚖️ TRADE-OFFS TO CONSIDER:\n"
        for i, tradeoff in enumerate(recommendation['trade_offs'], 1):
            explanation += f"{i}. {tradeoff}\n"
        
        explanation += "\n🏆 TOP ALTERNATIVES:\n"
        for i, alt in enumerate(recommendation['top_alternatives'], 1):
            explanation += f"{i}. {alt['name']} (Score: {float(alt['score']):.1f}) - {alt['key_strength']}\n"
        
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