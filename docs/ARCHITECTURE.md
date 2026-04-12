# System Architecture

## Overview

The NYC Business Location Advisor uses a **multi-agent architecture** orchestrated by LangGraph to analyze NYC data and produce intelligent location recommendations.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  - User input collection                                     │
│  - Parameter configuration                                   │
│  - Results visualization                                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              LangGraph Orchestrator                          │
│  - Manages agent workflow                                    │
│  - Handles state transitions                                 │
│  - Implements refinement loop                                │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Planner    │ │     Data     │ │     EDA      │
│    Agent     │ │  Collector   │ │    Agent     │
│              │ │    Agent     │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Hypothesis  │ │    Critic    │ │    Output    │
│    Agent     │ │    Agent     │ │  Generation  │
│              │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Component Details

### 1. Frontend Layer (Streamlit)

**Purpose**: User interface for configuration and results

**Components**:
- Input widgets (dropdowns, sliders, multiselect)
- Results dashboard (metrics, charts, tables)
- Artifact download links
- Interactive visualizations

**Tech**: Streamlit, Plotly

### 2. Orchestration Layer (LangGraph)

**Purpose**: Coordinate multi-agent workflow

**Workflow**:
```
Start → Planner → DataCollector → EDA → Hypothesis → Critic
                                                        │
                                                        ├─→ Refine (if needed)
                                                        └─→ Output → End
```

**State Management**:
- Maintains conversation state
- Passes data between agents
- Tracks iteration count
- Stores intermediate results

**Tech**: LangGraph, TypedDict

### 3. Agent Layer

#### Planner Agent

**Input**: User preferences (business type, filters, weights)

**Process**:
1. Analyze user requirements
2. Identify relevant data sources
3. Define metrics to compute
4. Create structured analysis plan

**Output**: JSON plan with data sources and metrics

**Tech**: Claude (LLM), Pydantic validation

#### Data Collector Agent

**Input**: Analysis plan

**Process**:
1. Call NYC Open Data API
2. Call Census Bureau API
3. Call MTA API
4. Normalize column names
5. Clean and validate data

**Output**: Dictionary of pandas DataFrames

**Tech**: requests, pandas

#### EDA Agent

**Input**: Raw datasets, scoring weights, plan

**Process**:
1. Merge datasets by neighborhood/zip
2. Group and aggregate by location
3. Compute normalized metrics
4. Calculate weighted scores
5. Generate visualizations

**Output**: Analysis results, charts, scored data

**Tech**: pandas, DuckDB, Plotly

#### Hypothesis Agent

**Input**: EDA results

**Process**:
1. Rank neighborhoods by score
2. Identify best location
3. Generate evidence-based reasoning
4. Identify trade-offs
5. Suggest alternatives

**Output**: Recommendation with explanation

**Tech**: Claude (LLM), structured JSON output

#### Critic Agent

**Input**: Recommendation, EDA results

**Process**:
1. Review recommendation quality
2. Identify potential issues
3. Check for biases
4. Evaluate confidence level
5. Suggest improvements

**Output**: Approval/refinement feedback

**Tech**: Claude (LLM), critical analysis

**Refinement Loop**:
```
Hypothesis → Critic ──┐
      ▲               │
      │               │ not approved && iterations < 2
      └───────────────┘
```

### 4. Data Layer

#### NYC Open Data
- **Endpoint**: `https://data.cityofnewyork.us/resource/`
- **Datasets**: Business licenses, restaurant inspections
- **Rate Limit**: 1000 requests/day (without token)

#### Census Bureau
- **Endpoint**: `https://api.census.gov/data/`
- **Dataset**: ACS 5-year estimates
- **Metrics**: Population, income, rent by zip code

#### MTA
- **Endpoint**: `http://web.mta.info/developers/`
- **Dataset**: Turnstile entry/exit counts
- **Proxy**: Foot traffic estimation

### 5. Analysis Layer

#### Data Pipeline

```
Raw Data → Normalization → Merge → Aggregation → Scoring → Ranking
```

**Normalization**:
- Min-max scaling to [0,1]
- Handles missing values
- Outlier detection

**Scoring Formula**:
```
Score = w1·Demand + w2·FootTraffic + w3·Income 
      - w4·Competition - w5·Rent

where each metric is normalized and weights sum to 1
```

**Aggregation Levels**:
- Neighborhood (primary)
- Zip code (when neighborhood unavailable)
- Borough (for filtering)

### 6. Output Layer

**Artifacts Generated**:

1. **CSV File**: Complete scored dataset
2. **Text Report**: Formatted recommendation
3. **HTML Charts**: 
   - Bar chart (top 10 scores)
   - Line chart (metric comparison)
   - Histogram (score distribution)
   - Scatter plot (income vs competition)

## Data Flow

```
User Input
    ↓
Planner (creates plan)
    ↓
Data Collector (fetches data)
    ↓
    ├─→ NYC Open Data API
    ├─→ Census API
    └─→ MTA API
    ↓
Raw Datasets
    ↓
EDA Agent (analysis)
    ↓
    ├─→ Merge datasets
    ├─→ Compute metrics
    ├─→ Calculate scores
    └─→ Generate charts
    ↓
Scored Neighborhoods
    ↓
Hypothesis Agent (recommendation)
    ↓
Draft Recommendation
    ↓
Critic Agent (review)
    ↓
    ├─→ Approved → Output
    └─→ Not Approved → Refine (max 2 iterations)
    ↓
Final Recommendation + Artifacts
```

## State Schema

```python
WorkflowState = {
    'user_input': Dict[str, Any],
    'plan': Dict[str, Any],
    'datasets': Dict[str, pd.DataFrame],
    'eda_results': Dict[str, Any],
    'charts': List[Figure],
    'scored_data': pd.DataFrame,
    'recommendation': Dict[str, Any],
    'explanation': str,
    'critic_feedback': Dict[str, Any],
    'iteration': int,
    'final_output': Dict[str, Any]
}
```

## Scalability Considerations

### Current Design
- **Data Volume**: ~50K records per API call
- **Processing**: In-memory pandas
- **Concurrency**: Sequential agent execution

### Scaling Strategies

**For Larger Datasets**:
- Use DuckDB for out-of-core processing
- Implement data streaming
- Add caching layer (Redis)

**For Faster Performance**:
- Parallel data collection
- Pre-computed aggregations
- CDN for static assets

**For High Traffic**:
- Queue-based processing (Celery)
- Result caching
- Load balancing

## Technology Stack Summary

| Layer | Technologies |
|-------|-------------|
| Frontend | Streamlit, Plotly |
| Orchestration | LangGraph |
| Agents | Claude (Anthropic), Pydantic |
| Data Processing | pandas, DuckDB |
| APIs | requests, REST |
| Visualization | Plotly, matplotlib |
| Deployment | Streamlit Cloud, Render |

## Security Considerations

- API keys stored in environment variables
- No user data persisted
- Rate limiting on API calls
- Input validation via Pydantic
- No SQL injection risk (using APIs)

## Monitoring & Logging

**Current Implementation**:
- Console logging for agent execution
- Error tracking with try/catch
- Iteration counting

**Production Recommendations**:
- Add structured logging (loguru)
- Implement error alerting
- Track API usage metrics
- Monitor response times
