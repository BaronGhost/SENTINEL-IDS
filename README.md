# 🛡️ Sentinel IDS: Hierarchical Intrusion Detection System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange)
![LightGBM](https://img.shields.io/badge/LightGBM-4.0%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Sentinel IDS** is a machine learning-powered Network Intrusion Detection System (NIDS) designed to analyze CICFlowMeter CSV outputs. It utilizes a **two-stage hierarchical architecture** to efficiently filter out benign traffic and classify specific network attacks with high precision.

## 🧠 Architecture

Traditional multi-class models often fail on imbalanced network datasets because benign traffic severely outnumbers malicious traffic. Sentinel AI solves this using a two-stage pipeline:

1. **Stage 1: Binary Triage (Benign vs. Attack)**
   - A highly optimized Random Forest model trained on the top 30 behavioral features.
   - Achieves **~99% accuracy** and drastically reduces false positives.
2. **Stage 2: Multi-Class Detective (Attack Type)**
   - A LightGBM model that only runs if Stage 1 detects an attack.
   - Classifies the specific attack (e.g., DDoS, Exploits, Fuzzers, Reconnaissance).

### Supported Datasets
The application includes pre-trained models for two industry-standard datasets:
- **CIC-UNSW-NB15** (Modern, highly imbalanced dataset)
- **CIC-IDS2017** (Classic, highly popular dataset)

## 🚀 Features

- **Interactive UI:** Built with Streamlit and Plotly for a sleek, dark-mode "Cyber AI" aesthetic.
- **Memory Safe:** Processes huge files (1.8GB+) using **chunked reading** to prevent RAM crashes.
- **Dynamic Insights:** Automatically generates threat-level indicators and AI insights based on the uploaded traffic.
- **Downloadable Results:** Export the analyzed CSV with new `Verdict` and `Attack_Probability` columns.

## 📁 Repository Structure

- **app.py:** The Streamlit frontend and UI logic.
- **predictor.py:** The backend engine handling preprocessing, model loading, and chunking.
- **Models:** Directory containing serialized .joblib files for both datasets.
- **Notebooks:** Jupyter Notebooks used to train, tune, and evaluate the models.

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/BaronGhost/SENTINEL-IDS.git
   cd SENTINEL-IDS
   
2. **Run the Application**
   ```bash
   python3 -m venv venv
   .venv/Scripts/Activate.ps1
  
   pip install -r requirements.txt
   streamlit run app.py 
