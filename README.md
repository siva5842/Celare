# Celare (PII Detector & Masker)

## Problem Statement
Accidental leaks of Personally Identifiable Information (PII) in enterprise datasets pose significant compliance and security risks. Celare provides automated detection and masking of PII to protect sensitive data.

## Architecture Overview
Celare uses a hybrid two-phase approach:
1. **Phase 1 - High-Speed Regex Engine**: Deterministic pattern matching for common PII types (email, phone, SSN, credit card, etc.)
2. **Phase 2 - Contextual Ollama LLM Agent Loop**: Advanced contextual analysis using local LLM to catch edge cases and context-dependent PII

## Setup & Installation

### Clone the Repository
```bash
git clone <your-repo-url.git
cd Celare
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Set Up Ollama
1. Download and install Ollama from [ollama.com](https://ollama.com)
2. Pull a model (e.g., llama3.1):
   ```bash
   ollama pull llama3.1
   ```

## Usage

### Run Streamlit Dashboard
```bash
streamlit run app.py
```

### Run Tests
```bash
pytest
```

## Project Structure
```
Celare/
├── data_ingestion.py    # Data loading/saving utilities
├── regex_engine.py    # Regex-based PII detection/masking
├── llm_engine.py      # LLM-based PII detection/masking
├── workspace_rules.md  # Team collaboration rules
├── requirements.txt   # Python dependencies
└── README.md         # This file
```
