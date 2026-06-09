import streamlit as st
import pandas as pd
import time
from pathlib import Path
from datetime import datetime
from data_ingestion import load_data, save_data
from regex_engine import mask_deterministic, PII_PATTERNS

# Page config
st.set_page_config(page_title="Celare - PII Detector & Masker", page_icon="🛡️", layout="wide")

# Initialize session state
if "active_df" not in st.session_state:
    st.session_state.active_df = None
if "masked_df" not in st.session_state:
    st.session_state.masked_df = None
if "pii_counts" not in st.session_state:
    st.session_state.pii_counts = {}
if "original_filename" not in st.session_state:
    st.session_state.original_filename = None
if "processed" not in st.session_state:
    st.session_state.processed = False
if "history" not in st.session_state:
    st.session_state.history = []
if "selected_pii_type" not in st.session_state:
    st.session_state.selected_pii_type = None
if "temp_masked_files" not in st.session_state:
    st.session_state.temp_masked_files = {}

# ------------------------------
# Sidebar
# ------------------------------
with st.sidebar:
    # Logo
    try:
        st.image("logo.png")
    except Exception as e:
        pass
    
    st.markdown("---")
    
    # Large file uploader
    uploaded_file = st.file_uploader(
        "Upload your file",
        type=["csv", "json", "xlsx"],
        help="Supports CSV, JSON, and XLSX formats • Drag and drop for easy upload",
        label_visibility="visible"
    )
    
    st.markdown("---")
    
    # Sidebar footer
    st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>v1.0.0 | Kinetic Prism</p>", unsafe_allow_html=True)

# ------------------------------
# Main Panel
# ------------------------------
st.title("🛡️ Celare - PII Detector & Masker")

# Handle file upload and processing
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
            
            # Add to history
            history_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "filename": uploaded_file.name,
                "counts": st.session_state.pii_counts.copy(),
                "file_ext": ext
            }
            # Save masked file temp copy for history
            temp_masked_path = Path(f"temp_history_{len(st.session_state.history)}{ext}")
            if save_data(st.session_state.masked_df, temp_masked_path):
                st.session_state.temp_masked_files[len(st.session_state.history)] = temp_masked_path
                history_entry["temp_path"] = temp_masked_path
                st.session_state.history.append(history_entry)
            
            # Reset selection on new upload
            st.session_state.selected_pii_type = None
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

# ------------------------------
# Tabs
# ------------------------------
tab1, tab2 = st.tabs(["Dashboard", "History"])

# ------------------------------
# Tab 1: Dashboard
# ------------------------------
with tab1:
    if st.session_state.active_df is not None and st.session_state.processed:
        # Metrics and Analytics
        st.subheader("PII Detection Overview")
        
        # Metrics row with clickable buttons
        pii_types = ["email", "phone", "pan", "aadhaar"]
        display_names = ["Emails", "Phone Numbers", "PAN Cards", "Aadhaar Cards"]
        metric_cols = st.columns(4)
        
        for i, (pii_type, display) in enumerate(zip(pii_types, display_names)):
            with metric_cols[i]:
                count = st.session_state.pii_counts.get(pii_type, 0)
                # Button with st.button, which sets session state
                if st.button(f"{count} {display}", key=f"btn_{pii_type}", use_container_width=True):
                    st.session_state.selected_pii_type = pii_type
        
        # Bar chart
        st.subheader("Masked Entity Distribution")
        chart_data = pd.DataFrame.from_dict(st.session_state.pii_counts, orient='index', columns=['Count'])
        st.bar_chart(chart_data, color="#00FF88")
        
        st.markdown("---")
        
        # Dataframe display with optional filtering
        st.subheader("Data Preview")
        
        # Filter dataframe based on selected pii type
        display_df = st.session_state.masked_df.copy()
        
        if st.session_state.selected_pii_type:
            st.info(f"Showing entries with {display_names[pii_types.index(st.session_state.selected_pii_type)]} (highlighted if masked)")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Original Data")
            st.dataframe(st.session_state.active_df, use_container_width=True)
        
        with col2:
            st.markdown("### Masked Data")
            st.dataframe(display_df, use_container_width=True)
        
        st.markdown("---")
        
        # Download options
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
            # Verification report
            report_content = "# Celare PII Detection Verification Report\n\n"
            report_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            report_content += "## Summary\n"
            for pii_type, display in zip(pii_types, display_names):
                report_content += f"- {display}: {st.session_state.pii_counts.get(pii_type, 0)}\n"
            report_content += f"\nTotal PII Found: {sum(st.session_state.pii_counts.values())}"
            st.download_button("📄 Download Verification Report", report_content, "verification_report.md", "text/markdown", use_container_width=True)

# ------------------------------
# Tab 2: History
# ------------------------------
with tab2:
    st.subheader("Processing History")
    if len(st.session_state.history) == 0:
        st.info("No processing history yet. Upload and mask a file to get started!")
    else:
        for idx, entry in enumerate(reversed(st.session_state.history)):
            with st.container():
                st.markdown(f"**File:** {entry['filename']} • **Timestamp:** {entry['timestamp']}")
                
                # Counts summary
                entry_cols = st.columns(4)
                for i, (pii_type, display) in enumerate(zip(pii_types, display_names)):
                    entry_cols[i].metric(display, entry['counts'].get(pii_type, 0))
                
                # Download button for past masked file
                if "temp_path" in entry:
                    if entry['temp_path'].exists():
                        base_name = Path(entry['filename']).stem
                        ext = entry['file_ext']
                        download_name = f"{base_name}_masked{ext}"
                        with open(entry['temp_path'], "rb") as f:
                            st.download_button(f"⬇️ Download {download_name}", f, download_name, key=f"hist_dl_{idx}")
                
                st.markdown("---")

# ------------------------------
# Cleanup temporary files
# ------------------------------
def cleanup_temp_files():
    files_to_remove = [
        "temp_output.csv", "temp_output.json", "temp_output.xlsx",
        "temp_upload.csv", "temp_upload.json", "temp_upload.xlsx"
    ]
    for f in files_to_remove:
        path = Path(f)
        if path.exists():
            path.unlink(missing_ok=True)

cleanup_temp_files()
