from agents.critic import CriticAgent
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_critic():
    print("\n" + "="*50)
    print("🚀 STARTING CRITIC DEBUG TEST")
    print("="*50)
    
    # Mock data
    recommendation = {
        "neighborhood": "Manhattan - 10025",
        "boro": "Manhattan",
        "score": 0.85,
        "confidence": "high",
        "reasoning": ["High income area", "Good foot traffic"],
        "trade_offs": ["High competition"],
        "top_alternatives": ["Brooklyn - 11201"]
    }
    
    data_summary = {
        "scored_data": [
            {
                "neighborhood": "Manhattan - 10025",
                "population": 50000,
                "median_income": 95000,
                "competition_count": 12,
                "final_score": 0.85
            }
        ]
    }
    
    agent = CriticAgent()
    result = agent.review_recommendation(recommendation, data_summary, "coffee_shop")
    
    print("\n" + "="*50)
    print("📝 CRITIC RESULT:")
    print("="*50)
    print(json.dumps(result, indent=2))
    print("="*50)
    
    # Check for defaults
    defaults_found = any("peak business hours" in str(s).lower() for s in result.get("suggestions", []))
    if defaults_found:
        print("❌ FAILURE: Critic is still using default suggestions.")
        return False
    
    if not result.get("suggestions"):
        print("❌ FAILURE: No suggestions provided.")
        return False
        
    print("✅ SUCCESS: Critic provided real suggestions!")
    return True

if __name__ == "__main__":
    test_critic()
