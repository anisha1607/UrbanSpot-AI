import sys
from pathlib import Path

from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

import os
import streamlit as st
from agents.orchestrator import run_analysis
from tools.pdf_generator import generate_pdf_report
from tools.email_service import send_email_with_attachment
import plotly.graph_objects as go
from datetime import datetime


st.set_page_config(
    page_title="NYC Business Location Advisor",
    page_icon="🏙️",
    layout="wide"
)

st.markdown("""
<style>
    /* Premium Minimalist Font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #111111 !important;
    }
    
    /* Clean Light Background */
    .stApp {
        background-color: #f9f9f9;
        background-image: radial-gradient(#e5e7eb 1px, transparent 0);
        background-size: 40px 40px;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #111111 !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }
    
    /* Elegant Pinterest-style Cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
        padding: 5% 5% 5% 8%;
        border-radius: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.08);
        border-color: rgba(230, 0, 35, 0.2) !important;
    }

    div[data-testid="stMetricValue"] > div {
        font-size: 2.5rem !important;
        font-weight: 800;
        color: #111111 !important;
        letter-spacing: -0.03em;
    }
    
    /* Soft Expanders */
    .streamlit-expanderHeader {
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
        font-weight: 600;
        border: 1px solid rgba(0,0,0,0.03);
    }
    
    /* Pinterest-style Buttons */
    .stButton>button {
        background-color: #E60023 !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        padding: 0.6rem 2.5rem !important;
        box-shadow: 0 4px 14px rgba(230, 0, 35, 0.3) !important;
        transition: transform 0.2s ease, background-color 0.2s ease !important;
    }
    .stButton>button:hover {
        background-color: #ad081b !important;
        transform: scale(1.02) !important;
    }

    /* Target generic metrics text to stop hiding */
    div[data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #666666 !important;
        margin-bottom: 5px;
    }

    /* Pinterest Report Cards styling */
    .report-card {
        background-color: #ffffff;
        border: 1px solid rgba(0, 0, 0, 0.05);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }
    
    .report-card h4 {
        margin-top: 0px !important;
        padding-top: 0px !important;
    }

    /* Sidebar Clean styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

if not os.getenv("ANTHROPIC_API_KEY"):
    st.error(
        "Missing ANTHROPIC_API_KEY.\n"
        "Set it in your environment, or create a `.env` file from `.env.example` and restart Streamlit."
    )
    st.stop()

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
weight_competition = st.sidebar.slider("Competition", 0.0, 1.0, 0.20, 0.05)
weight_rent = st.sidebar.slider("Rent", 0.0, 1.0, 0.15, 0.05)

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
    time_placeholder = st.empty()
    time_placeholder.info("⏰ This multi-agent evaluation typically requires 60-90 seconds. Please do not refresh...")
    
    with st.spinner('🔄 Running deep multi-agent analysis...'):
        try:
            result = run_analysis(user_input)
            
            st.session_state['result'] = result
            st.session_state['analysis_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            time_placeholder.empty()
            st.success("✅ Analysis complete!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

if 'result' in st.session_state:
    result = st.session_state['result']
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1.5, 1, 1.3])
    
    with col1:
        st.markdown(f"### 🎯 Best Location: {result['recommendation']['best_location']}")
        st.markdown(f"**Borough:** {result['recommendation']['borough']}")
    
    with col2:
        business_score = min(100.0, result['recommendation'].get('score', 0))
        st.metric("Overall Match Suitability", f"{business_score:.1f} / 100")
    
    with col3:
        confidence = result['recommendation']['confidence']
        color = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(confidence.lower(), "⚪")
        business_text = {"high": "Optimal Market", "medium": "Favorable Fit", "low": "Requires Caution"}.get(confidence.lower(), confidence.upper())
        st.metric("Market Viability", f"{color} {business_text}")
        
        dynamic_reason = result['recommendation'].get('confidence_reasoning', '')
        if dynamic_reason:
            st.caption(f"*{dynamic_reason}*")
        elif business_text == "Favorable Fit":
            st.caption("*(Favorable Fit represents data-backed stability across core metrics acknowledging minor competitive offsets or mathematical ties!)*")
        elif business_text == "Optimal Market":
            st.caption("*(Optimal Market reflects phenomenal data-backed superiority isolating a clear uncompromised winner!)*")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Recommendation", "📈 Visualizations", "🔍 Critic Feedback", "📁 Artifacts"])
    
    with tab1:
        st.subheader("AI Analysis & Recommendation Report")
        
        recs = result.get('recommendation', {})
        
        # Why This Location
        why_html = '<div class="report-card"><h4>📊 Why This Location</h4>'
        for idx, reason in enumerate(recs.get('reasoning', [])):
            clean_reason = str(reason).replace('$', '&#36;')
            why_html += f"<p><strong>{idx+1}.</strong> {clean_reason}</p>"
        why_html += '</div>'
        st.markdown(why_html, unsafe_allow_html=True)
        
        # Trade-offs to Consider
        tradeoffs_html = '<div class="report-card"><h4>⚖️ Trade-offs to Consider</h4>'
        for idx, tr in enumerate(recs.get('trade_offs', [])):
            clean_tr = str(tr).replace('$', '&#36;')
            tradeoffs_html += f"<p><strong>{idx+1}.</strong> {clean_tr}</p>"
        tradeoffs_html += '</div>'
        st.markdown(tradeoffs_html, unsafe_allow_html=True)
        
        # Top Alternatives
        alts_html = '<div class="report-card"><h4>🏆 Top Alternatives</h4>'
        for idx, alt in enumerate(recs.get('top_alternatives', [])):
            clean_str = str(alt.get('key_strength', '')).replace('$', '&#36;')
            alts_html += f"<p><strong>{idx+1}. {alt.get('name', 'N/A')} (Score: {alt.get('score', 0):.1f})</strong> - {clean_str}</p>"
        alts_html += '</div>'
        st.markdown(alts_html, unsafe_allow_html=True)
        
        if recs.get('key_insights'):
            clean_insights = str(recs.get('key_insights')).replace('$', '&#36;')
            st.info(f"💡 **KEY INSIGHT:** {clean_insights}")
        
        with st.expander("ℹ️ How did we calculate these scores?"):
            st.markdown(
                "You might be wondering how perfect a neighborhood can truly be in NYC. "
                "Our algorithm calculates a mathematical baseline considering thousands of zip codes! "
                "Because cities naturally have heavy trade-offs (e.g. extremely high foot traffic *always* correlates with intense rent and heavy competition bounds), "
                "it is physically impossible for any real neighborhood to achieve the original 'perfect algorithmic peak'. "
                "Instead, we dynamically scale our suitability metric out of 100 relative to the **most profitable real-world opportunity** we identified for you. "
                "This ensures the top recommendations are truly the best available, even with built-in financial trade-offs!"
            )
    
    with tab2:
        st.subheader("Analysis Visualizations")
        st.markdown("We've evaluated dozens of neighborhood variables. Here are simplified visual charts comparing your top targets!")
        
        if 'artifacts' in result and 'figures' in result['artifacts']:
            figs = result['artifacts']['figures']
            
            for i, fig in enumerate(figs):
                if i == 0:
                    st.markdown("### 🏆 1. Top Neighborhood Rankings")
                    st.markdown("**What this shows**: The ultimate ranking of your best locations. A taller bar means a more perfect blend of high traffic, wealthy clients, and low expenses.")
                elif i == 1:
                    st.markdown("### ⚖️ 2. Detailed Neighborhood Breakdown")
                    st.markdown("**What this shows**: The individual strengths of each neighborhood. Check the spikes for specific local advantages like extremely low rent or massive transit availability!")
                elif i == 2:
                    st.markdown("### 📊 3. Overall Market Distribution")
                    st.markdown("**What this shows**: A market-wide perspective illustrating how your selected top locations absolutely dominate the vast majority of 'average' zip codes in NYC.")
                elif i == 3:
                     st.markdown("### 📍 4. The 'Sweet Spot' Matrix (Income vs Competition)")
                     st.markdown("**What this shows**: The ultimate business target! The most profitable locations to target sit strictly on the far right (Highest Wealth) while remaining close to the bottom (Lowest Competition).")
                     
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")
        else:
            st.info("No visualizations available - please run the analysis above.")
    
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
            
        st.markdown("---")
        st.subheader("📬 Email Report")
        email_addr = st.text_input("Enter Email Address", placeholder="example@email.com")
        
        if st.button("📧 Send PDF via Email", type="secondary"):
            if not email_addr:
                st.warning("Please enter a valid email address.")
            else:
                # Part 1: Generate PDF
                pdf_path = None
                with st.spinner("📄 Step 1/2: Generating PDF Report..."):
                    try:
                        pdf_path = generate_pdf_report(result, "analysis_report.pdf")
                        st.info("✅ PDF Generated successfully.")
                    except Exception as e:
                        st.error(f"❌ PDF Generation failed: {str(e)}")
                        st.info("💡 Trying again usually works. If it persists, try the 'Prepare Download' button below.")
                
                # Part 2: Send Email
                if pdf_path:
                    with st.spinner("📤 Step 2/2: Sending Email..."):
                        try:
                            subject = f"NYC Business Location Report - {result['recommendation']['best_location']}"
                            body = f"Hello,\n\nPlease find attached the AI-powered business location report for {result['recommendation']['best_location']}.\n\nBest regards,\nUrbanSpot-AI Team"
                            
                            send_email_with_attachment(
                                email_addr,
                                subject,
                                body,
                                pdf_path
                            )
                            st.success(f"✅ Report successfully sent to {email_addr}!")
                        except Exception as e:
                            st.error(f"❌ Email delivery failed: {str(e)}")
                            st.info("💡 Check your SMTP credentials in the .env file. For Gmail, you MUST use an 'App Password'.")
        
        # Also add a direct download button for convenience
        if st.button("📄 Prepare Download Link"):
            with st.spinner("Generating PDF..."):
                pdf_path = generate_pdf_report(result, "analysis_report.pdf")
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=f,
                        file_name="NYC_Business_Report.pdf",
                        mime="application/pdf"
                    )


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
