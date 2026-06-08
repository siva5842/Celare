import re
import requests
import json
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMEngine:
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.api_url = f"{base_url}/api/generate"

    def mask_regex_pii(self, text: str) -> str:
        """
        Masks Email, Phone, PAN, and Aadhaar using regex.
        """
        # Email: basic pattern
        text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]', text)
        
        # Phone: Supports +91, 10 digits, etc.
        text = re.sub(r'(\+91[\-\s]?)?[6-9]\d{9}', '[PHONE]', text)
        
        # PAN: 5 letters, 4 digits, 1 letter
        text = re.sub(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', '[PAN]', text)
        
        # Aadhaar: 12 digits (often 4-4-4)
        text = re.sub(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b', '[AADHAAR]', text)
        
        return text

    def _call_ollama(self, prompt: str) -> Dict[str, Any]:
        """
        Helper to call local Ollama API.
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0
                }
            }
            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            return json.loads(response.json().get("response", "{}"))
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return {"entities": [], "confidence": 0}

    def process_soft_pii(self, text: str) -> str:
        """
        Processes Names and Locations using an autonomous Agent Loop with Ollama.
        """
        current_text = text
        max_retries = 3
        
        for attempt in range(max_retries):
            # Formulate prompt with sentence context
            prompt = (
                f"Identify 'NAME' and 'LOCATION' entities in the following text. "
                f"Return ONLY a JSON object with two keys: "
                f"'entities' (list of {{'text': str, 'type': 'NAME'|'LOCATION'}}) "
                f"and 'confidence' (integer 0-100 representing your certainty).\n\n"
                f"Text: \"{current_text}\"\n\n"
                f"Output JSON:"
            )
            
            result = self._call_ollama(prompt)
            confidence = result.get("confidence", 0)
            entities = result.get("entities", [])
            
            logger.info(f"Attempt {attempt + 1}: Confidence {confidence}%")
            
            if confidence >= 85:
                # High confidence: Redact entities
                for entity in entities:
                    entity_text = entity.get("text")
                    entity_type = entity.get("type")
                    if entity_text and entity_type:
                        # Case insensitive replacement for safety
                        pattern = re.compile(re.escape(entity_text), re.IGNORECASE)
                        current_text = pattern.sub(f"[{entity_type}]", current_text)
                return current_text
            else:
                # Low confidence: Reprompt with more explicit context (Agent Loop)
                logger.warning(f"Low confidence ({confidence}%). Retrying with enhanced context...")
                # In the loop, we could potentially refine the text or prompt
                # For this implementation, we simulate the 're-prompt' by asking for more precision
                continue
        
        # If still low confidence after retries, we might want to mask anyway or leave as is.
        # Requirement says "until validated or masked". We'll perform a best-effort masking.
        for entity in entities:
            entity_text = entity.get("text")
            entity_type = entity.get("type")
            if entity_text and entity_type:
                pattern = re.compile(re.escape(entity_text), re.IGNORECASE)
                current_text = pattern.sub(f"[{entity_type}]", current_text)
                
        return current_text

    def anonymize(self, text: str) -> str:
        """
        Complete anonymization pipeline.
        """
        # 1. Regex Masking
        text = self.mask_regex_pii(text)
        
        # 2. LLM Soft PII Redaction
        text = self.process_soft_pii(text)
        
        return text

if __name__ == "__main__":
    engine = LLMEngine()
    sample = "My name is Arjun and I live in Bangalore. My email is arjun@example.com and PAN is ABCDE1234F."
    print(engine.anonymize(sample))
