import pandas as pd
from typing import Union


def read_csv_safe(file_path: str, encodings: list = ['utf-8', 'latin-1', 'cp1252']) -> Union[pd.DataFrame, None]:
    """
    Safely read a CSV file with multiple encoding fallback options.
    
    Args:
        file_path: Path to CSV file
        encodings: List of encodings to try in order
    """
    for encoding in encodings:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error reading CSV with encoding {encoding}: {e}")
    return None


def write_csv_safe(data: pd.DataFrame, file_path: str, encoding: str = 'utf-8') -> bool:
    """
    Safely write a DataFrame to CSV.
    
    Args:
        data: Pandas DataFrame to write
        file_path: Output file path
        encoding: Encoding to use (default utf-8)
    """
    try:
        data.to_csv(file_path, index=False, encoding=encoding)
        return True
    except Exception as e:
        print(f"Error writing CSV: {e}")
        return False


def read_json_safe(file_path: str, encodings: list = ['utf-8', 'latin-1']) -> Union[pd.DataFrame, None]:
    """
    Safely read JSON file with encoding fallback.
    
    Args:
        file_path: Path to JSON file
        encodings: List of encodings to try
    """
    for encoding in encodings:
        try:
            return pd.read_json(file_path, encoding=encoding)
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error reading JSON with encoding {encoding}: {e}")
    return None


def write_json_safe(data: pd.DataFrame, file_path: str, encoding: str = 'utf-8') -> bool:
    """
    Safely write DataFrame to JSON.
    
    Args:
        data: Pandas DataFrame to write
        file_path: Output file path
        encoding: Encoding to use
    """
    try:
        data.to_json(file_path, orient='records', encoding=encoding)
        return True
    except Exception as e:
        print(f"Error writing JSON: {e}")
        return False
