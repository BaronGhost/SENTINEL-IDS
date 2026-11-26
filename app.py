import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from predictor import IDSPredictor
import os
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Sentinel AI | IDS", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
        /* Import Tech Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300..700&display=swap')
    
    /* Apply font to whole app */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Tech Grid Background */
    [data-testid="stAppViewContainer"] {
        background-color: #050533;
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 40px 40px;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #060D1F;
        border-right: 1px solid #1C2541;
    }

    /* Hero Text Styling */
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.1;
        margin-bottom: 0px;
    }
    .hero-title span {
        color: #4F8EF7;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #A0ABC0;
        margin-top: 15px;
        margin-bottom: 30px;
        line-height: 1.6;
    }

    /* The Tech Card */
    .tech-card {
        background-color: rgba(13, 22, 41, 0.7);
        border: 1px solid rgba(79, 142, 247, 0.3);
        border-radius: 16px;
        padding: 25px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        height: 100%;
    }
    .tech-card h4 {
        color: #FFFFFF;
        margin-top: 0;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .tech-card .status-badge {
        background-color: rgba(0, 240, 255, 0.1);
        color: #00F0FF;
        border: 1px solid #00F0FF;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 20px;
    }
    .tech-card p {
        color: #A0ABC0;
        font-size: 0.95rem;
        margin-bottom: 10px;
    }
    .tech-card .highlight {
        color: #FFA500;
        font-weight: bold;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        color: #00F0FF;
    }
    [data-testid="metric-container"] {
        background-color: #1C2541;
        border: 1px solid #3A506B;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* Insight Box */
    .insight-box {
        background-color: #1C2541;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00F0FF;
        height: 100%;
    }
    
    /* Primary Buttons (Scan & Download) */
    .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
        color: #0A1128 !important; 
        background-color: #00F0FF !important; 
        font-weight: 800;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {
        background-color: #00C0CC !important;
        box-shadow: 0 0 15px #00F0FF; 
    }
    
    /* Secondary Button (Scan Another) */
    .stButton > button[kind="secondary"] {
        color: #00F0FF !important;
        border: 2px solid #00F0FF !important;
        background-color: transparent !important;
        font-weight: bold;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #1C2541 !important;
        box-shadow: 0 0 10px #00F0FF;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("🛡️ SENTINEL IDS")
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Model Configuration")

# The Dropdown
model_choice = st.sidebar.radio(
    "Select Dataset Profile:",
    ("CIC-UNSW-NB15", "CIC-IDS2017")
)

dataset_key = 'unsw' if model_choice == "CIC-UNSW-NB15" else 'ids17'

# Dynamic Descriptions
st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 Dataset Info")

if dataset_key == 'unsw':
    st.sidebar.info(
        """
        **CIC-UNSW-NB15 (Modern Threats)**

        *Traffic Profile:* Captured in 2024, this dataset contains modern, complex attack vectors with a highly imbalanced class distribution. 

        *Detectable Attacks:* Fuzzers, Analysis, Backdoors, DoS, Exploits, Generic, Reconnaissance, Shellcode, and Worms.
        """
    )
else:
    st.sidebar.info(
        """
        **CIC-IDS2017 (Classic Threats)**

        *Traffic Profile:* Captured in 2017, this dataset represents a more traditional enterprise network with a massive volume of benign background traffic.

        *Detectable Attacks:* DDoS, PortScan, Brute Force (FTP/SSH), Web Attacks (SQLi, XSS), Botnet, and Infiltration.
        """
    )


@st.cache_resource
def get_predictor(dtype):
    return IDSPredictor(dataset_type=dtype)


try:
    predictor = get_predictor(dataset_key)
    st.sidebar.success(f"✅ {model_choice} Active")
except Exception as e:
    st.sidebar.error(f"❌ Error loading model: {e}")

# --- HERO SECTION ---
col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("""
        <p style="color: #56aeff; font-weight: 600; letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 10px;">
            NEXT-GEN CYBER DEFENSE
        </p>
        <h1 style="margin: 0; font-family: verdana; font-weight: 700; font-size: clamp(36px, 5vw, 48px); line-height: 1.05; letter-spacing: -0.02em">Sentinel IDS. <br> <span style="color: #56aeff">Hierarchical</span> Detection.</h1>
        <p class="hero-subtitle">
            A two-stage machine learning pipeline that filters benign traffic with surgical precision, 
            and identifies malicious attack vectors in real-time using CICFlowMeter data.
        </p>
    """, unsafe_allow_html=True)

with col2:
    # We dynamically update the card based on the selected model
    if dataset_key == 'unsw':
        model_name = "CIC-UNSW-NB15"
        attacks = "Fuzzers, Analysis, Backdoors, DoS, Exploits"
    else:
        model_name = "CIC-IDS2017"
        attacks = "DDoS, PortScan, Brute Force, Web Attacks, Botnet"

    st.markdown(f"""
        <div class="tech-card">
            <div class="status-badge">● SYSTEM ONLINE</div>
            <h4>Active Model: {model_name}</h4>
            <p><strong>Stage 1:</strong> Binary Triage (RF)</p>
            <p><strong>Stage 2:</strong> Multi-Class Detective (LGBM)</p>
            <hr style="border-color: rgba(255,255,255,0.1); margin: 15px 0;">
            <p><strong>Detectable Threats:</strong><br>{attacks}</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- INPUT SECTION ---
# (Your existing input method radio button and file uploader go here)
st.markdown("### Initiate Scan")
input_method = st.radio("Input Method:", ["Upload File", "Local File Path"], horizontal=True)
data_source = None

if input_method == "Upload File":
    uploaded_file = st.file_uploader(f"Upload CICFlowMeter CSV. Should match {model_name} feature schema", type=["csv"])
    if uploaded_file is not None:
        data_source = uploaded_file
else:
    file_path = st.text_input("Enter absolute path to CSV:", placeholder="C:/datasets/CICFlowMeter_out.csv")
    if file_path and os.path.exists(file_path):
        data_source = file_path

# --- PREDICTION LOGIC ---
if data_source is not None:
    if st.button("🚀 INITIATE SCAN", type="primary", use_container_width=True):
        # Clear previous session states
        st.session_state.pop('results', None)
        st.session_state.pop('csv_data', None)

        with st.spinner("Analyzing traffic behavior..."):
            # The chunked prediction
            results, error = predictor.predict_file(data_source, chunksize=50000)

            if error:
                st.error(f"**Prediction Error:** {error}")
            else:
                # Save results to session state so they persist on UI clicks
                st.session_state['results'] = results
                st.success("Analysis Complete!")

# --- DISPLAY RESULTS (If they exist in session state) ---
if 'results' in st.session_state:
    results = st.session_state['results']

    total_flows = len(results)
    attack_count = len(results[results['Verdict'] != 'BENIGN'])
    benign_count = total_flows - attack_count
    attack_percentage = (attack_count / total_flows) * 100 if total_flows > 0 else 0

    # Determine Threat Level
    if attack_percentage > 20:
        threat_level = "🔴 CRITICAL"
        threat_color = "#FF4B4B"
    elif attack_percentage > 5:
        threat_level = "🟠 HIGH"
        threat_color = "#FFA500"
    elif attack_count > 0:
        threat_level = "🟡 ELEVATED"
        threat_color = "#FFD700"
    else:
        threat_level = "🟢 LOW"
        threat_color = "#2ecc71"

    # --- 1. METRICS ---
    st.markdown("### 📊 Scan Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Flows", f"{total_flows:,}")
    col2.metric("Benign Traffic", f"{benign_count:,}")
    col3.metric("Attacks Detected", f"{attack_count:,}")
    col4.markdown(f"""
        <div style="background-color: #1C2541; padding: 15px; border-radius: 10px; border: 1px solid #3A506B; text-align: center;">
            <p style="margin:0; font-size: 14px; color: #E0E1DD;">THREAT LEVEL</p>
            <h2 style="margin:0; color: {threat_color}; text-shadow: 0 0 10px {threat_color};">{threat_level}</h2>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # --- 2. CHARTS & INSIGHTS ---
    st.markdown("### 🔍 Visual Analysis")

    # Row 1: Pie Chart & Text Insights
    row1_col1, row1_col2 = st.columns([1, 1])

    with row1_col1:
        fig_pie = px.pie(
            values=[benign_count, attack_count],
            names=['Benign', 'Attack'],
            title="Traffic Distribution",
            color_discrete_sequence=['#1C2541', '#00F0FF'],  # Dark blue vs Neon Cyan
            hole=0.6  # Makes it a donut chart (more modern)
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E0E1DD")
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with row1_col2:
        # Generate dynamic text insights
        if attack_count > 0:
            attack_df = results[results['Verdict'] != 'BENIGN']
            top_attack = attack_df['Verdict'].mode()[0]
            top_attack_count = attack_df['Verdict'].value_counts().iloc[0]

            st.markdown(f"""
            <div class="insight-box">
                <h3 style="color: #00F0FF; margin-top:0;">ML Insights</h3>
                <p>Our Stage 1 Binary Triage successfully filtered out <b>{benign_count:,}</b> benign flows.</p>
                <p>Stage 2 identified <b>{attack_count:,}</b> malicious flows, making up <b>{attack_percentage:.2f}%</b> of total traffic.</p>
                <hr style="border-color: #3A506B;">
                <p>⚠️ <b>Primary Threat:</b> <span style="color:#FF4B4B; font-weight:bold;">{top_attack}</span></p>
                <p>The model detected <b>{top_attack_count:,}</b> instances of this attack type. Immediate investigation of these flows is recommended.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="insight-box">
                <h3 style="color: #00F0FF; margin-top:0;">AI Insights</h3>
                <p>✅ No malicious traffic detected in this capture.</p>
                <p>The network appears to be operating under normal parameters based on the provided flow metadata.</p>
            </div>
            """, unsafe_allow_html=True)

    # Row 2: Bar Chart (Full Width)
    if attack_count > 0:
        attack_df = results[results['Verdict'] != 'BENIGN']
        attack_counts = attack_df['Verdict'].value_counts().reset_index()
        attack_counts.columns = ['Attack Type', 'Count']

        fig_bar = px.bar(
            attack_counts,
            x='Attack Type',
            y='Count',
            title="Attack Type Distribution",
            color='Count',
            color_continuous_scale=['#1C2541', '#00F0FF']  # Gradient from dark blue to cyan
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E0E1DD"),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # --- 3. DATA PREVIEW & DOWNLOAD ---
    st.markdown("### 📄 Detailed Results")

    # Only show rows with attacks in the preview (or show top 100 if no attacks)
    if attack_count > 0:
        attack_results = results[results['Verdict'] != 'BENIGN']
        st.dataframe(attack_results[['Verdict', 'Attack_Probability']].head(100), use_container_width=True)
    else:
        st.dataframe(results[['Verdict', 'Attack_Probability']].head(100), use_container_width=True)

    # TWO-STEP DOWNLOAD (FILTERED FOR MEMORY SAFETY)
    st.markdown("#### Export Threat Report")
    st.markdown(
        "To prevent server crashes, we only export the **malicious flows (Alerts)**. Benign traffic is omitted.")

    if st.button("Prepare Threat Report (CSV)"):
        with st.spinner("Compiling threat report..."):
            if attack_count > 0:
                export_df = results[results['Verdict'] != 'BENIGN']
            else:
                export_df = results  # If no attacks, just export the small batch

            # Convert to CSV in memory (now much smaller)
            st.session_state['csv_data'] = export_df.to_csv(index=False).encode('utf-8')
            st.success(f"Threat Report Ready! ({len(export_df):,} flows)")

    if 'csv_data' in st.session_state:
        st.download_button(
            label="📥 DOWNLOAD THREAT REPORT",
            data=st.session_state['csv_data'],
            file_name='sentinel_ids_alerts.csv',
            mime='text/csv',
            type="primary"
        )

    # --- 4. RESET BUTTON ---
    st.markdown("---")
    if st.button("🔄 Scan Another File", type="secondary", use_container_width=True):
        st.session_state.pop('results', None)
        st.session_state.pop('csv_data', None)
        st.rerun()