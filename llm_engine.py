import pandas as pd
from typing import Tuple, Dict, List, Optional
import json

# Try to import Ollama, provide fallback if not available
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: Ollama not installed. Indirect PII detection will be skipped.")

def analyze_text_indirect(text: str, model: str = "llama3.1") -> Tuple[str, bool]:
    """
    Use a local Ollama LLM to detect indirect PII combinations in text.
    
    Args:
        text: Input text to analyze
        model: Name of Ollama model to use
        
    Returns:
        Tuple of (masked_text, contains_indirect_pii)
    """
    if not OLLAMA_AVAILABLE:
        return text, False
    
    if pd.isna(text) or not str(text).strip():
        return text, False
    
    system_prompt = """
    You are a PII detection specialist. Your task is to analyze text and identify INDIRECT PII.
    INDIRECT PII is when two or more non-sensitive pieces of information are combined to reveal identity.
    Examples of INDIRECT PII combinations:
    - Full Name + Date of Birth
    - Full Name + Specific Salary
    - Address + Medical Condition
    - Date of Birth + Place of Birth
    - Email + Phone + Name
    
    For each text you analyze, respond ONLY with a valid JSON object in this exact format:
    {
        "contains_indirect_pii": true/false,
        "masked_text": "text with indirect PII replaced by [REDACTED_IDENTITY]"
    }
    
    Rules:
    1. Only replace the specific parts that form the indirect PII combination
    2. Do NOT replace normal operational data
    3. Always return valid JSON with both keys
    4. If no indirect PII, return the original text
    """
    
    try:
        response = ollama.generate(
            model=model,
            prompt=str(text),
            system=system_prompt,
            format="json"
        )
        
        result = json.loads(response["response"])
        return result.get("masked_text", text), result.get("contains_indirect_pii", False)
    except Exception as e:
        print(f"Warning: Ollama analysis failed: {e}")
        return text, False

def mask_indirect(df: pd.DataFrame, model: str = "llama3.1") -> Tuple[pd.DataFrame, int]:
    """
    Apply indirect PII masking to an entire DataFrame using Ollama.
    
    Args:
        df: Input DataFrame (already processed for direct PII)
        model: Ollama model name
        
    Returns:
        Tuple of (masked_df, total_indirect_pii_count)
    """
    if not OLLAMA_AVAILABLE:
        return df, 0
    
    masked_df = df.copy()
    total_count = 0
    
    for col in masked_df.select_dtypes(include=["object"]).columns:
        processed = []
        for val in df[col]:
            masked_val, has_indirect = analyze_text_indirect(val, model)
            processed.append(masked_val)
            if has_indirect:
                total_count += 1
        masked_df[col] = processed
    
    return masked_df, total_count

def mask_full_pipeline(df: pd.DataFrame, model: str = "llama3.1") -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    End-to-end pipeline: first mask direct PII, then indirect PII.
    
    Args:
        df: Input DataFrame
        model: Ollama model name
        
    Returns:
        Tuple of (masked_df, counts_dict)
    """
    from regex_engine import mask_deterministic
    
    masked_df, direct_counts = mask_deterministic(df)
    masked_df, indirect_count = mask_indirect(masked_df, model)
    
    total_counts = {
        **direct_counts,
        "indirect_pii_combinations": indirect_count
    }
    
    return masked_df, total_counts
