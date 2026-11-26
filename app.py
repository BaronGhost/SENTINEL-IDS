import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from predictor import IDSPredictor
import os
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Sentinel AI | IDS", page_icon="🛡️", layout="wide")

# --- CUSTOM CSS FOR AI VIBE ---
st.markdown("""
<style>
    /* Glowing title */
    .title-text {
        color: #00F0FF;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
        font-weight: 800;
        letter-spacing: 2px;
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
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #060D1F;
        border-right: 1px solid #1C2541;
    }
    /* Insight Box */
    .insight-box {
        background-color: #1C2541;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00F0FF;
        height: 100%;
    }

    /* --- BUTTON STYLING --- */
    /* Primary Buttons (Scan & Download) */
    .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
        color: #0A1128 !important; /* Dark blue text for contrast */
        background-color: #00F0FF !important; /* Cyan background */
        font-weight: 800;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {
        background-color: #00C0CC !important;
        box-shadow: 0 0 15px #00F0FF; /* Glowing effect on hover */
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
st.sidebar.markdown("**Model Selection**")
model_choice = st.sidebar.radio("Select Dataset:", ("CIC-UNSW-NB15", "CIC-IDS2017"))
dataset_key = 'unsw' if model_choice == "CIC-UNSW-NB15" else 'ids17'


@st.cache_resource
def get_predictor(dtype):
    return IDSPredictor(dataset_type=dtype)


try:
    predictor = get_predictor(dataset_key)
    st.sidebar.success(f"✅ {model_choice} Active")
except Exception as e:
    st.sidebar.error(f"❌ Error loading model: {e}")

# --- MAIN UI ---
st.markdown("<h1 class='title-text'>🛡️ SENTINEL IDS: HIERARCHICAL DETECTION</h1>", unsafe_allow_html=True)
st.markdown("Advanced network traffic analysis powered by two-stage machine learning.")
st.markdown("---")

# Input Method
input_method = st.radio("Input Method:", ["Upload File", "Local File Path"], horizontal=True)
data_source = None

if input_method == "Upload File":
    uploaded_file = st.file_uploader("Upload CICFlowMeter CSV", type=["csv"])
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
    st.dataframe(results[['Verdict', 'Attack_Probability']].head(100), use_container_width=True)

    # TWO-STEP DOWNLOAD TO PREVENT UI FREEZE
    st.markdown("#### Export Data")
    st.markdown("Generating the full CSV may take a moment depending on file size.")

    if st.button("Prepare Full CSV for Download"):
        with st.spinner("Compiling 1.8GB CSV... (Please wait)"):
            # Convert to CSV once and store in session state
            st.session_state['csv_data'] = results.to_csv(index=False).encode('utf-8')
            st.success("CSV Ready!")

    if 'csv_data' in st.session_state:
        st.download_button(
            label="📥 CLICK HERE TO DOWNLOAD",
            data=st.session_state['csv_data'],
            file_name='sentinel_ai_results.csv',
            mime='text/csv',
            type="primary"
        )

    # --- 4. RESET BUTTON ---
    st.markdown("---")
    if st.button("🔄 Scan Another File", type="secondary", use_container_width=True):
        # Clear the stored results and CSV data from memory
        st.session_state.pop('results', None)
        st.session_state.pop('csv_data', None)
        # Rerun the app to reset the UI back to the uploader
        st.rerun()