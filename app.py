import streamlit as st
import pandas as pd
import time
import base64
from pathlib import Path
from data_ingestion import load_data, save_data
from regex_engine import mask_deterministic

# Set page config
st.set_page_config(page_title="Celare - PII Detector & Masker", page_icon="🛡️", layout="wide")

# Custom modern CSS
st.markdown("""
    <style>
        /* Main background */
        .main {
            background: linear-gradient(135deg, #0E1117 0%, #1A1F2E 100%);
        }
        
        /* Hide default streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Card styling */
        .card {
            background-color: #161A23;
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        
        /* Logo container */
        .logo-container {
            text-align: center;
            margin-bottom: 32px;
        }
        
        .logo-container img {
            border-radius: 50%;
            box-shadow: 0 4px 20px rgba(0, 255, 136, 0.2);
        }
        
        /* Uploader styling */
        .stFileUploader > div {
            background-color: #1E2330;
            border: 2px dashed #00FF88;
            border-radius: 12px;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #00FF88 0%, #00CC6F 100%);
            color: #0E1117;
            border-radius: 10px;
            border: none;
            font-weight: 600;
            padding: 10px 24px;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #00CC6F 0%, #00AA5A 100%);
        }
        
        /* Metrics */
        .metric-card {
            background-color: #1E2330;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid #2A3040;
        }
        
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            color: #00FF88;
        }
        
        .metric-label {
            font-size: 14px;
            color: #8B949E;
            margin-top: 4px;
        }
        
        /* Headers */
        h1 {
            background: linear-gradient(135deg, #FFFFFF 0%, #00FF88 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "active_df" not in st.session_state:
    st.session_state.active_df = None
if "masked_df" not in st.session_state:
    st.session_state.masked_df = None
if "pii_counts" not in st.session_state:
    st.session_state.pii_counts = None
if "original_filename" not in st.session_state:
    st.session_state.original_filename = None
if "processed" not in st.session_state:
    st.session_state.processed = False

# Layout container
main_col, _, _ = st.columns([2, 1, 1])
with main_col:
    # Center logo (circle)
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    try:
        # Load and encode logo to base64 for circular rendering
        logo_path = Path("logo.png")
        if logo_path.exists():
            with open(logo_path, "rb") as img_file:
                base64_img = base64.b64encode(img_file.read()).decode()
            st.markdown(f'<img src="data:image/png;base64,{base64_img}" width="180">', unsafe_allow_html=True)
    except Exception as e:
        st.image("logo.png", width=180)
    st.markdown("</div>", unsafe_allow_html=True)

    # Title
    st.markdown("<h1 style='text-align: center; margin-bottom: 8px;'>🛡️ Celare - PII Detector & Masker</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8B949E; margin-bottom: 40px;'>Protect your sensitive data with ease</p>", unsafe_allow_html=True)

    # File uploader card
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload your file",
        type=["csv", "json", "xlsx"],
        help="200MB per file • Supports CSV, JSON, and XLSX formats"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("<p style='text-align: center; color: #5C6370; font-size: 13px;'>v1.0.0 | Celare Project</p>", unsafe_allow_html=True)

# Data processing and display
if st.session_state.active_df is not None and st.session_state.processed:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Metrics row
    st.subheader("PII Detection Summary")
    metric_cols = st.columns(4)
    pii_types = ["email", "phone", "pan", "aadhaar"]
    display_names = ["Emails", "Phone Numbers", "PAN Cards", "Aadhaar Cards"]
    for i, (pii_type, display) in enumerate(zip(pii_types, display_names)):
        with metric_cols[i]:
            st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{st.session_state.pii_counts[pii_type]}</div>
                    <div class='metric-label'>{display}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Data preview
    preview_col1, preview_col2 = st.columns(2)
    with preview_col1:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Original Data")
            st.dataframe(st.session_state.active_df, use_container_width=True, height=400)
            st.markdown("</div>", unsafe_allow_html=True)
    with preview_col2:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Masked Data")
            st.dataframe(st.session_state.masked_df, use_container_width=True, height=400)
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Export card
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Download Options")
    export_col1, export_col2 = st.columns(2)
    with export_col1:
        output_format = st.selectbox("Select Export Format", ["CSV", "JSON", "XLSX"])
        if st.session_state.original_filename:
            base_name = Path(st.session_state.original_filename).stem
        else:
            base_name = "masked_data"
        
        output_filename = f"{base_name}_masked.{output_format.lower()}"
        temp_output = Path(f"temp_output.{output_format.lower()}")
        if save_data(st.session_state.masked_df, temp_output):
            with open(temp_output, "rb") as f:
                st.download_button("⬇️ Download Masked File", f, output_filename, use_container_width=True)
    with export_col2:
        report_content = "# Celare PII Detection Verification Report\n\n"
        report_content += f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report_content += "## Summary\n"
        for pii_type, display in zip(pii_types, display_names):
            report_content += f"- {display}: {st.session_state.pii_counts[pii_type]}\n"
        report_content += f"\nTotal PII Found: {sum(st.session_state.pii_counts.values())}"
        st.download_button("📄 Download Verification Report", report_content, "verification_report.md", "text/markdown", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Handle file upload
if uploaded_file is not None:
    temp_path = Path(f"temp_upload{Path(uploaded_file.name).suffix}")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    load_result = load_data(temp_path)
    if load_result:
        st.session_state.active_df, ext = load_result
        st.session_state.original_filename = uploaded_file.name
        with st.spinner("Masking PII..."):
            time.sleep(0.5)
            st.session_state.masked_df, st.session_state.pii_counts = mask_deterministic(st.session_state.active_df)
            st.session_state.processed = True
        st.rerun()
    else:
        st.error("Failed to load file")
else:
    if not st.session_state.processed:
        mock_path = Path("sample_data/mock_dataset.csv")
        if mock_path.exists():
            load_result = load_data(mock_path)
            if load_result:
                st.session_state.active_df, ext = load_result
                st.session_state.masked_df, st.session_state.pii_counts = mask_deterministic(st.session_state.active_df)
                st.session_state.processed = True
                st.session_state.original_filename = "mock_dataset.csv"

# Cleanup temp files
if Path("temp_output.csv").exists(): Path("temp_output.csv").unlink(missing_ok=True)
if Path("temp_output.json").exists(): Path("temp_output.json").unlink(missing_ok=True)
if Path("temp_output.xlsx").exists(): Path("temp_output.xlsx").unlink(missing_ok=True)
if Path("temp_upload.csv").exists(): Path("temp_upload.csv").unlink(missing_ok=True)
if Path("temp_upload.json").exists(): Path("temp_upload.json").unlink(missing_ok=True)
if Path("temp_upload.xlsx").exists(): Path("temp_upload.xlsx").unlink(missing_ok=True)
