from typing import Dict, Any
import json
import os
from anthropic import Anthropic


class CriticAgent:
    """
    Challenges assumptions and triggers refinement if needed
    """
    
    def __init__(self, model_name: str = "claude-sonnet-4-20250514"):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = model_name
    
    def critique(
        self,
        recommendation: Dict[str, Any],
        eda_results: Dict[str, Any],
        business_type: str
    ) -> Dict[str, Any]:
        """
        Critically evaluate the recommendation
        """
        system_prompt = """You are a critical business analyst reviewing location recommendations.

Your job is to identify potential issues, overlooked factors, and suggest improvements.

Return valid JSON with this structure:
{
    "approved": true/false,
    "issues": [
        "issue 1 if any",
        "issue 2 if any"
    ],
    "suggestions": [
        "suggestion 1",
        "suggestion 2"
    ],
    "missing_considerations": [
        "factor 1 that wasn't considered",
        "factor 2 that wasn't considered"
    ],
    "confidence_assessment": "explanation of whether the confidence level is justified",
    "alternative_perspective": "a different way to interpret the same data"
}

Be constructive but critical. Look for:
- Data quality issues
- Overlooked neighborhoods
- Biased weighting
- Missing context
- Unrealistic expectations
- Trade-offs not properly explained
"""
        
        user_message = f"""Review this recommendation for a {business_type}:

RECOMMENDATION:
{json.dumps(recommendation, indent=2)}

ANALYSIS DATA:
{json.dumps(eda_results.get('summary', {}), indent=2)}

TOP 5 NEIGHBORHOODS ANALYZED:
{json.dumps(eda_results.get('top_neighborhoods', [])[:5], indent=2)}

Provide critical feedback. Should this recommendation be refined?
"""
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        
        response_text = message.content[0].text
        
        try:
            feedback = json.loads(response_text)
            return feedback
        except json.JSONDecodeError:
            content = response_text.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
    
    def format_feedback(self, feedback: Dict[str, Any]) -> str:
        """
        Format critic feedback for display
        """
        status = "✅ APPROVED" if feedback['approved'] else "⚠️ NEEDS REFINEMENT"
        
        output = f"\n{status}\n\n"
        
        if feedback['issues']:
            output += "🔍 ISSUES IDENTIFIED:\n"
            for i, issue in enumerate(feedback['issues'], 1):
                output += f"{i}. {issue}\n"
            output += "\n"
        
        if feedback['suggestions']:
            output += "💡 SUGGESTIONS:\n"
            for i, suggestion in enumerate(feedback['suggestions'], 1):
                output += f"{i}. {suggestion}\n"
            output += "\n"
        
        if feedback.get('missing_considerations'):
            output += "📌 MISSING CONSIDERATIONS:\n"
            for i, consideration in enumerate(feedback['missing_considerations'], 1):
                output += f"{i}. {consideration}\n"
            output += "\n"
        
        output += f"🎯 CONFIDENCE ASSESSMENT:\n{feedback['confidence_assessment']}\n\n"
        output += f"🔄 ALTERNATIVE PERSPECTIVE:\n{feedback['alternative_perspective']}\n"
        
        return output


def critique_recommendation(
    recommendation: Dict[str, Any],
    eda_results: Dict[str, Any],
    business_type: str
) -> tuple:
    """
    Standalone function to critique recommendation
    Returns (feedback_dict, formatted_feedback_text)
    """
    critic = CriticAgent()
    feedback = critic.critique(recommendation, eda_results, business_type)
    formatted = critic.format_feedback(feedback)
    
    return feedback, formatted