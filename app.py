import streamlit as st
import pandas as pd
import time
from pathlib import Path
from io import BytesIO
from data_ingestion import load_data, save_data
from regex_engine import mask_deterministic

# Set page config
st.set_page_config(page_title="Celare - PII Detector & Masker", page_icon="🛡️", layout="centered")

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

# Center logo
left, center, right = st.columns([1, 2, 1])
with center:
    try:
        st.image("logo.png", width=150)
    except:
        pass

st.title("🛡️ Celare - PII Detector & Masker")
st.markdown("<br>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "PII Detector & Masker | Upload your file | 200MB per file • CSV, JSON, XLSX",
    type=["csv", "json", "xlsx"]
)

st.markdown("<p style='text-align: center; color: gray;'>v1.0.0 | Celare Project</p>", unsafe_allow_html=True)

# Data display area
if st.session_state.active_df is not None and st.session_state.processed:
    st.markdown("---")
    st.subheader("Data Preview")
    col_original, col_masked = st.columns(2)
    with col_original:
        st.markdown("**Original Data**")
        st.dataframe(st.session_state.active_df, use_container_width=True)
    with col_masked:
        st.markdown("**Masked Data**")
        st.dataframe(st.session_state.masked_df, use_container_width=True)
    
    st.markdown("---")
    st.subheader("PII Detection Summary")
    cols = st.columns(4)
    pii_types = ["email", "phone", "pan", "aadhaar"]
    display_names = ["Emails", "Phone Numbers", "PAN Cards", "Aadhaar Cards"]
    for i, (pii_type, display) in enumerate(zip(pii_types, display_names)):
        with cols[i]:
            st.metric(display, st.session_state.pii_counts[pii_type])
    
    st.markdown("---")
    col_export, col_report = st.columns(2)
    with col_export:
        output_format = st.selectbox("Select Export Format", ["CSV", "JSON", "XLSX"])
        if st.session_state.original_filename:
            base_name = Path(st.session_state.original_filename).stem
        else:
            base_name = "masked_data"
        
        output_filename = f"{base_name}_masked.{output_format.lower()}"
        temp_output = Path(f"temp_output.{output_format.lower()}")
        if save_data(st.session_state.masked_df, temp_output):
            with open(temp_output, "rb") as f:
                st.download_button("⬇️ Download Masked File", f, output_filename)
    with col_report:
        report_content = "# Celare PII Detection Verification Report\n\n"
        report_content += f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report_content += "## Summary\n"
        for pii_type, display in zip(pii_types, display_names):
            report_content += f"- {display}: {st.session_state.pii_counts[pii_type]}\n"
        report_content += f"\nTotal PII Found: {sum(st.session_state.pii_counts.values())}"
        st.download_button("📄 Download Verification Report", report_content, "verification_report.md", "text/markdown")

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
