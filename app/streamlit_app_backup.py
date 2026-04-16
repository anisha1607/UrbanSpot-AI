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
    page_icon="📍",
    layout="wide"
)

st.markdown("""
<style>
    /* Modern Professional Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1f2937 !important;
    }
    
    /* Animated Gradient Background with Glass Effect */
    .stApp {
        background: linear-gradient(135deg, 
            #667eea 0%, 
            #764ba2 25%, 
            #f093fb 50%, 
            #4facfe 75%, 
            #00f2fe 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Frosted Glass Overlay */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(100px);
        -webkit-backdrop-filter: blur(100px);
        pointer-events: none;
        z-index: 0;
    }
    
    /* Ensure content is above overlay */
    .block-container {
        position: relative;
        z-index: 1;
    }

    /* Beautiful Headers */
    h1 {
        color: #111827 !important;
        font-weight: 800 !important;
        font-size: 3rem !important;
        letter-spacing: -0.03em !important;
        margin-bottom: 0.5rem !important;
        background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    h2 {
        color: #1f2937 !important;
        font-weight: 700 !important;
        font-size: 1.75rem !important;
        letter-spacing: -0.02em !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        color: #374151 !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
        letter-spacing: -0.02em !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    h4 {
        color: #4b5563 !important;
        font-weight: 600 !important;
        font-size: 1.125rem !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Glassmorphic Metric Cards */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        padding: 2rem 1.5rem !important;
        border-radius: 20px !important;
        box-shadow: 
            0 8px 32px 0 rgba(31, 38, 135, 0.15),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.5) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px) scale(1.02) !important;
        background: rgba(255, 255, 255, 0.85) !important;
        box-shadow: 
            0 20px 40px 0 rgba(31, 38, 135, 0.25),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.6) !important;
        border-color: rgba(30, 64, 175, 0.4) !important;
    }

    div[data-testid="stMetricValue"] > div {
        font-size: 2.75rem !important;
        font-weight: 800 !important;
        color: #1e40af !important;
        letter-spacing: -0.02em !important;
        line-height: 1 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        color: #6b7280 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        margin-bottom: 0.75rem !important;
    }
    
    /* Glassmorphic Expanders */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border-radius: 12px;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: #374151 !important;
        padding: 1rem 1.25rem !important;
        transition: all 0.2s ease;
        box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.1);
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.8) !important;
        border-color: rgba(255, 255, 255, 0.5);
        box-shadow: 0 8px 24px 0 rgba(31, 38, 135, 0.15);
    }
    
    /* Premium Glass Buttons */
    .stButton>button {
        background: rgba(30, 64, 175, 0.9) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 0.875rem 2rem !important;
        box-shadow: 
            0 4px 16px 0 rgba(30, 64, 175, 0.3),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.2) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: 0.02em !important;
    }
    
    .stButton>button:hover {
        background: rgba(30, 58, 138, 1) !important;
        transform: translateY(-2px) !important;
        box-shadow: 
            0 12px 24px 0 rgba(30, 64, 175, 0.4),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.3) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
    }
    
    .stButton>button:active {
        transform: translateY(0) !important;
    }

    /* Glassmorphic Report Cards */
    .report-card {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-left: 4px solid rgba(30, 64, 175, 0.8);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 
            0 8px 32px 0 rgba(31, 38, 135, 0.12),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.5);
        word-wrap: break-word;
        overflow-wrap: break-word;
        transition: all 0.3s ease;
    }
    
    .report-card:hover {
        background: rgba(255, 255, 255, 0.85) !important;
        box-shadow: 
            0 12px 40px 0 rgba(31, 38, 135, 0.18),
            inset 0 1px 0 0 rgba(255, 255, 255, 0.6);
        border-left-color: rgba(124, 58, 237, 0.9);
        transform: translateY(-2px);
    }
    
    .report-card h4 {
        margin-top: 0 !important;
        padding-top: 0 !important;
        color: #111827 !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.25rem !important;
        letter-spacing: -0.01em !important;
    }
    
    .report-card p {
        color: #374151 !important;
        line-height: 1.8 !important;
        margin-bottom: 1rem !important;
        word-wrap: break-word;
        overflow-wrap: break-word;
        max-width: 100%;
        font-size: 1rem !important;
    }
    
    .report-card p strong {
        color: #1f2937 !important;
        font-weight: 600 !important;
    }

    /* Glassmorphic Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 2px 0 20px 0 rgba(31, 38, 135, 0.1);
    }
    
    section[data-testid="stSidebar"] h2 {
        color: #111827 !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
    }
    
    section[data-testid="stSidebar"] h3 {
        color: #374151 !important;
        font-size: 1.125rem !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
        .hero-container {
        text-align: center;
        padding: 3rem 2rem;
        margin-bottom: 2rem;

        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);

        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.3);

        box-shadow: 
            0 10px 40px rgba(31, 38, 135, 0.2),
            inset 0 1px 0 rgba(255,255,255,0.5);

        max-width: 900px;
        margin-left: auto;
        margin-right: auto;

        transition: all 0.3s ease;
    }

    .hero-container:hover {
        transform: translateY(-3px);
        background: rgba(255, 255, 255, 0.8);
    }

    /* Subtitle */
    .hero-subtitle {
        font-size: 1.25rem;
        font-weight: 600;
        color: #374151;
        margin-top: 0.5rem;
    }

    /* Caption */
    .hero-caption {
        font-size: 0.95rem;
        color: #6b7280;
        margin-top: 0.5rem;
    }    
                
    
    [data-testid="column"] {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: stretch;       
    }        
    /* Fix text overflow globally */
    .stMarkdown {
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    /* Glassmorphic Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: #6b7280;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        transition: all 0.2s ease;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #374151;
        background: rgba(255, 255, 255, 0.4);
    }
    
    .stTabs [aria-selected="true"] {
        color: #1e40af !important;
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 4px 12px 0 rgba(31, 38, 135, 0.15) !important;
    }
    
    /* Glassmorphic Alert Boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border-radius: 12px;
        border-left-width: 4px;
        padding: 1rem 1.25rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.1);
    }
    
    /* Captions */
    .stCaption {
        color: #6b7280 !important;
        font-size: 0.875rem !important;
        line-height: 1.6 !important;
    }
    
    /* Better spacing */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
    }
    
    /* Glassmorphic Dividers */
    hr {
        margin: 2.5rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(255, 255, 255, 0.5) 50%, 
            transparent);
    }
    
    /* Input fields with glass effect */
    input[type="text"], 
    input[type="email"],
    input[type="number"],
    textarea {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
    }
    
    input[type="text"]:focus, 
    input[type="email"]:focus,
    input[type="number"]:focus,
    textarea:focus {
        background: rgba(255, 255, 255, 0.8) !important;
        border-color: rgba(30, 64, 175, 0.4) !important;
        box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

if not os.getenv("GOOGLE_API_KEY"):
    st.error(
        "⚠️ Missing GOOGLE_API_KEY. "
        "Set it in your environment, or create a `.env` file from `.env.example` and restart Streamlit."
    )
    st.stop()

# === HEADER ===
st.markdown("""
<div class="hero-container">
    <h1>NYC Business Location Advisor</h1>
    <p class="hero-subtitle">AI-Powered Multi-Agent System for Optimal Business Placement</p>
    <p class="hero-caption">Analyze 165+ NYC neighborhoods using real-time data from NYC Open Data, Census Bureau, and MTA</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# === SIDEBAR ===
st.sidebar.header("Configuration")

business_type = st.sidebar.selectbox(
    "Business Type",
    ["Coffee Shop", "Gym", "Salon", "Restaurant", "Retail Store"],
    help="Select the type of business you want to analyze"
)

st.sidebar.markdown("---")
st.sidebar.subheader("Borough Filter")

boroughs = st.sidebar.multiselect(
    "Target Boroughs",
    ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"],
    help="Leave empty to analyze all NYC boroughs"
)

# st.sidebar.markdown("---")
# st.sidebar.subheader("Scoring Weights")
# st.sidebar.caption("Adjust the importance of each factor (must sum to 1.0)")

# weight_demand = st.sidebar.slider("Customer Demand", 0.0, 1.0, 0.25, 0.05, help="Population and market size")
# weight_foot_traffic = st.sidebar.slider("Foot Traffic", 0.0, 1.0, 0.20, 0.05, help="Subway ridership data")
# weight_income = st.sidebar.slider("Income Level", 0.0, 1.0, 0.20, 0.05, help="Median household income")
# weight_competition = st.sidebar.slider("Low Competition", 0.0, 1.0, 0.20, 0.05, help="Fewer existing businesses")
# weight_rent = st.sidebar.slider("Affordable Rent", 0.0, 1.0, 0.15, 0.05, help="Lower cost indicators")

# total_weight = weight_demand + weight_foot_traffic + weight_income + weight_competition + weight_rent

# if abs(total_weight - 1.0) < 0.01:
#     st.sidebar.success(f" Total weight: {total_weight:.2f}")
# else:
#     st.sidebar.warning(f" Total weight: {total_weight:.2f} (should be 1.0)")
# Scoring weight inputs — use 0-100 percent sliders and auto-normalize to sum=1
st.sidebar.header("Importance Weights (percentage)")
_defaults = {"demand": 25, "foot_traffic": 25, "income": 20, "competition": 15, "rent": 15}

demand_pct = st.sidebar.slider("Demand (%)", 0, 100, _defaults["demand"])
foot_traffic_pct = st.sidebar.slider("Foot traffic (%)", 0, 100, _defaults["foot_traffic"])
income_pct = st.sidebar.slider("Median income (%)", 0, 100, _defaults["income"])
competition_pct = st.sidebar.slider("Competition (%)", 0, 100, _defaults["competition"])
rent_pct = st.sidebar.slider("Rent / Cost (%)", 0, 100, _defaults["rent"])

total_pct = demand_pct + foot_traffic_pct + income_pct + competition_pct + rent_pct

# if _total_pct == 0:
#     st.sidebar.warning("All weights are zero — using balanced defaults.")
#     normalized_weights = {k: v / 100.0 for k, v in _defaults.items()}
# else:
#     normalized_weights = {
#         "demand": demand_pct / _total_pct,
#         "foot_traffic": foot_traffic_pct / _total_pct,
#         "income": income_pct / _total_pct,
#         "competition": competition_pct / _total_pct,
#         "rent": rent_pct / _total_pct,
#     }

# st.sidebar.markdown(f"**Normalized weights (sum = {sum(normalized_weights.values()):.2f})**")
# st.sidebar.write({k: f"{v:.0%}" for k, v in normalized_weights.items()})
if total_pct == 0:
    st.sidebar.warning("All weights are zero — using balanced defaults.")
    demand_pct = _defaults["demand"]
    foot_traffic_pct = _defaults["foot_traffic"]
    income_pct = _defaults["income"]
    income_pct = _defaults["income"]
    competition_pct = _defaults["competition"]
    rent_pct = _defaults["rent"]
    total_pct = 100

# Disallow processing when total exceeds 100%
run_disabled = False
if total_pct > 100:
    st.sidebar.error(f"Total weight is {total_pct:.0f}% — please reduce sliders so the total is at most 100%.")
    run_disabled = True
else:
    # Friendly status like original single-sum check (tolerance 1%)
    if abs(total_pct - 100) <= 1:
        st.sidebar.success(f" Total weight: {total_pct:.0f}%")
    else:
        st.sidebar.info(f" Total weight: {total_pct:.0f}% (recommended to sum to 100%)")

# Convert percent sliders to fractional weights (will sum <= 1.0)
normalized_weights = {
    "demand": demand_pct / 100.0,
    "foot_traffic": foot_traffic_pct / 100.0,
    "income": income_pct / 100.0,
    "competition": competition_pct / 100.0,
    "rent": rent_pct / 100.0,
}   
# === RUN ANALYSIS ===
if st.sidebar.button("Run Analysis", type="primary", use_container_width=True):
    user_input = {
        'business_type': business_type.lower().replace(' ', '_'),
        'borough_filter': boroughs if boroughs else None,
         'weight_demand': normalized_weights["demand"],
        'weight_foot_traffic': normalized_weights["foot_traffic"],
        'weight_income': normalized_weights["income"],
        'weight_competition': normalized_weights["competition"],
        'weight_rent': normalized_weights["rent"]
    }
    
    time_placeholder = st.empty()
    time_placeholder.info("⏱️ This multi-agent evaluation typically requires 60-90 seconds. Please do not refresh...")
    
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

# === RESULTS ===
if 'result' in st.session_state:
    result = st.session_state['result']
    
    st.markdown('<div class="top-glass-container">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.5, 1, 1.3], gap="large")

    with col1:
        st.markdown("### 🎯 Best Location")
        st.markdown(f"<div class='big-location'>{result['recommendation']['best_location']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='borough-text'>📍 Borough: <strong>{result['recommendation']['borough']}</strong></div>", unsafe_allow_html=True)

    with col2:
        business_score = min(100.0, result['recommendation'].get('score', 0))
        st.metric("Overall Match Suitability", f"{business_score:.1f}/100")

    with col3:
        confidence = result['recommendation']['confidence']
        business_text = {
            "high": "Optimal Market", 
            "medium": "Favorable Fit", 
            "low": "Caution"
        }.get(confidence.lower(), confidence.upper())

        st.metric("Market Viability", business_text)

        dynamic_reason = result['recommendation'].get('confidence_reasoning', '')
        if dynamic_reason:
            st.caption(dynamic_reason)

    st.markdown('</div>', unsafe_allow_html=True)
    # === TABS ===
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Recommendation", "📈 Visualizations", "🔍 Critic Feedback", "📁 Artifacts"])
    
    # === TAB 1: RECOMMENDATION ===
    with tab1:
        st.markdown("## AI Analysis & Recommendation Report")
        
        recs = result.get('recommendation', {})
        
        # Why This Location
        why_html = '<div class="report-card"><h4>💡 Why This Location</h4>'
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
            alts_html += f"<p><strong>{idx+1}. {alt.get('name', 'N/A')} (Score: {alt.get('score', 0):.1f})</strong> — {clean_str}</p>"
        alts_html += '</div>'
        st.markdown(alts_html, unsafe_allow_html=True)
        
        if recs.get('key_insights'):
            clean_insights = str(recs.get('key_insights')).replace('$', '&#36;')
            st.info(f"**💡 KEY INSIGHT:** {clean_insights}")
        
        with st.expander("ℹ️ How did we calculate these scores?"):
            st.markdown(
                "You might be wondering how perfect a neighborhood can truly be in NYC. "
                "Our algorithm calculates a mathematical baseline considering thousands of zip codes. "
                "Because cities naturally have heavy trade-offs (e.g., extremely high foot traffic *always* "
                "correlates with intense rent and heavy competition), it is physically impossible for any "
                "real neighborhood to achieve the original 'perfect algorithmic peak'. "
                "\n\n"
                "Instead, we dynamically scale our suitability metric out of 100 relative to the **most profitable "
                "real-world opportunity** we identified for you. This ensures the top recommendations are truly "
                "the best available, even with built-in financial trade-offs."
            )
    
    # === TAB 2: VISUALIZATIONS ===
    with tab2:
        st.markdown("## Analysis Visualizations")
        st.caption("We've evaluated dozens of neighborhood variables. Here are simplified visual charts comparing your top targets.")
        
        if 'artifacts' in result and 'figures' in result['artifacts']:
            figs = result['artifacts']['figures']
            
            for i, fig in enumerate(figs):
                if i == 0:
                    st.markdown("### 🏆 1. Top Neighborhood Rankings")
                    st.caption("**What this shows:** The ultimate ranking of your best locations. A taller bar means a more perfect blend of high traffic, wealthy clients, and low expenses.")
                elif i == 1:
                    st.markdown("### ⚖️ 2. Detailed Neighborhood Breakdown")
                    st.caption("**What this shows:** The individual strengths of each neighborhood. Check the spikes for specific local advantages like extremely low rent or massive transit availability.")
                elif i == 2:
                    st.markdown("### 📊 3. Overall Market Distribution")
                    st.caption("**What this shows:** A market-wide perspective illustrating how your selected top locations absolutely dominate the vast majority of average zip codes in NYC.")
                elif i == 3:
                    st.markdown("### 📍 4. The Sweet Spot Matrix (Income vs Competition)")
                    st.caption("**What this shows:** The ultimate business target! The most profitable locations sit on the far right (Highest Wealth) while remaining close to the bottom (Lowest Competition).")
                     
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")
                if i < len(figs) - 1:
                    st.markdown("---")
        else:
            st.info("📊 No visualizations available — please run the analysis above.")
    
    # === TAB 3: CRITIC FEEDBACK ===
    with tab3:
        st.markdown("## Critic Agent Feedback")
        
        feedback = result['critic_feedback']
        
        if feedback['approved']:
            st.success("✅ **Recommendation Approved**")
        else:
            st.warning("⚠️ **Recommendation Needs Refinement**")
        
        if feedback['issues']:
            st.markdown("### Issues Identified")
            for issue in feedback['issues']:
                st.markdown(f"- {issue}")
        
        if feedback['suggestions']:
            st.markdown("### Suggestions")
            for suggestion in feedback['suggestions']:
                st.markdown(f"- {suggestion}")
        
        if feedback.get('missing_considerations'):
            st.markdown("### Missing Considerations")
            for consideration in feedback['missing_considerations']:
                st.markdown(f"- {consideration}")
        
        if feedback.get('alternative_perspective'):
            with st.expander("💭 Alternative Perspective"):
                st.markdown(feedback['alternative_perspective'])
    
    # === TAB 4: ARTIFACTS ===
    with tab4:
        st.markdown("## Generated Artifacts")
        
        artifacts = result.get('artifacts', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'csv' in artifacts:
                st.markdown(f"**📊 Scores CSV:** `{artifacts['csv']}`")
            
            if 'report' in artifacts:
                st.markdown(f"**📄 Analysis Report:** `{artifacts['report']}`")
        
        with col2:
            st.markdown(f"**🔄 Iterations:** {result.get('iterations', 1)}")
            st.markdown(f"**⏱️ Analyzed:** {st.session_state.get('analysis_time', 'N/A')}")
        
        if 'charts' in artifacts:
            st.markdown(f"**📈 Visualizations:** {len(artifacts['charts'])} charts generated")
            
        st.markdown("---")
        st.markdown("### 📬 Email Report")
        
        email_addr = st.text_input("Email Address", placeholder="your@email.com")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("📧 Send PDF via Email", use_container_width=True):
                if not email_addr:
                    st.warning("⚠️ Please enter a valid email address.")
                else:
                    pdf_path = None
                    with st.spinner("📄 Step 1/2: Generating PDF Report..."):
                        try:
                            pdf_path = generate_pdf_report(result, "analysis_report.pdf")
                            st.info("✅ PDF Generated successfully.")
                        except Exception as e:
                            st.error(f"❌ PDF Generation failed: {str(e)}")
                            st.info("💡 Trying again usually works. If it persists, try the 'Prepare Download' button.")
                    
                    if pdf_path:
                        with st.spinner("📤 Step 2/2: Sending Email..."):
                            try:
                                subject = f"NYC Business Location Report - {result['recommendation']['best_location']}"
                                body = f"Hello,\n\nPlease find attached the AI-powered business location report for {result['recommendation']['best_location']}.\n\nBest regards,\nUrbanSpot AI Team"
                                
                                send_email_with_attachment(email_addr, subject, body, pdf_path)
                                st.success(f"✅ Report successfully sent to {email_addr}!")
                            except Exception as e:
                                st.error(f"❌ Email delivery failed: {str(e)}")
                                st.info("💡 Check your SMTP credentials in the .env file. For Gmail, you MUST use an 'App Password'.")
        
        with col_btn2:
            if st.button("📥 Prepare Download Link", use_container_width=True):
                with st.spinner("Generating PDF..."):
                    pdf_path = generate_pdf_report(result, "analysis_report.pdf")
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download PDF Report",
                            data=f,
                            file_name="NYC_Business_Report.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )

# === NO RESULTS STATE ===
else:
    st.info("👈 Configure your business parameters in the sidebar and click **'Run Analysis'** to begin")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔬 How It Works
        
        This system uses a **multi-agent architecture** to analyze NYC data and recommend optimal business locations:
        
        1. **Planner Agent** — Interprets your input and creates an analysis plan
        2. **Data Collector Agent** — Fetches real-time data from NYC Open Data, Census, and MTA APIs
        3. **EDA Agent** — Performs exploratory analysis, computes scores, and generates visualizations
        4. **Hypothesis Agent** — Produces data-backed recommendations with evidence
        5. **Critic Agent** — Reviews the recommendation and suggests refinements
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Data Sources
        
        The system analyzes:
        
        - **Competition** — Number of existing businesses
        - **Income** — Median household income  
        - **Population** — Demand proxy
        - **Foot Traffic** — Subway ridership data
        - **Rent** — Cost indicators
        
        *All data is retrieved at runtime — no hardcoded datasets!*
        """)

st.sidebar.markdown("---")
st.sidebar.caption(f"UrbanSpot AI v1.0 · {datetime.now().year}")