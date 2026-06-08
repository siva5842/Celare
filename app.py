import streamlit as st
import pandas as pd
import time
from data_ingestion import read_csv_safe, write_csv_safe
from regex_engine import mask_deterministic

# Set page config
st.set_page_config(
    page_title="Celare - PII Detector & Masker",
    page_icon="🛡️",
    layout="wide"
)

# Sidebar
st.sidebar.title("🛡️ Celare")
st.sidebar.markdown("### PII Detector & Masker")

uploaded_file = st.sidebar.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    with open("temp_upload.csv", "wb") as f:
        f.write(uploaded_file.getbuffer())
    df = read_csv_safe("temp_upload.csv")
else:
    df = read_csv_safe("sample_data/mock_dataset.csv")

st.sidebar.markdown("---")
st.sidebar.subheader("Processing Status")
status_placeholder = st.sidebar.empty()
progress_bar = st.sidebar.progress(0)

# Main content
st.title("🛡️ Celare - PII Detector & Masker")
st.markdown("---")

if df is not None:
    # Step 1: Show original data
    st.header("1. Original Dataset")
    st.dataframe(df, use_container_width=True)

    # Step 2: Process data with loading state
    st.markdown("---")
    st.header("2. PII Processing")
    
    with st.spinner("Processing data..."):
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        
        masked_df, counts = mask_deterministic(df)
        status_placeholder.success("✅ Processing complete!")
    
    # Step 3: Show masked data
    st.markdown("---")
    st.header("3. Masked Dataset")
    st.dataframe(masked_df, use_container_width=True)

    # Step 4: Show metrics
    st.markdown("---")
    st.header("4. Masking Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    total_masked = sum(counts.values())
    col1.metric("Total PII Masked", total_masked)
    col2.metric("Emails", counts['email'])
    col3.metric("Phones", counts['phone'])
    col4.metric("PAN Cards", counts['pan'])
    col5, col6 = st.columns(2)
    col5.metric("Aadhaar Cards", counts['aadhaar'])
    
    # Chart
    st.subheader("PII Type Distribution")
    chart_data = pd.DataFrame.from_dict(counts, orient='index', columns=['count'])
    st.bar_chart(chart_data)

    # Download button
    st.markdown("---")
    csv = masked_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Download Masked Dataset",
        csv,
        "masked_dataset.csv",
        "text/csv",
        key='download-csv'
    )

else:
    st.error("Error loading data!")
