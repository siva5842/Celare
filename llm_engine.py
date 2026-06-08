import ollama
from typing import List, Dict, Any


def detect_pii_with_llm(text: str, model: str = 'llama3.1') -> List[Dict[str, Any]]:
    """
    Detect PII (Personally Identifiable Information) in text using a local LLM via Ollama.
    
    Args:
        text: Input text to analyze for PII.
        model: Name of the Ollama model to use (default: 'llama3.1').
        
    Returns:
        List of dictionaries with 'type' and 'value' of detected PII.
    """
    prompt = f"""
    Analyze the following text and identify all Personally Identifiable Information (PII).
    Return your response as a JSON list of objects, each with keys "type" and "value".
    Common PII types include: name, email, phone, address, SSN, credit card, IP address, etc.
    
    Text: "{text}"
    
    Response format: [{{"type": "...", "value": "..."}}, ...]
    """
    
    try:
        response = ollama.generate(model=model, prompt=prompt)
        return response.get('response', [])
    except Exception as e:
        print(f"Error with LLM PII detection: {e}")
        return []


def mask_pii_with_llm(text: str, model: str = 'llama3.1') -> str:
    """
    Mask PII in text using a local LLM via Ollama.
    
    Args:
        text: Input text containing PII.
        model: Name of the Ollama model to use (default: 'llama3.1').
        
    Returns:
        Text with PII masked.
    """
    prompt = f"""
    Mask all Personally Identifiable Information (PII) in the following text.
    Replace PII with appropriate placeholders (e.g., [NAME], [EMAIL], [PHONE], etc.).
    Only return the masked text, no additional explanation.
    
    Text: "{text}"
    """
    
    try:
        response = ollama.generate(model=model, prompt=prompt)
        return response.get('response', text)
    except Exception as e:
        print(f"Error with LLM PII masking: {e}")
        return text


def process_text_with_llm(text: str, model: str = 'llama3.1') -> str:
    """
    End-to-end PII detection and masking using a local LLM via Ollama.
    
    Args:
        text: Input text to process.
        model: Name of the Ollama model to use (default: 'llama3.1').
        
    Returns:
        Text with all detected PII masked.
    """
    return mask_pii_with_llm(text, model)
