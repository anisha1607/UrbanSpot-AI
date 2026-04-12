import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from agents.orchestrator import run_analysis
import plotly.graph_objects as go
from datetime import datetime


st.set_page_config(
    page_title="NYC Business Location Advisor",
    page_icon="🏙️",
    layout="wide"
)

st.title("🏙️ NYC Business Location Advisor")
st.markdown("### AI-Powered Multi-Agent System for Optimal Business Placement")

st.sidebar.header("Business Configuration")

business_type = st.sidebar.selectbox(
    "Business Type",
    ["Coffee Shop", "Gym", "Salon", "Restaurant", "Retail Store"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Borough Filter")

boroughs = st.sidebar.multiselect(
    "Select boroughs to analyze (leave empty for all)",
    ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Scoring Weights")
st.sidebar.markdown("*Adjust importance of each factor*")

weight_demand = st.sidebar.slider("Demand", 0.0, 1.0, 0.25, 0.05)
weight_foot_traffic = st.sidebar.slider("Foot Traffic", 0.0, 1.0, 0.20, 0.05)
weight_income = st.sidebar.slider("Income Level", 0.0, 1.0, 0.20, 0.05)
weight_competition = st.sidebar.slider("Competition (inverse)", 0.0, 1.0, 0.20, 0.05)
weight_rent = st.sidebar.slider("Rent (inverse)", 0.0, 1.0, 0.15, 0.05)

total_weight = weight_demand + weight_foot_traffic + weight_income + weight_competition + weight_rent
st.sidebar.info(f"Total weight: {total_weight:.2f}")

if total_weight != 1.0:
    st.sidebar.warning("⚠️ Weights should sum to 1.0 for optimal results")

if st.sidebar.button("🚀 Run Analysis", type="primary", use_container_width=True):
    user_input = {
        'business_type': business_type.lower().replace(' ', '_'),
        'borough_filter': boroughs if boroughs else None,
        'weight_demand': weight_demand,
        'weight_foot_traffic': weight_foot_traffic,
        'weight_income': weight_income,
        'weight_competition': weight_competition,
        'weight_rent': weight_rent
    }
    
    with st.spinner('🔄 Running multi-agent analysis...'):
        try:
            result = run_analysis(user_input)
            
            st.session_state['result'] = result
            st.session_state['analysis_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            st.success("✅ Analysis complete!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

if 'result' in st.session_state:
    result = st.session_state['result']
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### 🎯 Best Location: {result['recommendation']['best_location']}")
        st.markdown(f"**Borough:** {result['recommendation']['borough']}")
    
    with col2:
        st.metric("Score", f"{result['recommendation']['score']:.3f}")
    
    with col3:
        confidence = result['recommendation']['confidence']
        color = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(confidence, "⚪")
        st.metric("Confidence", f"{color} {confidence.upper()}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Recommendation", "📈 Visualizations", "🔍 Critic Feedback", "📁 Artifacts"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Why This Location")
            for i, reason in enumerate(result['recommendation']['reasoning'], 1):
                st.markdown(f"{i}. {reason}")
        
        with col2:
            st.subheader("Trade-offs")
            for i, tradeoff in enumerate(result['recommendation']['trade_offs'], 1):
                st.markdown(f"{i}. {tradeoff}")
        
        st.markdown("---")
        
        st.subheader("Top Alternatives")
        for i, alt in enumerate(result['recommendation']['top_alternatives'], 1):
            with st.expander(f"{i}. {alt['name']} - Score: {alt['score']:.3f}"):
                st.markdown(f"**Key Strength:** {alt['key_strength']}")
        
        st.markdown("---")
        st.info(f"**Key Insight:** {result['recommendation']['key_insights']}")
    
    with tab2:
        st.subheader("Analysis Visualizations")
        
        if 'artifacts' in result and 'charts' in result['artifacts']:
            chart_files = result['artifacts']['charts']
            
            for chart_file in chart_files:
                try:
                    with open(chart_file, 'r') as f:
                        st.components.v1.html(f.read(), height=500, scrolling=True)
                except Exception as e:
                    st.error(f"Error loading chart: {e}")
        else:
            st.info("No visualizations available")
    
    with tab3:
        st.subheader("Critic Agent Feedback")
        
        feedback = result['critic_feedback']
        
        if feedback['approved']:
            st.success("✅ Recommendation Approved")
        else:
            st.warning("⚠️ Recommendation Needs Refinement")
        
        if feedback['issues']:
            st.markdown("**Issues Identified:**")
            for issue in feedback['issues']:
                st.markdown(f"- {issue}")
        
        if feedback['suggestions']:
            st.markdown("**Suggestions:**")
            for suggestion in feedback['suggestions']:
                st.markdown(f"- {suggestion}")
        
        if feedback.get('missing_considerations'):
            st.markdown("**Missing Considerations:**")
            for consideration in feedback['missing_considerations']:
                st.markdown(f"- {consideration}")
        
        with st.expander("Alternative Perspective"):
            st.markdown(feedback['alternative_perspective'])
    
    with tab4:
        st.subheader("Generated Artifacts")
        
        artifacts = result.get('artifacts', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'csv' in artifacts:
                st.markdown(f"📊 **Scores CSV:** `{artifacts['csv']}`")
            
            if 'report' in artifacts:
                st.markdown(f"📄 **Analysis Report:** `{artifacts['report']}`")
        
        with col2:
            st.markdown(f"🔄 **Iterations:** {result.get('iterations', 1)}")
            st.markdown(f"⏱️ **Analyzed:** {st.session_state.get('analysis_time', 'N/A')}")
        
        if 'charts' in artifacts:
            st.markdown(f"📈 **Visualizations:** {len(artifacts['charts'])} charts generated")

else:
    st.info("👈 Configure your business parameters in the sidebar and click 'Run Analysis' to begin")
    
    st.markdown("---")
    
    st.markdown("""
    ### How It Works
    
    This system uses a **multi-agent architecture** to analyze NYC data and recommend optimal business locations:
    
    1. **Planner Agent**: Interprets your input and creates an analysis plan
    2. **Data Collector Agent**: Fetches real-time data from NYC Open Data, Census, and MTA APIs
    3. **EDA Agent**: Performs exploratory analysis, computes scores, and generates visualizations
    4. **Hypothesis Agent**: Produces data-backed recommendations with evidence
    5. **Critic Agent**: Reviews the recommendation and suggests refinements
    
    The system analyzes:
    - 🏢 **Competition**: Number of existing businesses
    - 💰 **Income**: Median household income
    - 👥 **Population**: Demand proxy
    - 🚇 **Foot Traffic**: Subway ridership data
    - 🏠 **Rent**: Cost indicators
    
    All data is retrieved at runtime - no hardcoded datasets!
    """)

st.sidebar.markdown("---")
