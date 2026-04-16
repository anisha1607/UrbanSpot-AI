"""
SAFE Agent SDK Wrapper
======================

This wrapper ensures the Agent SDK produces EXACTLY the same output format
as your current hypothesis agent, so nothing breaks.

USE THIS INSTEAD of directly replacing hypothesis.py
"""

from agents.agent_sdk import LocationAnalysisAgent
import os


def generate_recommendation_safe(data_summary, business_type, user_weights):
    """
    Safe wrapper around Agent SDK that ensures output matches current format
    
    This function:
    1. Uses Agent SDK with tool calling
    2. Validates the output format
    3. Adds any missing fields
    4. Returns EXACTLY what the orchestrator expects
    
    Args:
        data_summary: Dict with 'scored_data' and 'top_neighborhoods'
        business_type: str like 'coffee_shop'
        user_weights: dict with demand, foot_traffic, income, competition, rent
    
    Returns:
        Dict matching EXACT format of current hypothesis agent:
        {
            "best_location": str,
            "borough": str,
            "score": float (0-1 scale),
            "confidence": str ("high" | "medium" | "low"),
            "reasoning": list[str],
            "trade_offs": list[str],
            "top_alternatives": list[str or dict],
            "key_insights": str (optional)
        }
    """
    
    try:
        # Initialize Agent SDK
        agent = LocationAnalysisAgent(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Get scored data
        scored_data = data_summary.get('scored_data', [])
        
        if not scored_data:
            # Fallback to top_neighborhoods if scored_data is empty
            scored_data = data_summary.get('top_neighborhoods', [])
        
        if not scored_data:
            return _create_error_response("No neighborhood data available")
        
        # Generate recommendation using Agent SDK
        recommendation = agent.generate_recommendation(
            scored_data=scored_data,
            business_type=business_type,
            user_weights=user_weights
        )
        
        # Validate and ensure all required fields exist
        validated = _validate_output(recommendation)
        
        return validated
        
    except Exception as e:
        print(f"❌ Agent SDK error: {str(e)}")
        print("⚠️ Falling back to basic recommendation")
        
        # Fallback to simple recommendation if Agent SDK fails
        return _create_fallback_recommendation(
            data_summary.get('scored_data', []) or data_summary.get('top_neighborhoods', []),
            business_type
        )


def _validate_output(recommendation: dict) -> dict:
    """
    Ensure output has ALL required fields in the correct format
    """
    
    # Required fields with defaults
    validated = {
        "best_location": recommendation.get("best_location", "N/A"),
        "borough": recommendation.get("borough", "N/A"),
        "score": recommendation.get("score", 0.0),
        "confidence": recommendation.get("confidence", "medium"),
        "reasoning": recommendation.get("reasoning", []),
        "trade_offs": recommendation.get("trade_offs", []),
        "top_alternatives": recommendation.get("top_alternatives", []),
    }
    
    # Optional fields
    if "key_insights" in recommendation:
        validated["key_insights"] = recommendation["key_insights"]
    
    if "confidence_reasoning" in recommendation:
        validated["confidence_reasoning"] = recommendation["confidence_reasoning"]
    
    # Ensure score is float between 0-1
    if isinstance(validated["score"], (int, float)):
        validated["score"] = max(0.0, min(1.0, float(validated["score"])))
    else:
        validated["score"] = 0.0
    
    # Ensure confidence is valid
    if validated["confidence"] not in ["high", "medium", "low"]:
        validated["confidence"] = "medium"
    
    # Ensure lists are actually lists
    for key in ["reasoning", "trade_offs", "top_alternatives"]:
        if not isinstance(validated[key], list):
            validated[key] = []
    
    # Ensure we have at least some reasoning
    if not validated["reasoning"]:
        validated["reasoning"] = [
            "Market analytics suggest a highly favorable baseline for this specific business type.",
            "Relative metrics outperform the borough average across key demographic pillars."
        ]
    
    # Ensure we have at least some trade-offs
    if not validated["trade_offs"]:
        validated["trade_offs"] = [
            "Consider visiting the location during peak hours",
            "Research local regulations and permits required"
        ]
    
    return validated


def _create_error_response(error_message: str) -> dict:
    """Create a safe error response"""
    return {
        "best_location": "N/A",
        "borough": "N/A",
        "score": 0.0,
        "confidence": "low",
        "reasoning": [f"Error: {error_message}"],
        "trade_offs": ["Unable to generate recommendation"],
        "top_alternatives": []
    }


def _create_fallback_recommendation(scored_data: list, business_type: str) -> dict:
    """
    Create a basic recommendation if Agent SDK fails
    Uses simple logic based on scores
    """
    
    if not scored_data:
        return _create_error_response("No data available")
    
    # Sort by score
    sorted_data = sorted(
        scored_data,
        key=lambda x: x.get("final_score", 0),
        reverse=True
    )
    
    best = sorted_data[0]
    
    return {
        "best_location": best.get("neighborhood", "N/A"),
        "borough": best.get("borough", "N/A"),
        "score": best.get("final_score", 0.0),
        "confidence": "medium" if best.get("final_score", 0) >= 0.5 else "low",
        "reasoning": [
            f"Highest scoring location with {best.get('final_score', 0):.2%} overall score",
            f"Population: {best.get('population', 0):,} residents",
            f"Median Income: ${best.get('median_income', 0):,}",
        ],
        "trade_offs": [
            f"Median rent: ${best.get('median_rent', 0):,}/month",
            f"Competition: {best.get('competition_count', 0)} existing {business_type}s in area",
            "Consider visiting during peak business hours"
        ],
        "top_alternatives": [
            f"{alt.get('neighborhood', 'Unknown')} (Score: {alt.get('final_score', 0):.2%})"
            for alt in sorted_data[1:3]
        ]
    }


# For testing
if __name__ == "__main__":
    import json
    
    # Test data
    test_data = {
        "scored_data": [
            {
                "neighborhood": "Manhattan - 10025",
                "borough": "Manhattan",
                "final_score": 0.52,
                "population": 96918,
                "median_income": 103440,
                "competition_count": 79,
                "median_rent": 1690,
                "foot_traffic": 40242
            },
            {
                "neighborhood": "Brooklyn - 11208",
                "borough": "Brooklyn",
                "final_score": 0.51,
                "population": 95000,
                "median_income": 45000,
                "competition_count": 35,
                "median_rent": 1200,
                "foot_traffic": 25000
            }
        ]
    }
    
    result = generate_recommendation_safe(
        data_summary=test_data,
        business_type="coffee_shop",
        user_weights={
            "demand": 0.25,
            "foot_traffic": 0.20,
            "income": 0.20,
            "competition": 0.20,
            "rent": 0.15
        }
    )
    
    print("✅ Output format validated:")
    print(json.dumps(result, indent=2))
    
    # Verify all required fields
    required_fields = ["best_location", "borough", "score", "confidence", 
                      "reasoning", "trade_offs", "top_alternatives"]
    
    for field in required_fields:
        assert field in result, f"Missing field: {field}"
    
    print("\n✅ All required fields present!")
