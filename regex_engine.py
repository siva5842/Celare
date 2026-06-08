import re
from typing import List, Dict, Any


def detect_pii(text: str) -> List[Dict[str, Any]]:
    """
    Detect PII (Personally Identifiable Information) in a given text using regular expressions.
    
    Args:
        text: Input text to analyze for PII.
        
    Returns:
        List of dictionaries, each containing 'type', 'value', 'start', and 'end' of detected PII.
    """
    pii_patterns = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        'ssn': r'\b\d{3}[-.]?\d{2}[-.]?\d{4}\b',
        'credit_card': r'\b(?:\d[ -]*?){13,16}\b',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'zip_code': r'\b\d{5}(?:[-.]?\d{4})?\b'
    }
    
    detected_pii = []
    
    for pii_type, pattern in pii_patterns.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            detected_pii.append({
                'type': pii_type,
                'value': match.group(),
                'start': match.start(),
                'end': match.end()
            })
    
    return detected_pii


def mask_pii(text: str, detected_pii: List[Dict[str, Any]], mask_char: str = '*') -> str:
    """
    Mask detected PII in text using a specified mask character.
    
    Args:
        text: Original text containing PII.
        detected_pii: List of detected PII from detect_pii function.
        mask_char: Character to use for masking (default: '*').
        
    Returns:
        Text with PII masked.
    """
    masked_text = list(text)
    
    for pii in sorted(detected_pii, key=lambda x: x['start'], reverse=True):
        masked_text[pii['start']:pii['end']] = [mask_char] * (pii['end'] - pii['start'])
    
    return ''.join(masked_text)


def process_text(text: str) -> str:
    """
    End-to-end PII detection and masking for a given text.
    
    Args:
        text: Input text to process.
        
    Returns:
        Text with all detected PII masked.
    """
    detected = detect_pii(text)
    return mask_pii(text, detected)
