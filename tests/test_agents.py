import sys
sys.path.append('/home/claude/business-location-advisor')

import pytest
import pandas as pd
from schemas.models import UserInput, BusinessType, Borough
from tools.analysis import DataAnalyzer


def test_user_input_validation():
    """Test Pydantic validation for user input"""
    valid_input = UserInput(
        business_type=BusinessType.COFFEE_SHOP,
        borough_filter=[Borough.MANHATTAN],
        weight_demand=0.3,
        weight_foot_traffic=0.2,
        weight_income=0.2,
        weight_competition=0.2,
        weight_rent=0.1
    )
    
    assert valid_input.business_type == BusinessType.COFFEE_SHOP
    assert Borough.MANHATTAN in valid_input.borough_filter


def test_invalid_weights():
    """Test that invalid weights are rejected"""
    with pytest.raises(Exception):
        UserInput(
            business_type=BusinessType.GYM,
            weight_demand=1.5
        )


def test_data_analyzer_normalization():
    """Test data normalization"""
    analyzer = DataAnalyzer()
    
    test_series = pd.Series([10, 20, 30, 40, 50])
    normalized = analyzer._normalize(test_series)
    
    assert normalized.min() == 0.0
    assert normalized.max() == 1.0
    assert len(normalized) == len(test_series)


def test_data_analyzer_merge():
    """Test dataset merging"""
    analyzer = DataAnalyzer()
    
    df1 = pd.DataFrame({
        'neighborhood': ['Area A', 'Area B'],
        'population': [1000, 2000]
    })
    
    df2 = pd.DataFrame({
        'neighborhood': ['Area A', 'Area B'],
        'competition_count': [5, 10]
    })
    
    datasets = {'demo': df1, 'competition': df2}
    
    result = analyzer.merge_datasets(datasets)
    assert not result.empty


def test_scoring_computation():
    """Test score computation"""
    analyzer = DataAnalyzer()
    
    df = pd.DataFrame({
        'neighborhood': ['Area A', 'Area B', 'Area C'],
        'population': [1000, 2000, 1500],
        'median_income': [50000, 75000, 60000],
        'competition_count': [5, 15, 10],
        'median_rent': [2000, 3000, 2500]
    })
    
    weights = {
        'demand': 0.25,
        'foot_traffic': 0.20,
        'income': 0.20,
        'competition': 0.20,
        'rent': 0.15
    }
    
    result = analyzer.compute_scores(df, weights)
    
    assert 'final_score' in result.columns
    assert len(result) == 3
    assert result['final_score'].max() <= 1.0


def test_summarize_results():
    """Test result summarization"""
    analyzer = DataAnalyzer()
    
    df = pd.DataFrame({
        'neighborhood': ['Area A', 'Area B'],
        'final_score': [0.8, 0.6],
        'competition_count': [5, 10],
        'median_income': [60000, 50000],
        'median_rent': [2500, 2000]
    })
    
    summary = analyzer.summarize_results(df, top_n=2)
    
    assert 'total_neighborhoods' in summary
    assert summary['total_neighborhoods'] == 2
    assert 'top_neighborhoods' in summary
    assert len(summary['top_neighborhoods']) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
