import pytest
from unittest.mock import patch, MagicMock
from llm_engine import LLMEngine

@pytest.fixture
def engine():
    return LLMEngine()

def test_regex_masking_email(engine):
    text = "Contact me at test@example.com for info."
    expected = "Contact me at [EMAIL] for info."
    assert engine.mask_regex_pii(text) == expected

def test_regex_masking_phone(engine):
    text = "Call me at +91 9876543210 or 9876543210."
    # The regex in llm_engine handles +91 and 10 digits
    # "9876543210" matches [PHONE]
    # "+91 9876543210" matches [PHONE]
    masked = engine.mask_regex_pii(text)
    assert "[PHONE]" in masked
    assert "9876543210" not in masked

def test_regex_masking_pan(engine):
    text = "My PAN is ABCDE1234F."
    expected = "My PAN is [PAN]."
    assert engine.mask_regex_pii(text) == expected

def test_regex_masking_aadhaar(engine):
    text = "Aadhaar number: 1234 5678 9012."
    expected = "Aadhaar number: [AADHAAR]."
    assert engine.mask_regex_pii(text) == expected

def test_regex_combined(engine):
    text = "Email: a@b.com, PAN: ABCDE1234F, Phone: 9876543210"
    masked = engine.mask_regex_pii(text)
    assert "[EMAIL]" in masked
    assert "[PAN]" in masked
    assert "[PHONE]" in masked

@patch('requests.post')
def test_llm_soft_pii_high_confidence(mock_post, engine):
    # Mock high confidence response from Ollama
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": '{"entities": [{"text": "Arjun", "type": "NAME"}, {"text": "Bangalore", "type": "LOCATION"}], "confidence": 90}'
    }
    mock_post.return_value = mock_response

    text = "My name is Arjun and I live in Bangalore."
    result = engine.process_soft_pii(text)
    
    assert "[NAME]" in result
    assert "[LOCATION]" in result
    assert "Arjun" not in result
    assert "Bangalore" not in result

@patch('requests.post')
def test_llm_soft_pii_low_confidence_loop(mock_post, engine):
    # Mock low confidence responses for first 2 attempts, then high confidence
    mock_low = MagicMock()
    mock_low.status_code = 200
    mock_low.json.return_value = {
        "response": '{"entities": [], "confidence": 50}'
    }
    
    mock_high = MagicMock()
    mock_high.status_code = 200
    mock_high.json.return_value = {
        "response": '{"entities": [{"text": "Arjun", "type": "NAME"}], "confidence": 95}'
    }
    
    # Side effect: 2 lows then 1 high
    mock_post.side_effect = [mock_low, mock_low, mock_high]

    text = "My name is Arjun."
    result = engine.process_soft_pii(text)
    
    assert "[NAME]" in result
    assert mock_post.call_count == 3

@patch('requests.post')
def test_llm_soft_pii_failure_fallback(mock_post, engine):
    # Mock persistent low confidence
    mock_low = MagicMock()
    mock_low.status_code = 200
    mock_low.json.return_value = {
        "response": '{"entities": [{"text": "Arjun", "type": "NAME"}], "confidence": 50}'
    }
    mock_post.return_value = mock_low

    text = "My name is Arjun."
    result = engine.process_soft_pii(text)
    
    # Even with low confidence after retries, it should try to mask what it found
    assert "[NAME]" in result
    assert mock_post.call_count == 3

def test_complete_pipeline(engine):
    # We can mock both regex and LLM parts by mocking process_soft_pii and mask_regex_pii if needed,
    # but here we'll just mock the API call and let the rest run.
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": '{"entities": [{"text": "Arjun", "type": "NAME"}], "confidence": 90}'
        }
        mock_post.return_value = mock_response

        text = "Arjun's email is arjun@example.com"
        result = engine.anonymize(text)
        
        assert "[NAME]" in result
        assert "[EMAIL]" in result
        assert "Arjun" not in result
        assert "arjun@example.com" not in result
