"""
Example script showing how to use the NYC Business Location Advisor
"""

import sys
sys.path.append('/home/claude/business-location-advisor')

from agents.orchestrator import run_analysis
from pprint import pprint


def example_coffee_shop():
    """Example: Finding location for a coffee shop in Brooklyn"""
    
    print("=" * 60)
    print("EXAMPLE 1: Coffee Shop in Brooklyn")
    print("=" * 60)
    
    user_input = {
        'business_type': 'coffee_shop',
        'borough_filter': ['Brooklyn'],
        'weight_demand': 0.30,
        'weight_foot_traffic': 0.25,
        'weight_income': 0.20,
        'weight_competition': 0.15,
        'weight_rent': 0.10
    }
    
    result = run_analysis(user_input)
    
    print("\n" + result['explanation'])
    print("\n" + result['critic_formatted'])
    
    print("\nArtifacts Generated:")
    for key, value in result['artifacts'].items():
        print(f"  - {key}: {value}")
    
    return result


def example_gym_manhattan():
    """Example: Finding location for a gym in Manhattan"""
    
    print("\n\n" + "=" * 60)
    print("EXAMPLE 2: Gym in Manhattan")
    print("=" * 60)
    
    user_input = {
        'business_type': 'gym',
        'borough_filter': ['Manhattan'],
        'weight_demand': 0.25,
        'weight_foot_traffic': 0.20,
        'weight_income': 0.30,  # Higher weight on income for gyms
        'weight_competition': 0.15,
        'weight_rent': 0.10
    }
    
    result = run_analysis(user_input)
    
    print("\n" + result['explanation'])
    
    return result


def example_restaurant_all_boroughs():
    """Example: Finding location for a restaurant (all boroughs)"""
    
    print("\n\n" + "=" * 60)
    print("EXAMPLE 3: Restaurant - All NYC Boroughs")
    print("=" * 60)
    
    user_input = {
        'business_type': 'restaurant',
        'borough_filter': None,  # All boroughs
        'weight_demand': 0.25,
        'weight_foot_traffic': 0.30,  # Higher weight on foot traffic
        'weight_income': 0.20,
        'weight_competition': 0.15,
        'weight_rent': 0.10
    }
    
    result = run_analysis(user_input)
    
    print("\n" + result['explanation'])
    
    return result


if __name__ == "__main__":
    # Run examples
    # Note: These will make real API calls and may take several minutes
    
    try:
        result1 = example_coffee_shop()
        
        # Uncomment to run additional examples
        # result2 = example_gym_manhattan()
        # result3 = example_restaurant_all_boroughs()
        
    except Exception as e:
        print(f"\nError running example: {e}")
        print("\nMake sure you have:")
        print("1. Set up your .env file with API keys")
        print("2. Installed all requirements: pip install -r requirements.txt")
        print("3. Have a stable internet connection for API calls")
