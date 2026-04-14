# NYC Business Location Advisor

A multi-agent AI system that recommends optimal locations in NYC to open a business using real-world data and intelligent analysis.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Claude](https://img.shields.io/badge/Claude-3.5-orange.svg)
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

The system uses a **Custom Orchestration Framework** (in `agents/orchestrator.py`) to manage five specialized agents:

- **Planner Agent** (`agents/planner.py`): Interprets user input and defines the analysis plan using **explicit Tool Calling**.
- **Data Collector Agent** (`agents/data_collector.py`): Fetches real-world data from NYC Open Data, Census, and MTA APIs.
- **EDA Agent** (`agents/eda.py`): Performs statistical aggregation, computations, and generates visualizations.
- **Hypothesis Agent** (`agents/hypothesis.py`): Produces the final recommendation with evidence-based reasoning.
- **Critic Agent** (`agents/critic.py`): Challenges assumptions and triggers iterative refinements.

### Workflow Pattern

**Generator-Critic & Orchestrator Pattern:**
- The Orchestrator manages the flow from planning to output.
- The Hypothesis Agent (Generator) and Critic Agent form a feedback loop for iterative refinement.

## 📊 Data Sources (Runtime Retrieval)

All data is fetched dynamically via APIs - **no hardcoded datasets**:

1. **NYC Open Data API:** Business licenses, restaurant density.
2. **U.S. Census API:** Population density, median household income.
3. **MTA API:** Subway ridership used as a foot traffic proxy.

## 🔧 Technology Stack

```yaml
Frontend: Streamlit
Agent Logic: Custom Multi-Agent Orchestration
LLM: Claude 3.5 Sonnet (Anthropic)
Tool Calling: Anthropic Tool Use API
Data Processing: pandas, matplotlib
Visualization: Plotly, Matplotlib
```

## 📋 Rubric Implementation Mapping

| Requirement | Implementation Detail | Location |
|-------------|-----------------------|----------|
| **Collect (Step 1)** | Dynamic API retrieval from 3 sources | `agents/data_collector.py` |
| **EDA (Step 2)** | Statistical scoring & multi-dataset aggregation | `agents/eda.py`, `tools/analysis.py` |
| **Hypothesize (Step 3)** | Data-backed recommendations with reasoning | `agents/hypothesis.py` |
| **Frontend** | Interactive Streamlit Dashboard | `app/streamlit_app.py` |
| **Agent Framework** | Custom Orchestration Framework | `agents/orchestrator.py` |
| **Tool Calling** | Explicit model-side tool use (`set_analysis_plan`) | `agents/planner.py` |
| **Multi-Agent Pattern** | Orchestrator + Generator/Critic loop | `agents/orchestrator.py` |
| **Iterative Refinement** | Refinement loop based on Critic feedback | `agents/orchestrator.py` |
| **Artifacts** | PDF reports, PNG charts, CSV exports | `tools/pdf_generator.py`, `tools/output.py` |
| **Data Visualization** | Plotly & Matplotlib dashboard & report charts | `app/streamlit_app.py`, `tools/pdf_generator.py` |
| **Structured Output** | JSON-mode and Pydantic-style responses | `agents/*.py` |

## 🚀 Installation & Setup

1. **Clone & Install:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure:** Copy `.env.example` to `.env` and add your `ANTHROPIC_API_KEY`.
3. **Run:**
   ```bash
   streamlit run app/streamlit_app.py
   ```

## 🧪 Testing

```bash
python -m pytest tests/
```
