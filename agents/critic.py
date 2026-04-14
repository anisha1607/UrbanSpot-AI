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
        system_prompt = """You are a senior business critic. Your role is to play "devil's advocate" for a business owner. 

Your goal is to point out risks and trade-offs in plain English so the owner can make an informed decision.

Follow these communication rules:
1. NO JARGON: Avoid terms like "data measurement inconsistency", "statistical tie", or "structural reality".
2. BUSINESS IMPACT: Instead of technical metrics, explain what it means for the owner (e.g., "High rent in Manhattan means you need much higher daily sales to break even").
3. RESPECTFUL CHALLENGE: Be helpful. If two locations are close, explain it as "It's a tough choice between two great options" rather than critiquing the math.

Return valid JSON:
{
    "approved": true,
    "issues": [
        "Plain English risk (e.g., 'The area has a lot of competition already')",
        "Plain English risk"
    ],
    "suggestions": [
        "Actionable advice (e.g., 'Try to visit the area at lunch time to see the crowd')",
        "Actionable advice"
    ],
    "missing_considerations": [
        "Specific factor (e.g., 'Have you checked local parking options?')",
        "Specific factor"
    ],
    "confidence_assessment": "A simple explanation of why you are or aren't sure about the advice.",
    "alternative_perspective": "A simplified 'other way to look at it' (e.g., 'While Manhattan is busier, Brooklyn might be less stressful for a first-time owner.')"
}
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
            output += "🔍 POTENTIAL RISKS:\n"
            for i, issue in enumerate(feedback['issues'], 1):
                output += f"{i}. {issue}\n"
            output += "\n"
        
        if feedback['suggestions']:
            output += "💡 NEXT STEPS:\n"
            for i, suggestion in enumerate(feedback['suggestions'], 1):
                output += f"{i}. {suggestion}\n"
            output += "\n"
        
        if feedback.get('missing_considerations'):
            output += "📌 OTHER FACTORS TO CHECK:\n"
            for i, consideration in enumerate(feedback['missing_considerations'], 1):
                output += f"{i}. {consideration}\n"
            output += "\n"
        
        output += f"🎯 HOW SURE ARE WE?:\n{feedback['confidence_assessment']}\n\n"
        output += f"🔄 ANOTHER OPTION TO CONSIDER:\n{feedback['alternative_perspective']}\n"
        
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