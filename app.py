import streamlit as st
import pandas as pd
import time
from datetime import datetime
from data_ingestion import read_csv_safe, write_csv_safe
from regex_engine import mask_deterministic

# Set page config with dark theme
st.set_page_config(
    page_title="Celare - PII Detector & Masker",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown(
    """
    <style>
    /* Main background */
    .main {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #161A23;
    }
    /* Logo container */
    .sidebar-logo {
        text-align: center;
        margin-bottom: 20px;
        padding-top: 10px;
    }
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1E2330;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #00FF88;
    }
    /* PII warning highlight */
    .pii-warning {
        color: #FF4B4B;
        font-weight: bold;
    }
    /* Success green */
    .success-text {
        color: #00FF88;
    }
    /* Info blue */
    .info-text {
        color: #58A6FF;
    }
    /* Buttons */
    .stButton > button {
        background-color: #00FF88;
        color: #0E1117;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #00CC6F;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if "active_df" not in st.session_state:
    st.session_state.active_df = None
if "masked_df" not in st.session_state:
    st.session_state.masked_df = None
if "pii_counts" not in st.session_state:
    st.session_state.pii_counts = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "processing_history" not in st.session_state:
    st.session_state.processing_history = []
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.title("🛡️ Celare")
    st.markdown('</div>', unsafe_allow_html=True)
    st.subheader("PII Detector & Masker")
    st.markdown("---")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload your CSV file",
        type=["csv"]
    )
    
    if uploaded_file is not None:
        with open("temp_upload.csv", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.active_df = read_csv_safe("temp_upload.csv")
        st.session_state.file_uploaded = True
        st.success("File loaded successfully!")
    else:
        # Load mock dataset
        if st.session_state.active_df is None:
            st.session_state.active_df = read_csv_safe("sample_data/mask_dataset.csv")
            if st.session_state.active_df is None:
                st.session_state.active_df = read_csv_safe("sample_data/mock_dataset.csv")
        st.info("Using sample mock dataset")
    
    st.markdown("---")
    st.caption("v1.0.0 | Celare Project")

# Main tabs
tab1, tab2, tab3 = st.tabs(["🛡️ Masking Engine", "💬 Celare Chat Agent", "🕒 Audit & File History"])

# ------------------------------
# Tab 1: Masking Engine
# ------------------------------
with tab1:
    st.title("🛡️ Masking Engine")
    st.markdown("---")
    
    if st.session_state.active_df is not None:
        # Configuration
        col_config1, col_config2 = st.columns([1, 2])
        with col_config1:
            st.subheader("Configuration")
            process_button = st.button("🚀 Run PII Masking")
        
        # Progress section
        status_placeholder = st.empty()
        progress_bar = st.progress(0)
        
        # Process data on button click
        if process_button:
            with st.spinner("Processing data..."):
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                st.session_state.masked_df, st.session_state.pii_counts = mask_deterministic(st.session_state.active_df)
                
                # Add to processing history
                st.session_state.processing_history.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "filename": uploaded_file.name if uploaded_file else "mock_dataset.csv",
                    "total_masked": sum(st.session_state.pii_counts.values()),
                    "emails": st.session_state.pii_counts['email'],
                    "phones": st.session_state.pii_counts['phone'],
                    "pans": st.session_state.pii_counts['pan'],
                    "aadhaars": st.session_state.pii_counts['aadhaar']
                })
                
                status_placeholder.markdown('<p class="success-text">✅ Processing complete!</p>', unsafe_allow_html=True)
                time.sleep(1)
        
        # Side-by-side comparison
        st.markdown("---")
        st.subheader("Data Comparison")
        
        col_orig, col_masked = st.columns(2)
        with col_orig:
            st.markdown("### Original Dataset")
            st.dataframe(st.session_state.active_df, use_container_width=True)
        
        with col_masked:
            st.markdown("### Masked Dataset")
            if st.session_state.masked_df is not None:
                st.dataframe(st.session_state.masked_df, use_container_width=True)
            else:
                st.info("Run masking to view masked data")
        
        # Metrics
        if st.session_state.pii_counts is not None:
            st.markdown("---")
            st.subheader("Masking Statistics")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            total_masked = sum(st.session_state.pii_counts.values())
            col1.metric("Total PII Masked", total_masked)
            col2.metric("Emails", st.session_state.pii_counts['email'])
            col3.metric("Phones", st.session_state.pii_counts['phone'])
            col4.metric("PAN Cards", st.session_state.pii_counts['pan'])
            col5.metric("Aadhaar Cards", st.session_state.pii_counts['aadhaar'])
            
            # Chart
            st.subheader("PII Type Distribution")
            chart_data = pd.DataFrame.from_dict(st.session_state.pii_counts, orient='index', columns=['count'])
            st.bar_chart(chart_data, color="#00FF88")
            
            # Download button
            st.markdown("---")
            csv = st.session_state.masked_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⬇️ Download Masked Dataset",
                csv,
                "masked_dataset.csv",
                "text/csv",
                key='download-csv'
            )
    else:
        st.error("No data loaded!")

# ------------------------------
# Tab 2: Celare Chat Agent
# ------------------------------
with tab2:
    st.title("💬 Celare Chat Agent")
    st.markdown("---")
    
    if st.session_state.file_uploaded or (st.session_state.active_df is not None):
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about your dataset (e.g., 'Why was line 5 redacted?')"):
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate fake AI response
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                full_response = ""
                
                # Fake responses based on prompt
                if "line" in prompt.lower() and "redacted" in prompt.lower():
                    full_response = "That line was redacted because it contained one or more PII elements (email, phone, PAN, or Aadhaar number) that matched our deterministic regex patterns."
                elif "list" in prompt.lower() and "pii" in prompt.lower():
                    counts = st.session_state.pii_counts if st.session_state.pii_counts else {'email': 0, 'phone': 0, 'pan': 0, 'aadhaar': 0}
                    full_response = f"Here's the breakdown of discovered PII:\n- Emails: {counts['email']}\n- Phones: {counts['phone']}\n- PAN Cards: {counts['pan']}\n- Aadhaar Cards: {counts['aadhaar']}"
                elif "how" in prompt.lower() and "mask" in prompt.lower():
                    full_response = "Celare uses a hybrid approach: Phase 1 is high-speed deterministic regex matching for common Indian PII patterns, and Phase 2 (coming soon) will use an LLM agent loop for contextual analysis!"
                else:
                    full_response = "I'm here to help with your dataset! Try asking about specific lines, PII types, or how the masking process works."
                
                # Simulate streaming
                for i in range(len(full_response)):
                    time.sleep(0.01)
                    response_placeholder.markdown(full_response[:i+1])
                
                response_placeholder.markdown(full_response)
            
            # Add assistant message to history
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})
    else:
        st.info("Please upload a file or use the sample dataset to chat with the Celare agent!")

# ------------------------------
# Tab 3: Audit & File History
# ------------------------------
with tab3:
    st.title("🕒 Audit & File History")
    st.markdown("---")
    
    if len(st.session_state.processing_history) > 0:
        history_df = pd.DataFrame(st.session_state.processing_history)
        st.dataframe(history_df, use_container_width=True, hide_index=True)
        
        # Summary metrics
        total_runs = len(st.session_state.processing_history)
        total_all_masked = sum([h['total_masked'] for h in st.session_state.processing_history])
        
        col_sum1, col_sum2 = st.columns(2)
        col_sum1.metric("Total Processing Runs", total_runs)
        col_sum2.metric("Total PII Masked Across All Runs", total_all_masked)
    else:
        st.info("No processing history yet! Run masking in the first tab to start tracking.")
