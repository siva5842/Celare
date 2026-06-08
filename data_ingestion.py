import pandas as pd
import csv
from typing import Union, Tuple
from pathlib import Path

def _is_header_row(row: pd.Series) -> bool:
    """Helper to determine if first row is a header"""
    row_str = str(row).lower()
    if "header" in row_str:
        return True
    # Check for common generic column names
    generic_names = {"name", "email", "phone", "address", "id", "date", "time", "value", "text"}
    row_values = [str(x).strip().lower() for x in row if pd.notna(x)]
    matches = sum(1 for v in row_values if v in generic_names)
    # If more than 30% are generic, treat as header
    return len(row_values) > 0 and matches / len(row_values) > 0.3

def load_data(file_path: Union[str, Path]) -> Union[Tuple[pd.DataFrame, str], None]:
    """
    Safely load data from CSV, JSON, or XLSX files with robust parsing and header detection.
    
    Args:
        file_path: Path to the input file
        
    Returns:
        Tuple of (DataFrame, file_extension) or None if failed
    """
    file_path = Path(file_path)
    ext = file_path.suffix.lower()
    
    try:
        if ext == ".csv":
            # First read without header to inspect first row
            temp_df = pd.read_csv(file_path, quoting=csv.QUOTE_MINIMAL, on_bad_lines='skip', encoding_errors='replace', header=None, encoding='utf-8')
            if len(temp_df) > 0 and _is_header_row(temp_df.iloc[0]):
                # Use first row as header
                df = pd.read_csv(file_path, quoting=csv.QUOTE_MINIMAL, on_bad_lines='skip', encoding_errors='replace', header=0, encoding='utf-8')
            else:
                # Treat first row as data
                df = temp_df
            return df, ext
        elif ext == ".json":
            try:
                df = pd.read_json(file_path, encoding='utf-8', encoding_errors='replace')
            except:
                df = pd.read_json(file_path, orient='records', encoding='utf-8', encoding_errors='replace')
            return df, ext
        elif ext == ".xlsx":
            temp_df = pd.read_excel(file_path, engine='openpyxl', header=None)
            if len(temp_df) > 0 and _is_header_row(temp_df.iloc[0]):
                df = pd.read_excel(file_path, engine='openpyxl', header=0)
            else:
                df = temp_df
            return df, ext
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def save_data(df: pd.DataFrame, output_path: Union[str, Path]) -> bool:
    """
    Save DataFrame to the specified format.
    
    Args:
        df: DataFrame to save
        output_path: Path where data will be saved
        
    Returns:
        True if save succeeded, False otherwise
    """
    output_path = Path(output_path)
    ext = output_path.suffix.lower()
    
    try:
        if ext == ".csv":
            df.to_csv(output_path, index=False, quoting=csv.QUOTE_MINIMAL, encoding='utf-8')
        elif ext == ".json":
            df.to_json(output_path, orient='records', indent=2, force_ascii=False)
        elif ext == ".xlsx":
            df.to_excel(output_path, index=False, engine='openpyxl')
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False
