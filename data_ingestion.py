import pandas as pd
import csv
from typing import Union, Tuple
from pathlib import Path

def load_data(file_path: Union[str, Path]) -> Union[Tuple[pd.DataFrame, str], None]:
    """
    Safely load data from CSV, JSON, or XLSX files with robust parsing.
    
    Args:
        file_path: Path to the input file (supports .csv, .json, .xlsx)
        
    Returns:
        Tuple of (DataFrame, file_extension) or None if failed
    """
    file_path = Path(file_path)
    ext = file_path.suffix.lower()
    
    try:
        if ext == ".csv":
            df = pd.read_csv(
                file_path,
                quoting=csv.QUOTE_MINIMAL,
                on_bad_lines="skip",
                encoding_errors="replace",
                encoding="utf-8"
            )
            return df, ext
        elif ext == ".json":
            try:
                df = pd.read_json(file_path, encoding="utf-8", encoding_errors="replace")
            except:
                df = pd.read_json(file_path, orient="records", encoding="utf-8", encoding_errors="replace")
            return df, ext
        elif ext == ".xlsx":
            df = pd.read_excel(file_path, engine="openpyxl")
            return df, ext
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def save_data(df: pd.DataFrame, output_path: Union[str, Path]) -> bool:
    """
    Save DataFrame to the same format as input.
    
    Args:
        df: DataFrame to save
        output_path: Path where data will be saved (extension determines format)
        
    Returns:
        True if save succeeded, False otherwise
    """
    output_path = Path(output_path)
    ext = output_path.suffix.lower()
    
    try:
        if ext == ".csv":
            df.to_csv(output_path, index=False, quoting=csv.QUOTE_MINIMAL, encoding="utf-8")
        elif ext == ".json":
            df.to_json(output_path, orient="records", indent=2, force_ascii=False)
        elif ext == ".xlsx":
            df.to_excel(output_path, index=False, engine="openpyxl")
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False
