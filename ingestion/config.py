"""Configuration for the ingestion pipeline.

Supports loading from environment variables and provides defaults for local development.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


@dataclass
class IngestionConfig:
    """Configuration for StatsBomb data ingestion.

    Attributes:
        competition_id: StatsBomb competition ID
        season_id: StatsBomb season ID
        match_ids: Optional list of specific match IDs to ingest. If None, all matches
            for the competition+season will be ingested.
        raw_dir: Directory path for storing raw JSON files
        processed_dir: Directory path for storing processed DataFrames
        processed_format: Output format for processed data ("csv" | "parquet")
    """

    competition_id: int
    season_id: int
    match_ids: Optional[list[int]] = None
    raw_dir: Path = Path("data/raw")
    processed_dir: Path = Path("data/processed")
    processed_format: str = "parquet"

    def __post_init__(self):
        """Convert string paths to Path objects if needed."""
        if isinstance(self.raw_dir, str):
            self.raw_dir = Path(self.raw_dir)
        if isinstance(self.processed_dir, str):
            self.processed_dir = Path(self.processed_dir)

        # Ensure directories exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        # Validate format
        if self.processed_format not in ("csv", "parquet"):
            raise ValueError(f"processed_format must be 'csv' or 'parquet', got '{self.processed_format}'")


def get_ingestion_config() -> IngestionConfig:
    """Load ingestion configuration from environment variables.

    Environment variables:
        GRINTA_COMPETITION_ID: Competition ID (required)
        GRINTA_SEASON_ID: Season ID (required)
        GRINTA_MATCH_ID: Optional comma-separated match IDs (e.g., "123,456,789")
        GRINTA_RAW_DIR: Raw data directory (default: "data/raw")
        GRINTA_PROCESSED_DIR: Processed data directory (default: "data/processed")
        GRINTA_PROCESSED_FORMAT: Output format (default: "parquet")

    Returns:
        IngestionConfig instance

    Raises:
        ValueError: If required environment variables are missing
    """
    competition_id = os.getenv("GRINTA_COMPETITION_ID")
    season_id = os.getenv("GRINTA_SEASON_ID")

    if competition_id is None:
        raise ValueError("GRINTA_COMPETITION_ID environment variable is required")
    if season_id is None:
        raise ValueError("GRINTA_SEASON_ID environment variable is required")

    match_ids_str = os.getenv("GRINTA_MATCH_ID")
    match_ids = None
    if match_ids_str:
        match_ids = [int(mid.strip()) for mid in match_ids_str.split(",")]

    raw_dir = os.getenv("GRINTA_RAW_DIR", "data/raw")
    processed_dir = os.getenv("GRINTA_PROCESSED_DIR", "data/processed")
    processed_format = os.getenv("GRINTA_PROCESSED_FORMAT", "parquet")

    return IngestionConfig(
        competition_id=int(competition_id),
        season_id=int(season_id),
        match_ids=match_ids,
        raw_dir=Path(raw_dir),
        processed_dir=Path(processed_dir),
        processed_format=processed_format,
    )
