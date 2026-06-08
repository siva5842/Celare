import pandas as pd
from typing import Union, List, Optional


def load_data(file_path: str) -> Union[pd.DataFrame, None]:
    """
    Load data from various file formats into a pandas DataFrame.
    
    Args:
        file_path: Path to the input file (supports CSV, Excel, JSON, Parquet, etc.).
        
    Returns:
        Pandas DataFrame containing the loaded data, or None if loading fails.
    """
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            return pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            return pd.read_json(file_path)
        elif file_path.endswith('.parquet'):
            return pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def save_data(data: pd.DataFrame, output_path: str) -> bool:
    """
    Save a pandas DataFrame to a specified file path.
    
    Args:
        data: Pandas DataFrame to save.
        output_path: Path where the data will be saved.
        
    Returns:
        True if saving succeeds, False otherwise.
    """
    try:
        if output_path.endswith('.csv'):
            data.to_csv(output_path, index=False)
        elif output_path.endswith(('.xlsx', '.xls')):
            data.to_excel(output_path, index=False)
        elif output_path.endswith('.json'):
            data.to_json(output_path, orient='records')
        elif output_path.endswith('.parquet'):
            data.to_parquet(output_path, index=False)
        else:
            raise ValueError(f"Unsupported output format: {output_path}")
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False


def sample_data(data: pd.DataFrame, sample_size: int = 100) -> pd.DataFrame:
    """
    Generate a random sample from the input DataFrame.
    
    Args:
        data: Input pandas DataFrame.
        sample_size: Number of rows to sample (default: 100).
        
    Returns:
        Sampled pandas DataFrame.
    """
    return data.sample(n=min(sample_size, len(data)), random_state=42)
