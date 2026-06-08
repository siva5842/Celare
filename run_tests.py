import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_engine import LLMEngine

class TestPII(unittest.TestCase):
    def setUp(self):
        self.engine = LLMEngine()

    def test_regex_masking_email(self):
        text = "Contact me at test@example.com for info."
        expected = "Contact me at [EMAIL] for info."
        self.assertEqual(self.engine.mask_regex_pii(text), expected)

    def test_regex_masking_phone(self):
        text = "Call me at +91 9876543210."
        masked = self.engine.mask_regex_pii(text)
        self.assertIn("[PHONE]", masked)

    def test_regex_masking_pan(self):
        text = "My PAN is ABCDE1234F."
        expected = "My PAN is [PAN]."
        self.assertEqual(self.engine.mask_regex_pii(text), expected)

    def test_regex_masking_aadhaar(self):
        text = "Aadhaar number: 1234 5678 9012."
        expected = "Aadhaar number: [AADHAAR]."
        self.assertEqual(self.engine.mask_regex_pii(text), expected)

    @patch('requests.post')
    def test_llm_soft_pii_high_confidence(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": '{"entities": [{"text": "Arjun", "type": "NAME"}, {"text": "Bangalore", "type": "LOCATION"}], "confidence": 90}'
        }
        mock_post.return_value = mock_response

        text = "My name is Arjun and I live in Bangalore."
        result = self.engine.process_soft_pii(text)
        
        self.assertIn("[NAME]", result)
        self.assertIn("[LOCATION]", result)
        self.assertNotIn("Arjun", result)

    @patch('requests.post')
    def test_llm_soft_pii_low_confidence_loop(self, mock_post):
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
        
        mock_post.side_effect = [mock_low, mock_low, mock_high]

        text = "My name is Arjun."
        result = self.engine.process_soft_pii(text)
        
        self.assertIn("[NAME]", result)
        self.assertEqual(mock_post.call_count, 3)

if __name__ == '__main__':
    unittest.main()
