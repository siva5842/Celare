import sys
from pathlib import Path
import pandas as pd

print("=== Testing Celare Core Components ===\n")

# Test data_ingestion.py
print("1. Testing data_ingestion.py...")
try:
    from data_ingestion import load_data, save_data
    
    # Load mock data
    mock_path = Path("sample_data/mock_dataset.csv")
    if mock_path.exists():
        load_result = load_data(mock_path)
        if load_result:
            df, ext = load_result
            print(f"✅ Successfully loaded {len(df)} rows from {ext}")
        else:
            print("❌ Failed to load mock data")
            sys.exit(1)
    else:
        print(f"⚠️  Mock data not found at {mock_path}, creating test data")
        df = pd.DataFrame({
            "name": ["John Doe", "Jane Smith"],
            "email": ["john@example.com", "jane@company.co.in"],
            "phone": ["9876543210", "+91 9123456789"],
            "pan": ["ABCDE1234F", "XYZPQ5678R"],
            "aadhaar": ["1234 5678 9012", "9876-5432-1098"]
        })
        df.to_csv("test_data.csv", index=False)
        load_result = load_data("test_data.csv")
        if load_result:
            df, ext = load_result
            print(f"✅ Successfully loaded {len(df)} rows from {ext}")
except Exception as e:
    print(f"❌ Failed to test data_ingestion: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n2. Testing regex_engine.py...")
try:
    from regex_engine import mask_deterministic, mask_text
    
    # Test single text masking
    test_text = "Contact John at john@example.com or 9876543210"
    masked_text, counts = mask_text(test_text)
    print(f"✅ Text masking test passed: '{masked_text}'")
    print(f"   Counts: {counts}")
    
    # Test DataFrame masking
    masked_df, total_counts = mask_deterministic(df)
    print(f"✅ DataFrame masking test passed")
    print(f"   Total counts: {total_counts}")
except Exception as e:
    print(f"❌ Failed to test regex_engine: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n3. Testing llm_engine.py...")
try:
    from llm_engine import OLLAMA_AVAILABLE, mask_full_pipeline
    
    if OLLAMA_AVAILABLE:
        print(f"✅ Ollama is available")
        # Quick test (will skip if no model)
        masked_df_lm, counts_lm = mask_full_pipeline(df.head(2))
        print(f"✅ Full pipeline test passed")
    else:
        print("⚠️  Ollama not installed, skipping LLM tests")
except Exception as e:
    print(f"❌ Failed to test llm_engine: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== All Core Tests Passed! ===")
