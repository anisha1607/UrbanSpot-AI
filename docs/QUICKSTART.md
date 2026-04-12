# Quick Start Guide

Get up and running with the NYC Business Location Advisor in 5 minutes.

## 1. Prerequisites

- Python 3.9 or higher
- Git
- Anthropic API key ([Get one here](https://console.anthropic.com/))

## 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd business-location-advisor

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# Minimum required:
ANTHROPIC_API_KEY=sk-ant-...your-key-here
```

Optional API keys (improves data quality):
- Census API: https://api.census.gov/data/key_signup.html
- NYC Open Data: https://data.cityofnewyork.us/

## 4. Run the Application

```bash
streamlit run app/streamlit_app.py
```

Your browser will open to `http://localhost:8501`

## 5. Run Your First Analysis

### Via Web UI

1. Select **Business Type**: Coffee Shop
2. Choose **Boroughs**: Manhattan, Brooklyn
3. Click **Run Analysis**
4. Wait 1-2 minutes for results
5. Review recommendation and visualizations

### Via Python

```python
from agents.orchestrator import run_analysis

result = run_analysis({
    'business_type': 'coffee_shop',
    'borough_filter': ['Manhattan'],
    'weight_demand': 0.25,
    'weight_foot_traffic': 0.20,
    'weight_income': 0.20,
    'weight_competition': 0.20,
    'weight_rent': 0.15
})

print(result['recommendation']['best_location'])
```

## 6. Understanding Results

The system will output:

**Best Location**: The #1 recommended neighborhood

**Score**: 0.0-1.0, higher is better

**Reasoning**: Data-backed reasons for the recommendation

**Trade-offs**: Honest downsides to consider

**Alternatives**: Top 2-3 runner-up locations

**Visualizations**: Charts showing metrics by neighborhood

## 7. Customizing Analysis

### Adjust Weights

Different business priorities need different weights:

**For High-End Retail** (prioritize income):
```python
{
    'weight_demand': 0.20,
    'weight_foot_traffic': 0.15,
    'weight_income': 0.35,     # Higher
    'weight_competition': 0.20,
    'weight_rent': 0.10
}
```

**For Budget Fitness Center** (prioritize low rent):
```python
{
    'weight_demand': 0.30,
    'weight_foot_traffic': 0.20,
    'weight_income': 0.10,
    'weight_competition': 0.15,
    'weight_rent': 0.25       # Higher (inverse)
}
```

**For Tourist-Focused Business** (prioritize foot traffic):
```python
{
    'weight_demand': 0.20,
    'weight_foot_traffic': 0.35,  # Higher
    'weight_income': 0.20,
    'weight_competition': 0.15,
    'weight_rent': 0.10
}
```

### Filter by Borough

```python
# Only Manhattan
'borough_filter': ['Manhattan']

# Manhattan and Brooklyn only
'borough_filter': ['Manhattan', 'Brooklyn']

# All boroughs
'borough_filter': None
```

## 8. Viewing Artifacts

Generated files are saved to `data/outputs/`:

```bash
ls data/outputs/

# You'll see:
# - neighborhood_scores.csv
# - analysis_report.txt
# - chart_1_*.html
# - chart_2_*.html
# - chart_3_*.html
```

Open HTML charts in your browser to explore interactively.

## 9. Common Issues

**Issue**: "API key not found"
```bash
# Solution: Check .env file
cat .env | grep ANTHROPIC_API_KEY
```

**Issue**: "Module not found"
```bash
# Solution: Install requirements
pip install -r requirements.txt
```

**Issue**: "Port already in use"
```bash
# Solution: Use different port
streamlit run app/streamlit_app.py --server.port 8502
```

**Issue**: Slow performance
```bash
# Solution: Filter by specific borough
# Select only 1-2 boroughs in the UI
```

## 10. Next Steps

- 📖 Read the full [README.md](../README.md)
- 💻 Explore [API_USAGE.md](API_USAGE.md) for programmatic access
- 🧪 Run tests: `pytest tests/`
- 🎨 Customize the Streamlit UI in `app/streamlit_app.py`
- 🚀 Deploy to production (see Deployment section in README)

## Example Session

```bash
$ cd business-location-advisor
$ source venv/bin/activate
$ streamlit run app/streamlit_app.py

  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501

# In the UI:
# 1. Select "Coffee Shop"
# 2. Select "Brooklyn"
# 3. Adjust weight_foot_traffic to 0.30
# 4. Click "Run Analysis"
# 5. Wait ~90 seconds
# 6. View recommendation: "Williamsburg, Brooklyn"
# 7. Explore charts and download artifacts
```

## Tips for Best Results

1. **Start specific**: Choose 1-2 boroughs for faster results
2. **Adjust weights**: Tailor to your business model
3. **Check alternatives**: Top 3 are usually all viable
4. **Read trade-offs**: Understand what you're compromising
5. **Use critic feedback**: It often catches important issues

## Getting Help

- Check [Troubleshooting](API_USAGE.md#troubleshooting) section
- Review example code in `examples.py`
- Open a GitHub issue
- Read agent code in `agents/` for customization

---

**Happy analyzing! 🏙️**
