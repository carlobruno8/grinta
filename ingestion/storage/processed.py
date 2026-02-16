"""Storage for processed DataFrame files."""
import pandas as pd
from pathlib import Path


def save_events_df(df: pd.DataFrame, match_id: int, processed_dir: Path, fmt: str) -> Path:
    """Save normalized events DataFrame to file.

    Args:
        df: Normalized events DataFrame
        match_id: Match ID for filename
        processed_dir: Directory to save the file
        fmt: File format ("csv" or "parquet")

    Returns:
        Path to the saved file

    Raises:
        ValueError: If fmt is not "csv" or "parquet"
    """
    processed_dir.mkdir(parents=True, exist_ok=True)

    if fmt == "parquet":
        filepath = processed_dir / f"events_{match_id}.parquet"
        df.to_parquet(filepath, index=False, engine="pyarrow")
    elif fmt == "csv":
        filepath = processed_dir / f"events_{match_id}.csv"
        df.to_csv(filepath, index=False)
    else:
        raise ValueError(f"Unsupported format: {fmt}. Use 'csv' or 'parquet'.")

    return filepath


def load_events_df(match_id: int, processed_dir: Path, fmt: str) -> pd.DataFrame:
    """Load normalized events DataFrame from file.

    Args:
        match_id: Match ID for filename
        processed_dir: Directory containing the file
        fmt: File format ("csv" or "parquet")

    Returns:
        Normalized events DataFrame

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If fmt is not "csv" or "parquet"
    """
    if fmt == "parquet":
        filepath = processed_dir / f"events_{match_id}.parquet"
        return pd.read_parquet(filepath, engine="pyarrow")
    elif fmt == "csv":
        filepath = processed_dir / f"events_{match_id}.csv"
        return pd.read_csv(filepath)
    else:
        raise ValueError(f"Unsupported format: {fmt}. Use 'csv' or 'parquet'.")
