"""Utility functions for features module - data loading and time filtering."""
import re
from pathlib import Path
from typing import Optional

import pandas as pd

from config import GrintaConfig, get_config


# ==============================================================================
# DATA LOADING
# ==============================================================================

def load_match_events(
    match_id: int,
    processed_dir: Optional[Path] = None,
    fmt: Optional[str] = None,
    config: Optional[GrintaConfig] = None,
) -> pd.DataFrame:
    """Load normalized events DataFrame for a match.

    Reads from data/processed/ using the same naming convention as ingestion.

    Args:
        match_id: StatsBomb match ID.
        processed_dir: Override directory (optional).
        fmt: Override format "csv" or "parquet" (optional).
        config: Full config override (optional).

    Returns:
        Normalized events DataFrame with columns as per ingestion schema.

    Raises:
        FileNotFoundError: If the processed file does not exist.
    """
    if config is None:
        config = get_config()
    directory = processed_dir if processed_dir is not None else config.processed_dir
    format_str = fmt if fmt is not None else config.processed_format

    if format_str == "parquet":
        filepath = directory / f"events_{match_id}.parquet"
        return pd.read_parquet(filepath, engine="pyarrow")
    elif format_str == "csv":
        filepath = directory / f"events_{match_id}.csv"
        return pd.read_csv(filepath)
    else:
        raise ValueError(f"Unsupported format: {format_str}. Use 'csv' or 'parquet'.")


# ==============================================================================
# TIME FILTERING
# ==============================================================================

def _timestamp_to_seconds(timestamp: str) -> float:
    """Convert 'HH:MM:SS.fff' to seconds from period start."""
    if pd.isna(timestamp):
        return 0.0
    match = re.match(r"(\d+):(\d+):(\d+)\.?(\d*)", str(timestamp))
    if not match:
        return 0.0
    h, m, s = int(match.group(1)), int(match.group(2)), int(match.group(3))
    frac = match.group(4)
    secs = h * 3600 + m * 60 + s
    if frac:
        secs += int(frac.ljust(3, "0")[:3]) / 1000.0
    return secs


def filter_by_period(df: pd.DataFrame, period: int) -> pd.DataFrame:
    """Return events in a single period (1, 2, etc.)."""
    if "period" not in df.columns:
        return df
    return df[df["period"] == period].copy()


def filter_last_n_minutes(df: pd.DataFrame, n_minutes: float, period: Optional[int] = None) -> pd.DataFrame:
    """Return events in the last N minutes of the match (or of a period).

    Time is measured from the end of the period backwards. E.g. last 10 minutes
    of period 2 = events from (period_length - 10) to end of period 2.

    Args:
        df: Events DataFrame with 'period' and 'timestamp'.
        n_minutes: Number of minutes from end (e.g. 10 for "last 10 minutes").
        period: If set, only consider this period; otherwise use last period in data.

    Returns:
        Filtered DataFrame.
    """
    if "period" not in df.columns or "timestamp" not in df.columns:
        return df.copy()
    df = df.copy()
    df["_seconds"] = df["timestamp"].apply(_timestamp_to_seconds)
    periods = sorted(df["period"].dropna().unique())
    if not periods:
        return df
    use_period = period if period is not None else max(periods)
    period_events = df[df["period"] == use_period]
    if period_events.empty:
        return period_events
    # Assume 45 min per period if we can't infer
    period_max_seconds = period_events["_seconds"].max()
    period_length_seconds = max(period_max_seconds, 45 * 60)
    cutoff = period_length_seconds - n_minutes * 60
    out = df[(df["period"] == use_period) & (df["_seconds"] >= cutoff)].drop(columns=["_seconds"], errors="ignore")
    return out


def filter_first_n_minutes(df: pd.DataFrame, n_minutes: float, period: Optional[int] = None) -> pd.DataFrame:
    """Return events in the first N minutes of a period (or period 1)."""
    if "period" not in df.columns or "timestamp" not in df.columns:
        return df.copy()
    df = df.copy()
    df["_seconds"] = df["timestamp"].apply(_timestamp_to_seconds)
    use_period = period if period is not None else 1
    cutoff = n_minutes * 60
    out = df[(df["period"] == use_period) & (df["_seconds"] <= cutoff)].drop(columns=["_seconds"], errors="ignore")
    return out
