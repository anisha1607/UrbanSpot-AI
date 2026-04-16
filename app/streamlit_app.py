import sys
from pathlib import Path

from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

import os
import sys
import os
from agents.orchestrator import run_analysis
from tools.output import OutputGenerator
import time
import pandas as pd
import streamlit as st
from tools.pdf_generator import generate_pdf_report
from tools.email_service import send_email_with_attachment
import plotly.graph_objects as go
import streamlit.components.v1 as components
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
    
    /* ===== GLOBAL TEXT COLOR FIX ===== */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #111111 !important;
    }
    
    /* Force all Streamlit markdown text to be dark */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
    .stMarkdown strong, .stMarkdown em, .stMarkdown a,
    .stMarkdown ol, .stMarkdown ul,
    .element-container, .stText,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] strong,
    [data-testid="stMarkdownContainer"] em {
        color: #111111 !important;
    }
    
    /* Sidebar text */
    section[data-testid="stSidebar"] * {
        color: #111111 !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stSlider label {
        color: #111111 !important;
    }
    
    /* Captions / small text — keep slightly muted */
    .stCaption, [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    [data-testid="stCaptionContainer"] span {
        color: #555555 !important;
    }

    /* Expander content text */
    .streamlit-expanderContent p,
    .streamlit-expanderContent li,
    .streamlit-expanderContent span,
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] li,
    [data-testid="stExpander"] span {
        color: #111111 !important;
    }
    
    /* Info / Success / Warning / Error boxes */
    .stAlert p, .stAlert span, .stAlert div {
        color: #111111 !important;
    }
    
    /* Tab content text */
    .stTabs [data-baseweb="tab-panel"] p,
    .stTabs [data-baseweb="tab-panel"] li,
    .stTabs [data-baseweb="tab-panel"] span {
        color: #111111 !important;
    }
    
    /* Selectbox, multiselect, slider labels & values */
    label, .stSelectbox label, .stMultiSelect label,
    .stSlider label, .stTextInput label,
    [data-baseweb="select"] span,
    [data-baseweb="tag"] span {
        color: #111111 !important;
    }
    
    /* Report card paragraph text */
    .report-card p, .report-card li, .report-card span,
    .report-card strong {
        color: #222222 !important;
    }
    
    /* ===== CLEAN LIGHT BACKGROUND ===== */
    .stApp {
        background-color: #f9f9f9 !important;
        background-image: radial-gradient(#e5e7eb 1px, transparent 0);
        background-size: 40px 40px;
    }

    /* Force main content area background */
    .main .block-container {
        background-color: transparent !important;
    }
    
    /* ===== HEADINGS ===== */
    h1, h2, h3, h4, h5, h6 {
        color: #111111 !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }
    
    /* ===== METRIC CARDS ===== */
    div[data-testid="metric-container"] {
        background-color: #ffffff !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
        padding: 5% 5% 5% 8%;
        border-radius: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.08);
        border-color: rgba(37, 99, 235, 0.2) !important;
    }

    div[data-testid="stMetricValue"] > div {
        font-size: 2.5rem !important;
        font-weight: 800;
        color: #111111 !important;
        letter-spacing: -0.03em;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #555555 !important;
        margin-bottom: 5px;
    }
    
    div[data-testid="stMetricLabel"] label,
    div[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricLabel"] div {
        color: #555555 !important;
    }
    
    /* ===== EXPANDERS ===== */
    .streamlit-expanderHeader {
        background-color: #ffffff !important;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
        font-weight: 600;
        border: 1px solid rgba(0,0,0,0.03);
        color: #111111 !important;
    }
    
    /* ===== BUTTONS ===== */
    .stButton>button {
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        padding: 0.6rem 2.5rem !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
        transition: transform 0.2s ease, background-color 0.2s ease !important;
    }
    .stButton>button:hover {
        background-color: #1d4ed8 !important;
        transform: scale(1.02) !important;
    }

    /* ===== REPORT CARDS ===== */
    .report-card {
        background-color: #ffffff !important;
        border: 1px solid rgba(0, 0, 0, 0.05);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }
    
    .report-card h4 {
        margin-top: 0px !important;
        padding-top: 0px !important;
        color: #111111 !important;
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #111111 !important;
    }
    
    /* ===== HEADER BAR ===== */
    header[data-testid="stHeader"] {
        background-color: #ffffff !important;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    /* ===== INPUT FIELDS ===== */
    input, textarea, select,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        color: #111111 !important;
        background-color: #ffffff !important;
    }
    
    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab"] {
        color: #555555 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
    }
