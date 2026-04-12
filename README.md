# NYC Business Location Advisor

A multi-agent AI system that recommends optimal locations in NYC to open a business using real-world data and intelligent analysis.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.0.20-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red.svg)

## 🎯 Project Overview

This system implements a complete data analysis lifecycle:
1. **Collect** real-world data at runtime via APIs
2. **Explore** data through comprehensive EDA
3. **Hypothesize** with data-backed recommendations
4. **Critique** and refine through an iterative loop

The result is an intelligent recommendation for where to open your business in NYC based on competition, demographics, foot traffic, and economic indicators.

## 🏗️ System Architecture

### Multi-Agent Design

The system uses **LangGraph** to orchestrate five specialized agents:

```
┌─────────────┐
│   Planner   │  → Interprets user input, defines analysis plan
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Data        │  → Fetches data from NYC Open Data, Census, MTA
│ Collector   │  → Normalizes and merges datasets
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  EDA Agent  │  → Performs aggregation and analysis
│             │  → Computes metrics per neighborhood
│             │  → Generates visualizations
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Hypothesis  │  → Produces final recommendation
│   Agent     │  → Explains reasoning with evidence
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Critic    │  → Challenges assumptions
│   Agent     │  → Triggers refinement if needed
└─────────────┘
```

### Workflow Pattern

**Generator-Critic Refinement Loop:**
- Hypothesis agent generates recommendation
- Critic agent evaluates quality
- If issues found and iterations < 2, refine
- Otherwise, output final results

## 📊 Data Sources (Runtime Retrieval)

All data is fetched dynamically via APIs - **no hardcoded datasets**:

### 1. NYC Open Data
- **Business Licenses**: Active businesses by location
- **Restaurant Inspections**: Restaurant density and distribution
- **Demographics**: Neighborhood-level population indicators

### 2. U.S. Census API
- **Population Density**: Total population by zip code
- **Median Income**: Economic indicators
- **Median Rent**: Cost of doing business

### 3. MTA Data
- **Subway Ridership**: Foot traffic proxy
- **Transit Activity**: Turnstile entry/exit data

## 🔧 Technology Stack

```yaml
Frontend: Streamlit
Agent Framework: LangGraph
LLM: Claude (Anthropic)
Data Processing: pandas, DuckDB
Visualization: Plotly
Deployment: Streamlit Cloud / Render
```

## 📂 Project Structure

```
business-location-advisor/
│
├── app/
│   └── streamlit_app.py          # Streamlit UI
│
├── agents/
│   ├── planner.py                # Planner agent
│   ├── data_collector.py         # Data collection agent
│   ├── eda.py                    # EDA agent
│   ├── hypothesis.py             # Recommendation agent
│   ├── critic.py                 # Critic agent
│   └── orchestrator.py           # LangGraph workflow
│
├── tools/
│   ├── nyc_data.py               # NYC Open Data API
│   ├── census_data.py            # Census API
│   ├── mta_data.py               # MTA API
│   ├── analysis.py               # EDA and scoring
│   └── output.py                 # Chart and artifact generation
│
├── schemas/
│   └── models.py                 # Pydantic data models
│
├── data/
│   └── outputs/                  # Generated artifacts
│
├── tests/
│   └── test_agents.py            # Unit tests
│
├── requirements.txt              # Dependencies
├── .env.example                  # Environment variables template
└── README.md                     # This file
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.9+
- Anthropic API key
- Census API key (optional but recommended)
- NYC Open Data App Token (optional but recommended)

### Step 1: Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd business-location-advisor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your API keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CENSUS_API_KEY=your_census_api_key_here  # Get from https://api.census.gov/data/key_signup.html
NYC_APP_TOKEN=your_nyc_token_here        # Get from https://data.cityofnewyork.us/
```

### Step 3: Run the Application

```bash
# Run Streamlit app
streamlit run app/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## 💡 Usage

### Via Streamlit UI

1. Select your **business type** (Coffee Shop, Gym, Salon, etc.)
2. Choose **borough filters** (optional)
3. Adjust **scoring weights** based on priorities:
   - Demand (population-based)
   - Foot Traffic (subway ridership)
   - Income Level
   - Competition (inverse)
   - Rent (inverse)
4. Click **Run Analysis**
5. Review:
   - Best location recommendation
   - Top alternatives
   - Data visualizations
   - Critic feedback
   - Generated artifacts

### Via Python API

```python
from agents.orchestrator import run_analysis

