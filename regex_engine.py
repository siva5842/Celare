import re
import pandas as pd
from typing import Tuple, Dict


# Define PII patterns and their masks
PII_PATTERNS: Dict[str, re.Pattern] = {
    'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    'phone': re.compile(r'\b(?:\+91[-.\s]?)?[6-9]\d{9}\b'),
    'pan': re.compile(r'\b[A-Z]{5}\d{4}[A-Z]\b'),
    'aadhaar': re.compile(r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b')
}

PII_MASKS: Dict[str, str] = {
    'email': '[EMAIL_MASKED]',
    'phone': '[PHONE_MASKED]',
    'pan': '[PAN_MASKED]',
    'aadhaar': '[AADHAAR_MASKED]'
}


def mask_text(text: str) -> Tuple[str, Dict[str, int]]:
    """
    Mask PII in a single text string.
    
    Args:
        text: Input text to mask
        
    Returns:
        Tuple of (masked_text, count_dict) where count_dict tracks masked PII counts per type
    """
    masked_text = text
    counts = {key: 0 for key in PII_PATTERNS}
    
    for pii_type, pattern in PII_PATTERNS.items():
        matches = list(pattern.finditer(masked_text))
        # Sort matches from end to start to preserve positions
        for match in sorted(matches, key=lambda x: x.span()[0], reverse=True):
            start, end = match.span()
            masked_text = masked_text[:start] + PII_MASKS[pii_type] + masked_text[end:]
            counts[pii_type] += 1
    
    return masked_text, counts


def mask_deterministic(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Master function to mask PII in all string columns of a DataFrame.
    
    Args:
        df: Input pandas DataFrame
        
    Returns:
        Tuple of (masked_df, total_counts) where total_counts is total PII masked
    """
    masked_df = df.copy()
    total_counts = {key: 0 for key in PII_PATTERNS}
    
    for col in masked_df.select_dtypes(include=['object']).columns:
        # Process each value once: mask and count
        masked_values = []
        for val in df[col]:
            if pd.notna(val):
                masked_text_val, counts = mask_text(str(val))
                masked_values.append(masked_text_val)
                for key in PII_PATTERNS:
                    total_counts[key] += counts[key]
            else:
                masked_values.append(val)
        masked_df[col] = masked_values
    
    return masked_df, total_counts