</style>
""", unsafe_allow_html=True)

if not os.getenv("GROQ_API_KEY"):
    st.error(
        "Missing GROQ_API_KEY.\n"
        "Get one from https://console.groq.com, "
        "set it in your `.env` file and restart Streamlit."
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
st.sidebar.markdown("*Adjust importance of each factor (0-100%)*")

weight_demand = st.sidebar.slider("Demand", 0, 100, 25)
weight_foot_traffic = st.sidebar.slider("Foot Traffic", 0, 100, 20)
weight_income = st.sidebar.slider("Income Level", 0, 100, 20)
weight_competition = st.sidebar.slider("Competition", 0, 100, 20)
weight_rent = st.sidebar.slider("Rent", 0, 100, 15)

total_weight = weight_demand + weight_foot_traffic + weight_income + weight_competition + weight_rent
st.sidebar.info(f"Total percentage: {total_weight}%")

run_disabled = False
if total_weight != 100:
    st.sidebar.warning("⚠️ Weights must sum to exactly 100% to run the analysis.")
    run_disabled = True
else:
    st.sidebar.success("✅ Total weight is 100%. Ready to run!")

if st.sidebar.button("🚀 Run Analysis", type="primary", use_container_width=True, disabled=run_disabled):
    user_input = {
        'business_type': business_type.lower().replace(' ', '_'),
        'borough_filter': boroughs if boroughs else None,
        'weight_demand': weight_demand / 100.0,
        'weight_foot_traffic': weight_foot_traffic / 100.0,
        'weight_income': weight_income / 100.0,
        'weight_competition': weight_competition / 100.0,
        'weight_rent': weight_rent / 100.0
    }
    time_placeholder = st.empty()
    time_placeholder.info("⏰ This multi-agent evaluation typically requires 60-90 seconds. Please do not refresh...")
    
    with st.spinner('🔄 Running deep multi-agent analysis...'):
        try:
            @st.cache_data(show_spinner=False, ttl=3600)
            def cached_analysis(input_data):
                return run_analysis(input_data)
                
            result = cached_analysis(user_input)
            
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
        business_score = min(100.0, result['recommendation'].get('score', 0) * 100)
        st.metric("Overall Match Suitability", f"{business_score:.1f} / 100")
    
    with col3:
        confidence = result['recommendation']['confidence']
        color = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(confidence.lower(), "⚪")
        business_text = {"high": "Optimal Market", "medium": "Favorable Fit", "low": "Caution"}.get(confidence.lower(), confidence.upper())
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
        artifacts = result.get('artifacts', {})
        
        # Why This Location - Enhanced with detailed data-driven reasoning
        why_html = '<div class="report-card"><h4>📊 Why This Location</h4>'
        
        # Add data-driven context from the scored data
        scored_data = result.get('artifacts', {}).get('scored_data_list', None)
        # Try to get scored data from eda_results if available, else use recommendation metrics
        best_loc = recs.get('best_location', '')
        borough = recs.get('borough', '')
        score_val = recs.get('score', 0)
        
        # Build enhanced reasoning
        why_html += f"<p><strong>Location:</strong> {best_loc} in <strong>{borough}</strong></p>"
        why_html += f"<p><strong>Overall Suitability Score:</strong> {min(100.0, score_val * 100):.1f} / 100 — "
        if score_val >= 0.7:
            why_html += "This location significantly outperforms the citywide average, indicating an <em>excellent</em> match for your business type.</p>"
        elif score_val >= 0.5:
            why_html += "This location scores above the citywide median, indicating a <em>strong and viable</em> market opportunity with manageable trade-offs.</p>"
        else:
            why_html += "While not the absolute top-scorer, this location presents a <em>promising opportunity</em> worth investigating further.</p>"
        
        why_html += '<hr style="border:none;border-top:1px solid #eee;margin:12px 0">'
        why_html += '<p><strong>Key Factors Behind This Recommendation:</strong></p>'
        
        import re
        def md_to_html(text):
            # Convert **text** to <b>text</b>
            return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', str(text))
            
        for idx, reason in enumerate(recs.get('reasoning', [])):
            clean_reason = md_to_html(reason).replace('$', '&#36;')
            why_html += f"<p><strong>{idx+1}.</strong> {clean_reason}</p>"
        
        # Add confidence-level explanation
        confidence = recs.get('confidence', 'medium')
        conf_detail = {
            'high': 'Our multi-agent analysis converged with high confidence — the data consistently supports this location across demand, income, competition, and transit metrics.',
            'medium': 'Our analysis shows this location balances multiple factors well. Some trade-offs exist (e.g., moderate competition or rent), but the overall profile is favorable.',
            'low': 'This location has potential but carries higher uncertainty. Consider conducting additional on-the-ground research before committing.'
        }
        why_html += f'<hr style="border:none;border-top:1px solid #eee;margin:12px 0">'
        why_html += f"<p><strong>Confidence Assessment ({confidence.title()}):</strong> {conf_detail.get(confidence, '')}</p>"
        
        why_html += '</div>'
        st.markdown(why_html, unsafe_allow_html=True)
        
        # Trade-offs to Consider
        tradeoffs_html = '<div class="report-card"><h4>⚖️ Trade-offs to Consider</h4>'
        for idx, tr in enumerate(recs.get('trade_offs', [])):
            clean_tr = md_to_html(tr).replace('$', '&#36;')
            tradeoffs_html += f"<p><strong>{idx+1}.</strong> {clean_tr}</p>"
        tradeoffs_html += '</div>'
        st.markdown(tradeoffs_html, unsafe_allow_html=True)
        
        # Standalone Card for Top Alternatives - Pulling directly from Factual EDA results
        alts_html = '<div class="report-card"><h4>🏆 Top Alternatives</h4>'
        alternatives = recs.get('top_alternatives', [])
        
        # Pull directly from scored_data for the top 3 runners-up
        raw_scores = artifacts.get('scored_data')
        if not alternatives and raw_scores is not None:
            # Handle both DataFrame and List of Dicts
            all_records = []
            if hasattr(raw_scores, 'to_dict'):
                all_records = raw_scores.head(10).to_dict('records')
            elif isinstance(raw_scores, list):
                all_records = raw_scores
            
            seen_best = str(recs.get('best_location', '')).lower()
            for item in all_records:
                name = item.get('neighborhood')
                if name and name.lower() not in seen_best and len(alternatives) < 3:
                    alternatives.append({
                        "name": name,
                        "score": item.get('final_score', 0.0),
                        "key_strength": f"Ranked #{len(alternatives)+2} market suitability match"
                    })
        
        if alternatives:
            for idx, alt in enumerate(alternatives):
                name = alt.get('name') or alt.get('neighborhood') or 'Unknown Location'
                score = alt.get('score', 0)
                strength = alt.get('key_strength') or 'Strong market suitability'
                clean_str = md_to_html(strength).replace('$', '&#36;')
                alts_html += f"<p><strong>{idx+1}. {name} (Score: {score:.1f})</strong> - {clean_str}</p>"
        else:
            alts_html += "<p><em>Analyzing secondary candidates for this borough...</em></p>"
        alts_html += '</div>'
        st.markdown(alts_html, unsafe_allow_html=True)
        
        if recs.get('key_insights'):
            clean_insights = md_to_html(recs.get('key_insights')).replace('$', '&#36;')
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
        # Support both in-memory Plotly figures (tests/useful) and saved chart HTML paths
        artifacts = result.get('artifacts', {}) if result else {}
        figs = artifacts.get('figures')
        charts = artifacts.get('charts')

        if figs:
            # In-memory plotly Figure objects or other supported formats
            for i, fig in enumerate(figs):
                # Headings for first few charts
                if i == 0:
                    st.markdown("<h3 style='color:#111111'>🏆 1. Top Neighborhood Rankings</h3>", unsafe_allow_html=True)
                    st.markdown("<p style='color:#333333;margin-top:-8px'><strong>What this shows</strong>: The ultimate ranking of your best locations. A taller bar means a more perfect blend of high traffic, wealthy clients, and low expenses.</p>", unsafe_allow_html=True)
                elif i == 1:
                    st.markdown("<h3 style='color:#111111'>⚖️ 2. Detailed Neighborhood Breakdown</h3>", unsafe_allow_html=True)
                    st.markdown("<p style='color:#333333;margin-top:-8px'><strong>What this shows</strong>: The individual strengths of each neighborhood. Check the spikes for specific local advantages like extremely low rent or massive transit availability!</p>", unsafe_allow_html=True)
                elif i == 2:
                    st.markdown("<h3 style='color:#111111'>📊 3. Overall Market Distribution</h3>", unsafe_allow_html=True)
                    st.markdown("<p style='color:#333333;margin-top:-8px'><strong>What this shows</strong>: A market-wide perspective illustrating how your selected top locations absolutely dominate the vast majority of 'average' zip codes in NYC.</p>", unsafe_allow_html=True)
                elif i == 3:
                    st.markdown("<h3 style='color:#111111'>📍 4. The 'Sweet Spot' Matrix (Income vs Competition)</h3>", unsafe_allow_html=True)
                    st.markdown("<p style='color:#333333;margin-top:-8px'><strong>What this shows</strong>: The ultimate business target! The most profitable locations to target sit strictly on the far right (Highest Wealth) while remaining close to the bottom (Lowest Competition).</p>", unsafe_allow_html=True)

                # Flexible rendering depending on the type of `fig`
                try:
                    if isinstance(fig, go.Figure):
                        st.plotly_chart(fig, use_container_width=True, theme="streamlit")
                    elif isinstance(fig, dict):
                        # dict may be a Plotly figure spec
                        try:
                            st.plotly_chart(go.Figure(fig), use_container_width=True, theme="streamlit")
                        except Exception:
                            st.write(fig)
                    elif isinstance(fig, str):
                        # Could be HTML, raw plotly.to_html output, or a file path
                        cleaned = fig.strip()
                        if cleaned.startswith('<') and '</' in cleaned:
                            components.html(fig, height=600, scrolling=True)
                        elif os.path.exists(fig):
                            try:
                                with open(fig, 'r', encoding='utf-8') as _f:
                                    components.html(_f.read(), height=600, scrolling=True)
                            except Exception as e:
                                st.error(f"Failed to read chart file {fig}: {e}")
                        else:
                            # Fallback: print the string so developer can inspect
                            st.write(fig)
                    else:
                        # Unknown type: show repr so we can debug
                        st.write(repr(fig))
                except Exception as e:
                    st.error(f"Error rendering figure #{i}: {e}")

        elif charts:
            # charts are saved HTML file paths; embed them into Streamlit
            chart_names = [
                ("🏆 Neighborhood Suitability Rankings", "Overall composite score for the top 10 candidate locations"),
                ("⚖️ Multi-Metric Comparison", "Normalized side-by-side view of competition, income, rent & population"),
                ("📊 Score Distribution", "How all analyzed neighborhoods are spread across score ranges"),
                ("📍 Income vs Competition Matrix", "Sweet-spot analysis mapping wealth against market saturation")
            ]
            for i, chart_path in enumerate(charts):
                try:
                    with open(chart_path, 'r', encoding='utf-8') as f:
                        html = f.read()
                    # Use descriptive chart names
                    if i < len(chart_names):
                        name, desc = chart_names[i]
                        st.markdown(f"<h3 style='color:#111111'>{name}</h3>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color:#333333;margin-top:-8px'><strong>What this shows</strong>: {desc}</p>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<h3 style='color:#111111'>Chart {i+1}</h3>", unsafe_allow_html=True)
                    components.html(html, height=600, scrolling=True)
                except Exception as e:
                    st.error(f"Failed to load chart {chart_path}: {e}")

        else:
            st.info("No visualizations available - please run the analysis above.")
    
    with tab3:
        st.subheader("Critic Agent Feedback")
        
        feedback = result['critic_feedback']
        
        if feedback['approved']:
            st.success("✅ Recommendation Approved")
        else:
            st.warning("⚠️ Recommendation Needs Refinement")
        
        # Helper to filter out "data quality" mentions
        def _filter_data_quality(text):
            """Remove any text containing 'data quality' keyword."""
            if not text:
                return text
            if isinstance(text, str):
                if 'data quality' in text.lower():
                    return None
                return text
            return text
        
        # Critic Feedback UI Polish
        critic_html = '<div class="report-card"><h4>🔍 Critic Analysis</h4>'
        
        # Display the main verdict
        if feedback.get('approved'):
            critic_html += '<p style="color:#28a745; font-weight:bold;">✅ Recommendation Approved</p>'
        else:
            critic_html += '<p style="color:#dc3545; font-weight:bold;">⚠️ Recommendation Needs Refinement</p>'
        
        critic_html += '<hr style="border:none;border-top:1px solid #eee;margin:12px 0">'
        
        # Issues
        if feedback['issues']:
            filtered_issues = [i for i in feedback['issues'] if _filter_data_quality(i)]
            if filtered_issues:
                critic_html += '<p><strong>Issues Identified:</strong></p><ul>'
                for issue in filtered_issues:
                    critic_html += f"<li>{issue}</li>"
                critic_html += '</ul>'
        
        # Suggestions        
        if feedback['suggestions']:
            filtered_suggestions = [s for s in feedback['suggestions'] if _filter_data_quality(s)]
            if filtered_suggestions:
                critic_html += '<p><strong>Strategic Suggestions:</strong></p><ul>'
                for sug in filtered_suggestions:
                    critic_html += f"<li>{sug}</li>"
                critic_html += '</ul>'

        # Missing Considerations
        if feedback.get('missing_considerations'):
            filtered_considerations = [c for c in feedback['missing_considerations'] if _filter_data_quality(c)]
            if filtered_considerations:
                critic_html += '<p><strong>Missing Context:</strong></p><ul>'
                for item in filtered_considerations:
                    critic_html += f"<li>{item}</li>"
                critic_html += '</ul>'
        
        critic_html += '</div>'
        
        # Alternative Perspective
        alt_perspective = feedback.get('alternative_perspective', '')
        filtered_alt = _filter_data_quality(alt_perspective)
        if filtered_alt:
            alt_html = f'<div class="report-card" style="background-color: #f8f9fa;"><h4>💡 Strategic Perspective</h4><p>{filtered_alt}</p></div>'
            critic_html += alt_html
            
        st.markdown(critic_html, unsafe_allow_html=True)
    
    with tab4:
        st.subheader("Generated Artifacts")
        
        artifacts = result.get('artifacts', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'csv' in artifacts:
                st.markdown("📊 **Scores CSV:** Neighborhood scoring data")
            
            if 'report' in artifacts:
                st.markdown("📄 **Analysis Report:** Full analysis summary")
        
        with col2:
            st.markdown(f"🔄 **Iterations:** {result.get('iterations', 1)}")
            st.markdown(f"⏱️ **Analyzed:** {st.session_state.get('analysis_time', 'N/A')}")
        
        if 'charts' in artifacts:
            st.markdown(f"📈 **Visualizations:** {len(artifacts['charts'])} charts generated")
        
        st.markdown("---")
        st.subheader("⬇️ Download Artifacts")
        
        dl_col1, dl_col2 = st.columns(2)
        
        # Download Scores CSV
        with dl_col1:
            if 'csv' in artifacts:
                csv_path = artifacts['csv']
                try:
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        csv_data = f.read()
                    st.download_button(
                        label="📊 Download Scores CSV",
                        data=csv_data,
                        file_name="neighborhood_scores.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                except Exception:
                    st.info("Scores CSV not available for download.")
        
        # Download Analysis Report PDF
        with dl_col2:
            if st.button("📄 Prepare Analysis Report PDF", use_container_width=True):
                with st.spinner("Generating PDF..."):
                    try:
                        pdf_path = generate_pdf_report(result, "analysis_report.pdf")
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                label="⬇️ Download PDF Report",
                                data=f,
                                file_name="NYC_Business_Report.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"❌ PDF Generation failed: {str(e)}")
            
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
                        st.info("💡 Trying again usually works. If it persists, try the download buttons above.")
                
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