user_input = {
    'business_type': 'coffee_shop',
    'borough_filter': ['Manhattan', 'Brooklyn'],
    'weight_demand': 0.25,
    'weight_foot_traffic': 0.20,
    'weight_income': 0.20,
    'weight_competition': 0.20,
    'weight_rent': 0.15
}

result = run_analysis(user_input)

print(f"Best location: {result['recommendation']['best_location']}")
print(f"Score: {result['recommendation']['score']}")
```

## 📈 Scoring Function

The system uses a weighted scoring model:

```
Score = w1 × Demand 
      + w2 × Foot_Traffic 
      + w3 × Income 
      - w4 × Competition 
      - w5 × Rent
```

Where each metric is normalized (0-1) and weights are user-adjustable.

### Default Weights

```python
{
    'demand': 0.25,         # Population-based demand
    'foot_traffic': 0.20,   # Subway ridership proxy
    'income': 0.20,         # Median household income
    'competition': 0.20,    # Number of competitors (inverse)
    'rent': 0.15           # Cost indicator (inverse)
}
```

## 🎨 Features

✅ **Runtime API Data Retrieval** - Fresh data every run  
✅ **Python-Based EDA** - pandas, DuckDB for analysis  
✅ **Multi-Agent Architecture** - LangGraph orchestration  
✅ **Data Visualization** - Interactive Plotly charts  
✅ **Artifact Generation** - CSV, charts, text reports  
✅ **Iterative Refinement** - Generator-Critic loop  
✅ **Structured JSON Outputs** - Pydantic validation  

## 🌐 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Set environment variables in Streamlit settings
5. Deploy

### Render

```yaml
# render.yaml
services:
  - type: web
    name: business-location-advisor
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app/streamlit_app.py --server.port $PORT
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: CENSUS_API_KEY
        sync: false
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=agents --cov=tools tests/
```

## 📋 Example Output

```
🎯 RECOMMENDATION: Astoria, Queens
Score: 0.847
Confidence: HIGH

📊 WHY THIS LOCATION:
1. Lower competition (15 businesses) vs Williamsburg (45 businesses)
2. High population density (42,000 per sq mi) indicates strong demand
3. Median income ($68,000) above city average
4. Strong subway traffic (3 major lines, 2M+ annual riders)
5. Moderate rent ($2,400/month) keeps overhead manageable

⚖️ TRADE-OFFS TO CONSIDER:
1. Income level 8% below Manhattan neighborhoods
2. Slightly less foot traffic than prime Manhattan locations

🏆 TOP ALTERNATIVES:
1. Long Island City (Score: 0.821) - Rapid development, high growth potential
2. Park Slope (Score: 0.809) - Affluent demographic, strong community
```

## 🗺️ Rubric Mapping

This project addresses all key evaluation criteria:

| Criteria | Implementation |
|----------|----------------|
| **Runtime Data** | All APIs called dynamically, no hardcoded data |
| **EDA** | Comprehensive pandas/DuckDB analysis with aggregations |
| **Multi-Agent** | 5 specialized agents orchestrated via LangGraph |
| **Visualization** | Plotly charts: bar, scatter, histogram, line plots |
| **Artifacts** | CSV exports, text reports, HTML charts |
| **Refinement** | Generator-Critic loop with 2-iteration limit |
| **JSON Outputs** | Pydantic-validated structured responses |
| **Deployment** | Streamlit Cloud ready with env config |

## 🐛 Troubleshooting

### API Rate Limits

If you hit rate limits:
- Add delays between requests
- Reduce data fetch limits in `tools/*.py`
- Get API tokens for higher rate limits

### Missing Data

Some datasets may be empty if:
- API endpoints change
- Authentication issues
- Network problems

The system gracefully handles missing data and continues with available sources.

### Memory Issues

For large datasets:
- Reduce `limit` parameters in data fetch functions
- Use DuckDB for out-of-core processing
- Filter by borough earlier in pipeline

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- NYC Open Data for public datasets
- U.S. Census Bureau for demographic data
- MTA for transit data
- Anthropic for Claude API
- LangChain team for LangGraph framework

## 📞 Support

For issues or questions:
- Open a GitHub issue
- Check existing documentation
- Review example outputs

---

**Built with ❤️ using Claude, LangGraph, and NYC Open Data**
