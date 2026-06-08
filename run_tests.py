import sys
from pathlib import Path
import pandas as pd
import unittest

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_ingestion import load_data, save_data
from regex_engine import mask_text, mask_deterministic
from llm_engine import OLLAMA_AVAILABLE, mask_full_pipeline

class TestCelare(unittest.TestCase):
    def test_load_csv(self):
        """Test loading CSV file with robust parsing"""
        mock_path = Path("sample_data/mock_dataset.csv")
        if mock_path.exists():
            result = load_data(mock_path)
            self.assertIsNotNone(result)
            df, ext = result
            self.assertEqual(ext, ".csv")
            self.assertGreater(len(df), 0)
    
    def test_regex_mask_single_text(self):
        """Test single text masking with regex engine"""
        test_text = "Contact John at john@example.com or 9876543210"
        masked, counts = mask_text(test_text)
        self.assertIn("[REDACTED_IDENTITY", masked)
        self.assertEqual(counts["email"], 1)
        self.assertEqual(counts["phone"], 1)
    
    def test_regex_mask_dataframe(self):
        """Test dataframe masking with regex engine"""
        df = pd.DataFrame({
            "name": ["John Doe", "Jane Smith"],
            "email": ["john@example.com", "jane@company.co.in"],
            "phone": ["9876543210", "+91 9123456789"],
            "pan": ["ABCDE1234F", "XYZPQ5678R"],
            "aadhaar": ["1234 5678 9012", "9876-5432-1098"]
        })
        masked_df, total_counts = mask_deterministic(df)
        self.assertIsNotNone(masked_df)
        self.assertGreater(sum(total_counts.values()), 0)

if __name__ == '__main__':
    print("=== Running Celare Integration Test Suite ===\n")
    unittest.main()
