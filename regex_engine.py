import re
import pandas as pd
from typing import Tuple, Dict

# Define PII patterns and standardized categorical tokens
PII_PATTERNS: Dict[str, re.Pattern] = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone": re.compile(r'(?:\+91|0)?[6-9]\d{9}'),
    "pan": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
    "aadhaar": re.compile(r"\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b")
}

PII_TOKENS: Dict[str, str] = {
    "email": "[REDACTED_IDENTITY]",
    "phone": "[REDACTED_IDENTITY]",
    "pan": "[REDACTED_IDENTITY]",
    "aadhaar": "[REDACTED_IDENTITY]"
}

def mask_text(text: str) -> Tuple[str, Dict[str, int]]:
    """
    Mask direct PII in a single text string using standardized tokens.
    
    Args:
        text: Input text to process
        
    Returns:
        Tuple of (masked_text, count_dict)
    """
    if pd.isna(text):
        return text, {key: 0 for key in PII_PATTERNS}
    
    masked_text = str(text)
    counts = {key: 0 for key in PII_PATTERNS}
    
    for pii_type, pattern in PII_PATTERNS.items():
        matches = list(pattern.finditer(masked_text))
        for match in sorted(matches, key=lambda m: m.start(), reverse=True):
            start, end = match.span()
            masked_text = masked_text[:start] + PII_TOKENS[pii_type] + masked_text[end:]
            counts[pii_type] += 1
    
    return masked_text, counts

def mask_deterministic(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Master function to mask direct PII in all columns of a DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Tuple of (masked_df, total_counts)
    """
    masked_df = df.copy()
    total_counts = {key: 0 for key in PII_PATTERNS}
    
    # Apply masks to ALL columns, regardless of dtype
    for col in masked_df.columns:
        processed = []
        for val in df[col]:
            masked_val, counts = mask_text(val)
            processed.append(masked_val)
            for key in PII_PATTERNS:
                total_counts[key] += counts[key]
        masked_df[col] = processed
    
    return masked_df, total_counts
