import streamlit as st
import pandas as pd
import time
from datetime import datetime
from pathlib import Path
from data_ingestion import load_data, save_data
from regex_engine import mask_deterministic
from llm_engine import mask_full_pipeline, OLLAMA_AVAILABLE

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
if "file_ext" not in st.session_state:
    st.session_state.file_ext = ".csv"
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
if "use_ollama" not in st.session_state:
    st.session_state.use_ollama = False

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
        "Upload your file",
        type=["csv", "json", "xlsx"]
    )
    
    if uploaded_file is not None:
        temp_path = Path(f"temp_upload{Path(uploaded_file.name).suffix}")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        load_result = load_data(temp_path)
        if load_result:
            st.session_state.active_df, st.session_state.file_ext = load_result
            st.session_state.file_uploaded = True
            st.success(f"File loaded successfully! ({st.session_state.file_ext})")
        else:
            st.error("Failed to load file")
    else:
        if st.session_state.active_df is None:
            mock_path = Path("sample_data/mock_dataset.csv")
            if mock_path.exists():
                load_result = load_data(mock_path)
                if load_result:
                    st.session_state.active_df, st.session_state.file_ext = load_result
        st.info("Using sample mock dataset")
    
    # Ollama option
    st.markdown("---")
    if OLLAMA_AVAILABLE:
        st.session_state.use_ollama = st.checkbox(
            "Enable Indirect PII Detection (Ollama)",
            value=False,
            help="Uses local LLM to detect indirect PII combinations (slower)"
        )
    else:
        st.warning("Ollama not available. Indirect PII detection disabled.")
    
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
                
                if st.session_state.use_ollama and OLLAMA_AVAILABLE:
                    st.session_state.masked_df, st.session_state.pii_counts = mask_full_pipeline(st.session_state.active_df)
                else:
                    st.session_state.masked_df, st.session_state.pii_counts = mask_deterministic(st.session_state.active_df)
                
                # Add to processing history
                total_masked = sum(st.session_state.pii_counts.values())
                st.session_state.processing_history.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "filename": uploaded_file.name if uploaded_file else "mock_dataset.csv",
                    "total_masked": total_masked,
                    "emails": st.session_state.pii_counts.get("email", 0),
                    "phones": st.session_state.pii_counts.get("phone", 0),
                    "pans": st.session_state.pii_counts.get("pan", 0),
                    "aadhaars": st.session_state.pii_counts.get("aadhaar", 0),
                    "indirect_pii": st.session_state.pii_counts.get("indirect_pii_combinations", 0)
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
            
            cols = st.columns(6)
            total_masked = sum(st.session_state.pii_counts.values())
            cols[0].metric("Total PII Masked", total_masked)
            cols[1].metric("Emails", st.session_state.pii_counts.get("email", 0))
            cols[2].metric("Phones", st.session_state.pii_counts.get("phone", 0))
            cols[3].metric("PAN Cards", st.session_state.pii_counts.get("pan", 0))
            cols[4].metric("Aadhaar Cards", st.session_state.pii_counts.get("aadhaar", 0))
            cols[5].metric("Indirect PII", st.session_state.pii_counts.get("indirect_pii_combinations", 0))
            
            # Chart
            st.subheader("PII Type Distribution")
            chart_data = pd.DataFrame.from_dict(st.session_state.pii_counts, orient='index', columns=['count'])
            st.bar_chart(chart_data, color="#00FF88")
            
            # Download button
            st.markdown("---")
            if uploaded_file:
                download_name = f"masked_{uploaded_file.name}"
            else:
                download_name = f"masked_mock_dataset{st.session_state.file_ext}"
            
            temp_output = Path(f"temp_output{st.session_state.file_ext}")
            if save_data(st.session_state.masked_df, temp_output):
                with open(temp_output, "rb") as f:
                    st.download_button(
                        f"⬇️ Download Masked Dataset ({st.session_state.file_ext})",
                        f,
                        download_name
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
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if prompt := st.chat_input("Ask about your dataset (e.g., 'Why was line 5 redacted?')"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                full_response = ""
                
                if "line" in prompt.lower() and "redacted" in prompt.lower():
                    full_response = "That line was redacted because it contained one or more PII elements that matched our deterministic regex patterns or indirect PII combinations detected by our LLM agent."
                elif "list" in prompt.lower() and "pii" in prompt.lower():
                    counts = st.session_state.pii_counts if st.session_state.pii_counts else {}
                    full_response = f"Here's the breakdown of discovered PII:\n"
                    for key, val in counts.items():
                        full_response += f"- {key.replace('_', ' ').title()}: {val}\n"
                elif "how" in prompt.lower() and "mask" in prompt.lower():
                    full_response = "Celare uses a hybrid approach: Phase 1 is high-speed deterministic regex matching for common Indian PII patterns, and Phase 2 uses an Ollama LLM agent loop for contextual indirect PII detection!"
                else:
                    full_response = "I'm here to help with your dataset! Try asking about specific lines, PII types, or how the masking process works."
                
                for i in range(len(full_response)):
                    time.sleep(0.01)
                    response_placeholder.markdown(full_response[:i+1])
                
                response_placeholder.markdown(full_response)
            
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
        
        total_runs = len(st.session_state.processing_history)
        total_all_masked = sum([h['total_masked'] for h in st.session_state.processing_history])
        
        col_sum1, col_sum2 = st.columns(2)
        col_sum1.metric("Total Processing Runs", total_runs)
        col_sum2.metric("Total PII Masked Across All Runs", total_all_masked)
    else:
        st.info("No processing history yet! Run masking in the first tab to start tracking.")
