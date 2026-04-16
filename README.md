# NYC Business Location Advisor

A multi-agent AI system that recommends optimal locations in NYC to open a business using real-world data and intelligent analysis.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red.svg)

### 🌐 Live Application
**URL:** [https://urbanspot-ai-263893814921.us-central1.run.app/](https://urbanspot-ai-263893814921.us-central1.run.app/)

## 🎯 Project Overview

This system implements a complete data analysis lifecycle:
1. **Collect** real-world data at runtime via APIs.
2. **Explore** data through agent-driven statistical tool calls.
3. **Hypothesize** with data-backed recommendations using iterative tool loops for deep research.
4. **Critique** and refine through an autonomous Generator-Critic loop.

The result is an intelligent recommendation for where to open your business in NYC based on competition, demographics, foot traffic, and economic indicators.

---

## 📋 Rubric Implementation Mapping

This project fulfills all **Core Requirements** and **4 Elective Concepts** from the Grab-Bag.

### Core Requirements
| Requirement | Implementation Detail | Location (File + Class/Function) |
|-------------|-----------------------|----------------------------------|
| **Frontend** | Interactive Streamlit Dashboard | `app/streamlit_app.py` |
| **Agent Framework** | Google GenAI SDK (Vertex AI / Studio) | `agents/gemini_client.py` (`GeminiChatSession`) |
| **Tool Calling** | Model-invoked tool use with feedback loop | `agents/agent_sdk.py` (`LocationAnalysisAgent.generate_recommendation`) |
| **Non-trivial Dataset** | Multi-API retrieval (NYC Open Data, Census, MTA) | `tools/` (`nyc_data.py`, `census_data.py`, `mta_data.py`) |
| **Multi-Agent Pattern** | Orchestrator-Handoff + Generator-Critic | `agents/orchestrator.py` (`BusinessLocationOrchestrator`) |
| **Deployed** | [Live Instance (Google Cloud Run)](https://urbanspot-ai-263893814921.us-central1.run.app/) | `render.yaml` |
| **README.md** | Comprehensive project documentation | `README.md` |

### Advanced Techniques
| Concept | Description | Location (File) |
|---------|-------------|----------------------------------|
| **Iterative Refinement** | Critic Agent triggers re-analysis if quality is low | `agents/orchestrator.py` |
| **Artifacts** | Persistent PDF reports, PNG charts, and CSV data | `tools/pdf_generator.py`, `tools/output.py` |
| **Data Visualization** | Dynamic Plotly & Matplotlib visualizations | `tools/output.py` |
| **Structured Output** | JSON-mode extraction and strict parsing | `agents/planner.py` |

---

## 🏗️ System Architecture: Multi-Agent Pattern

The system uses a **Synchronous Orchestrator** with **Generator-Critic feedback**:
1. **Planner Agent** (`agents/planner.py`): Parses user intent into a structured JSON plan.
2. **Data Collector** (`agents/data_collector.py`): Executes the API pipeline.
3. **Market Analyst** (`agents/eda.py`): Uses **Agent-as-tool-call** to perform statistical EDA.
4. **Hypothesis Agent** (`agents/agent_sdk.py`): The "Generator" that conducts deep research.
5. **Critic Agent** (`agents/critic.py`): The "Critic" that evaluates the hypothesis and can trigger a refinement loop if the reasoning is weak or inconsistent.

---

## 🚀 Advanced Agentic Capabilities

- **⚡ Recursive Research Engine**: Unlike standard one-shot LLM responses, our **Location Analysis Agent** conducts multi-turn research. It executes recursive tool calls to "drill down" into specific neighborhood metrics to verify local demand before committing to a hypothesis.
- **🛡️ Autonomous Generator-Critic Loop**: To ensure high-rigor recommendations, a dedicated **Critic Agent** evaluates the Generator's output against the raw EDA data. It can trigger an autonomous re-analysis loop if it identifies weak reasoning or inconsistent evidence.
- **📩 On-Demand Strategic Dossiers**: Users can trigger the generation of a professional PDF report. This artifact synthesizes all agent insights, tool-retrieved evidence, and statistical visualizations into a single, inbox-delivered document.
- **🗣️ Human-Centric Strategy Translation**: The system translates "low-level" statistical data (like z-scores and ridership proxies) into plain-English business strategies, making technical analytics actionable for any entrepreneur.

---

## 🔧 Technology Stack

- **Frontend**: Streamlit
- **LLM:** Gemini 2.0 Flash (via Google GenAI SDK)
- **Visuals:** Plotly, Matplotlib
- **Reporting:** FPDF (PDF Generation)
- **Core Framework**: Google GenAI SDK (Gemini 2.0 Flash)

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anisha1607/UrbanSpot-AI.git
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment:**
   Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
   Add your `GOOGLE_API_KEY` (AI Studio or Vertex AI).

4. **Run the Application:**
   ```bash
   streamlit run app/streamlit_app.py
   ```

## 🧪 Testing

The system includes a test suite for score validation and agent logic:
```bash
python -m pytest tests/
```
