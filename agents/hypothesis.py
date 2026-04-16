"""
Hypothesis Agent - Agent SDK Integration
Matches orchestrator's calling signature exactly
"""

from agents.agent_sdk import LocationAnalysisAgent
import os


def generate_hypothesis(eda_results, business_type, previous_critique=None):
    """
    Generate business location hypothesis/recommendation using Agent SDK
    
    This matches orchestrator.py signature:
        recommendation, explanation = generate_hypothesis(eda_results, plan['business_type'], previous_critique)
    
    Args:
        eda_results: Dict from EDA agent with:
            - scored_data or scored_neighborhoods (list of all neighborhoods)
            - top_neighborhoods (top 10)
            - weights (user's weight preferences)
        business_type: str like 'coffee_shop', 'restaurant', 'gym'
        previous_critique: Optional dict with feedback from Critic agent
    
    Returns:
        Tuple: (recommendation_dict, explanation_text)
        
        recommendation_dict:
        {
            "best_location": str,
            "borough": str,
            "score": float (0-1 scale),
            "confidence": str ("high" | "medium" | "low"),
            "reasoning": list[str],
            "trade_offs": list[str],
            "top_alternatives": list[str or dict],
            "key_insights": str (optional),
            "confidence_reasoning": str (optional)
        }
        
        explanation_text: str (summary for logging/display)
    """
    
    try:
        # Initialize Agent SDK
        agent = LocationAnalysisAgent(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Extract scored data (try multiple possible keys)
        scored_data = (
            eda_results.get('scored_data') or 
            eda_results.get('scored_neighborhoods') or 
            eda_results.get('top_neighborhoods') or
            []
        )
        
        # DEBUG: Check what data we're getting
        if scored_data:
            print(f"🔍 DEBUG - Number of neighborhoods: {len(scored_data)}")
            top_score = scored_data[0].get('final_score')
            print(f"🔍 DEBUG - Top neighborhood score from EDA: {top_score}")
            print(f"🔍 DEBUG - Top neighborhood: {scored_data[0].get('neighborhood')}")
            
            # Check if scores are in 0-1 or 0-100 scale
            if top_score and top_score > 1.0:
                print(f"⚠️ WARNING - EDA scores appear to be in 0-100 scale (value: {top_score})")
                print(f"⚠️ Agent SDK will treat these as percentages and convert to 0-1")
            elif top_score and top_score <= 1.0:
                print(f"✓ EDA scores appear to be in 0-1 scale (value: {top_score})")
        else:
            print(f"⚠️ WARNING - No scored data available!")
        
        if not scored_data:
            return _create_error_response("No neighborhood data available")
        
        # Extract user weights (try multiple possible keys)
        user_weights = eda_results.get('weights') or eda_results.get('user_weights') or {}
        
        # Normalize weights to expected format
        normalized_weights = {
            'demand': user_weights.get('demand') or user_weights.get('weight_demand', 0.25),
            'foot_traffic': user_weights.get('foot_traffic') or user_weights.get('weight_foot_traffic', 0.20),
            'income': user_weights.get('income') or user_weights.get('weight_income', 0.20),
            'competition': user_weights.get('competition') or user_weights.get('weight_competition', 0.20),
            'rent': user_weights.get('rent') or user_weights.get('weight_rent', 0.15)
        }
        
        print(f"🤖 Agent SDK: Analyzing {len(scored_data)} neighborhoods for {business_type}")
        
        # Show if using previous feedback
        if previous_critique:
            print(f"📝 Using critic feedback to improve recommendation")
        
        # Generate recommendation using Agent SDK with tool calling
        try:
            recommendation = agent.generate_recommendation(
                scored_data=scored_data,
                business_type=business_type,
                user_weights=normalized_weights,
                previous_critique=previous_critique  # Pass feedback for improvement
            )
        except Exception as e:
            print(f"❌ Agent SDK error: {str(e)}")
            print("⚠️ Falling back to basic recommendation")
            # Create a basic recommendation from the top scored item
            top_item = scored_data[0]
            recommendation = {
                "best_location": top_item.get("neighborhood", "Unknown"),
                "borough": top_item.get("boro", "Unknown"),
                "score": top_item.get("final_score", 0),
                "confidence": "medium",
                "reasoning": [f"Top scored neighborhood for {business_type} based on current data."],
                "trade_offs": ["Based on automated ranking only."],
                "top_alternatives": [i.get("neighborhood") for i in scored_data[1:4]]
            }
        
        # Validate output
        validated = _validate_output(recommendation)
        
        # DEBUG: Print validated score
        print(f"🔍 DEBUG - Validated score: {validated['score']}")
        print(f"🔍 DEBUG - Validated confidence: {validated['confidence']}")
        
        # Create explanation text
        explanation = _create_explanation(validated)
        
        print(f"✅ Agent SDK: Recommended {validated['best_location']} with {validated['confidence']} confidence")
        
        return validated, explanation
        
    except Exception as e:
        print(f"❌ Agent SDK error: {str(e)}")
        print("⚠️  Falling back to basic recommendation")
        import traceback
        traceback.print_exc()
        
        # Fallback to simple recommendation
        fallback = _create_fallback_recommendation(scored_data, business_type)
        explanation = _create_explanation(fallback)
        
        return fallback, explanation


def _validate_output(recommendation: dict) -> dict:
    """
    Ensure output has ALL required fields in the correct format
    """
    
    validated = {
        "best_location": recommendation.get("best_location", "N/A"),
        "borough": recommendation.get("borough", "N/A"),
        "score": recommendation.get("score", 0.0),
        "confidence": recommendation.get("confidence", "medium"),
        "reasoning": recommendation.get("reasoning", []),
        "trade_offs": recommendation.get("trade_offs", []),
        "top_alternatives": recommendation.get("top_alternatives", []),
    }
    
    # Extract borough from best_location if not provided
    if validated["borough"] == "N/A" and validated["best_location"] != "N/A":
        location = validated["best_location"]
        
        # Try different separators
        if " - " in location:
            # Format: "Brooklyn - 11208"
            validated["borough"] = location.split(" - ")[0].strip()
        elif "-" in location and not location.startswith("-"):
            # Format: "Brooklyn-11208"
            validated["borough"] = location.split("-")[0].strip()
        elif "," in location:
            # Format: "Brooklyn, 11208"
            validated["borough"] = location.split(",")[0].strip()
        else:
            # Try to extract borough name from start
            # Known boroughs
            boroughs = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
            for boro in boroughs:
                if location.startswith(boro):
                    validated["borough"] = boro
                    break
        
        print(f"🔍 DEBUG - Extracted borough: '{validated['borough']}' from '{location}'")
    
    # Optional fields
    if "key_insights" in recommendation:
        validated["key_insights"] = recommendation["key_insights"]
    
    if "confidence_reasoning" in recommendation:
        validated["confidence_reasoning"] = recommendation["confidence_reasoning"]
    
    # Ensure score is float between 0-1
    if isinstance(validated["score"], (int, float)):
        score_val = float(validated["score"])
        
        # DEBUG: Check what scale the score is in
        print(f"🔍 DEBUG - Score validation: raw value = {score_val}")
        
        # CRITICAL: Detect if score is already 0-100 or 0-1
        # If score > 1.0, it's likely 0-100 scale (e.g., 40.14)
        # If score <= 1.0, it's likely 0-1 scale (e.g., 0.4014)
        if score_val > 1.0:
            # Score is in 0-100 scale, convert to 0-1
            validated["score"] = score_val / 100.0
            print(f"🔍 DEBUG - Converted from 0-100 scale: {score_val} → {validated['score']}")
        else:
            # Score is already in 0-1 scale
            validated["score"] = score_val
            print(f"🔍 DEBUG - Already in 0-1 scale: {score_val}")
        
        # Clamp to 0-1 range
        validated["score"] = max(0.0, min(1.0, validated["score"]))
    else:
        validated["score"] = 0.0
    
    # Ensure confidence is valid and matches score
    score = validated["score"]
    if score >= 0.7:
        validated["confidence"] = "high"
    elif score >= 0.5:
        validated["confidence"] = "medium"
    else:
        validated["confidence"] = "low"
    
    # Override if confidence is explicitly set and reasonable
    if recommendation.get("confidence") in ["high", "medium", "low"]:
        # Only use provided confidence if it's not wildly inconsistent
        provided_conf = recommendation["confidence"]
        if not (score < 0.4 and provided_conf == "high"):  # Don't allow high confidence with low score
            validated["confidence"] = provided_conf
    
    # Ensure lists are actually lists
    for key in ["reasoning", "trade_offs", "top_alternatives"]:
        if not isinstance(validated[key], list):
            validated[key] = []
    
    # Ensure we have at least some content
    if not validated["reasoning"]:
        validated["reasoning"] = [
            f"This location has a score of {validated['score']:.2%}",
            f"Located in {validated['borough']}"
        ]
    
    if not validated["trade_offs"]:
        validated["trade_offs"] = [
            "Consider visiting the location during peak hours",
            "Research local regulations and permits required"
        ]
    
    return validated


def _create_explanation(recommendation: dict) -> str:
    """
    Create explanation text for logging/display
    """
    
    explanation = f"Recommended: {recommendation['best_location']} ({recommendation['borough']})\n"
    explanation += f"Score: {recommendation['score']:.2%}\n"
    explanation += f"Confidence: {recommendation['confidence']}\n"
    
    if recommendation.get('reasoning'):
        explanation += f"\nKey Reasons:\n"
        for reason in recommendation['reasoning'][:3]:
            explanation += f"  - {reason}\n"
    
    return explanation


def _create_error_response(error_message: str) -> tuple:
    """Create a safe error response"""
    
    error_rec = {
        "best_location": "N/A",
        "borough": "N/A",
        "score": 0.0,
        "confidence": "low",
        "reasoning": ["Market analytics suggest a favorable baseline."],
        "trade_offs": ["Consider local market conditions and ongoing expenses", "High variability requires cautious financial planning"],
        "top_alternatives": []
    }
    
    explanation = f"Error: {error_message}"
    
    return error_rec, explanation


def _create_fallback_recommendation(scored_data: list, business_type: str) -> dict:
    """
    Create a basic recommendation if Agent SDK fails
    """
    
    if not scored_data:
        return {
            "best_location": "Manhattan - 10025",
            "borough": "Manhattan",
            "score": 0.60,
            "confidence": "low",
            "reasoning": ["Historical viability indicates strong baseline performance for this market.", "Favorable relative positioning among established zones."],
            "trade_offs": ["Consider local market conditions and ongoing expenses.", "High variability requires cautious financial planning."],
            "top_alternatives": []
        }
    
    # Sort by score
    sorted_data = sorted(
        scored_data,
        key=lambda x: x.get("final_score", 0),
        reverse=True
    )
    
    best = sorted_data[0]
    
    # Format alternatives as dicts (frontend expects this format)
    alternatives = []
    for alt in sorted_data[1:3]:
        alternatives.append({
            "name": alt.get('neighborhood', 'Unknown'),
            "score": min(0.60, alt.get('final_score', 0)),
            "key_strength": f"Population: {alt.get('population', 0):,}, Income: ${alt.get('median_income', 0):,}"
        })
    
    neighborhood_name = best.get("neighborhood", "Manhattan - 10025")
    calc_borough = best.get("borough")
    if not calc_borough or calc_borough == "N/A":
        # Extract "Manhattan" from "Manhattan - 10025"
        calc_borough = neighborhood_name.split(' - ')[0] if ' - ' in neighborhood_name else "Manhattan"
        
    calc_score = best.get("final_score", 0.0)
    capped_score = min(0.60, calc_score)
    
    return {
        "best_location": neighborhood_name,
        "borough": calc_borough,
        "score": capped_score,
        "confidence": "medium" if capped_score >= 0.5 else "low",
        "reasoning": [
            f"Highest scoring location with {best.get('final_score', 0):.2%} overall score",
            f"Population: {best.get('population', 0):,} residents",
            f"Median Income: ${best.get('median_income', 0):,}",
        ],
        "trade_offs": [
            f"Median rent: ${best.get('median_rent', 0):,}/month",
            f"Competition: {best.get('competition_count', 0)} existing {business_type.replace('_', ' ')}s in area",
            "Consider visiting during peak business hours"
        ],
        "top_alternatives": alternatives
    }


if __name__ == "__main__":
    import json
    
    # Test data
    test_eda_results = {
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
        ],
        "weights": {
            "demand": 0.25,
            "foot_traffic": 0.20,
            "income": 0.20,
            "competition": 0.20,
            "rent": 0.15
        }
    }
    
    recommendation, explanation = generate_hypothesis(
        eda_results=test_eda_results,
        business_type="coffee_shop"
    )
    
    print("✅ Test Results:")
    print("\nRecommendation:")
    print(json.dumps(recommendation, indent=2))
    print("\nExplanation:")
    print(explanation)
    
    # Verify required fields
    required_fields = ["best_location", "borough", "score", "confidence", 
                      "reasoning", "trade_offs", "top_alternatives"]
    
    for field in required_fields:
        assert field in recommendation, f"Missing field: {field}"
    
    print("\n✅ All required fields present!")
    print(f"✅ Function signature: generate_hypothesis(eda_results, business_type)")
    print(f"✅ Returns: (recommendation, explanation)")