# API Usage Guide

## Overview

The NYC Business Location Advisor can be used both as a Streamlit web app and as a Python library.

## Installation

```bash
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file:

```
ANTHROPIC_API_KEY=your_key_here
CENSUS_API_KEY=your_key_here  # Optional
NYC_APP_TOKEN=your_token_here  # Optional
```

## Python API

### Basic Usage

```python
from agents.orchestrator import run_analysis

# Define your business requirements
user_input = {
    'business_type': 'coffee_shop',
    'borough_filter': ['Manhattan', 'Brooklyn'],
    'weight_demand': 0.25,
    'weight_foot_traffic': 0.20,
    'weight_income': 0.20,
    'weight_competition': 0.20,
    'weight_rent': 0.15
}

# Run the analysis
result = run_analysis(user_input)

# Access the recommendation
print(result['recommendation']['best_location'])
print(result['recommendation']['score'])
```

### Business Types

Available business types:
- `coffee_shop`
- `gym`
- `salon`
- `restaurant`
- `retail`

### Borough Filters

Available boroughs:
- `Manhattan`
- `Brooklyn`
- `Queens`
- `Bronx`
- `Staten Island`

Set to `None` or empty list to analyze all boroughs.

### Weights

All weights should sum to 1.0:

```python
{
    'weight_demand': 0.25,         # Population-based demand
    'weight_foot_traffic': 0.20,   # Subway ridership proxy
    'weight_income': 0.20,         # Median household income
    'weight_competition': 0.20,    # Existing businesses (inverse)
    'weight_rent': 0.15           # Cost indicator (inverse)
}
```

## Output Structure

The `run_analysis()` function returns a dictionary:

```python
{
    'recommendation': {
        'best_location': str,
        'borough': str,
        'score': float,
        'reasoning': List[str],
        'trade_offs': List[str],
        'top_alternatives': List[Dict],
        'confidence': str,
        'key_insights': str
    },
    'explanation': str,
    'critic_feedback': Dict,
    'artifacts': {
        'csv': str,           # Path to scores CSV
        'report': str,        # Path to text report
        'charts': List[str]   # Paths to chart HTML files
    },
    'iterations': int
}
```

## Using Individual Agents

### Planner Agent

```python
from agents.planner import create_analysis_plan

plan = create_analysis_plan(user_input)
print(plan['data_sources'])
print(plan['metrics_to_compute'])
```

### Data Collector Agent

```python
from agents.data_collector import collect_data

datasets = collect_data(plan)
print(datasets.keys())  # Available datasets
print(len(datasets['restaurants']))  # Number of records
```

### EDA Agent

```python
from agents.eda import perform_eda

weights = {
    'demand': 0.25,
    'foot_traffic': 0.20,
    'income': 0.20,
    'competition': 0.20,
    'rent': 0.15
}

results, charts, scored_data = perform_eda(datasets, weights, plan)
print(results['top_neighborhoods'])
```

### Hypothesis Agent

```python
from agents.hypothesis import generate_hypothesis

recommendation, explanation = generate_hypothesis(
    eda_results,
    business_type='coffee_shop'
)
print(explanation)
```

### Critic Agent

```python
from agents.critic import critique_recommendation

feedback, formatted = critique_recommendation(
    recommendation,
    eda_results,
    business_type='coffee_shop'
)
print(formatted)
```

## Using Data Tools

### Fetch NYC Data

```python
from tools.nyc_data import fetch_nyc_data

datasets = fetch_nyc_data('coffee_shop')
print(datasets['restaurants'].head())
```

### Fetch Census Data

```python
from tools.census_data import fetch_census_data

census = fetch_census_data()
print(census[['zipcode', 'median_income', 'population']].head())
```

### Fetch MTA Data

```python
from tools.mta_data import fetch_mta_data

mta = fetch_mta_data()
print(mta.head())
```

### Analysis Tools

```python
from tools.analysis import merge_datasets, compute_scores, summarize_results

# Merge datasets
merged = merge_datasets(datasets)

# Compute scores
scored = compute_scores(merged, weights)

# Summarize
summary = summarize_results(scored, top_n=10)
```

### Output Tools

```python
from tools.output import save_csv, save_report, generate_charts

# Save data
save_csv(scored_data, 'results.csv')

# Save report
save_report(explanation, 'report.txt')

# Generate and save charts
charts = generate_charts(scored_data)
```

## Error Handling

```python
try:
    result = run_analysis(user_input)
except Exception as e:
    print(f"Analysis failed: {e}")
    # Handle error
```

## Advanced Configuration

### Custom Scoring Function

```python
# Modify weights dynamically
weights = {
    'demand': 0.30,      # Prioritize demand
    'foot_traffic': 0.10,
    'income': 0.25,      # Prioritize affluent areas
    'competition': 0.25,  # Avoid competition
    'rent': 0.10
}

user_input['weight_demand'] = weights['demand']
user_input['weight_foot_traffic'] = weights['foot_traffic']
# ... etc
```

### Filter by Minimum Income

```python
from agents.eda import EDAAgent

eda_agent = EDAAgent()
eda_results, charts, scored = eda_agent.analyze(datasets, weights, plan)

# Filter results
high_income = scored[scored['median_income'] > 70000]
```

## Rate Limiting

If you encounter rate limits:

```python
import time

# Add delay between API calls
time.sleep(1)  # 1 second delay
```

## Caching Data

```python
import pickle

# Save datasets for reuse
with open('datasets.pkl', 'wb') as f:
    pickle.dump(datasets, f)

# Load cached data
with open('datasets.pkl', 'rb') as f:
    datasets = pickle.load(f)
```

## Production Best Practices

1. **Use environment variables** for API keys
2. **Implement retry logic** for API calls
3. **Cache data** when possible
4. **Handle missing data** gracefully
5. **Log errors** for debugging
6. **Validate inputs** before processing
7. **Set timeouts** for API requests

## Performance Optimization

```python
# Reduce data fetch limits for faster testing
from tools.nyc_data import NYCDataCollector

collector = NYCDataCollector()
data = collector.fetch_business_data('coffee_shop', limit=1000)  # Smaller limit
```

## Troubleshooting

### Issue: API key errors
**Solution**: Check `.env` file, ensure keys are valid

### Issue: Empty datasets
**Solution**: Check API endpoints, verify internet connection

### Issue: Slow performance
**Solution**: Reduce data limits, filter by borough earlier

### Issue: Memory errors
**Solution**: Use DuckDB for larger datasets, process in chunks

## Support

For additional help, see:
- `README.md` for full documentation
- `examples.py` for usage examples
- Tests in `tests/` for code examples
