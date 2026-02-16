"""StatsBomb data ingestion pipeline.

Public API for loading, normalizing, and persisting StatsBomb open data.
"""
from config import GrintaConfig, get_config
from ingestion.loaders import load_competitions, load_events, load_matches
from ingestion.normalizers import normalize_events
from ingestion.pipeline import PipelineResult, run_match_events_pipeline, run_pipeline
from ingestion.storage import (
    load_events_df,
    load_events as load_events_from_cache,
    save_competitions,
    save_events,
    save_events_df,
    save_matches,
)

__all__ = [
    # Configuration
    "GrintaConfig",
    "get_config",
    # Loaders
    "load_competitions",
    "load_matches",
    "load_events",
    # Normalizers
    "normalize_events",
    # Storage
    "save_competitions",
    "save_matches",
    "save_events",
    "load_events_from_cache",
    "save_events_df",
    "load_events_df",
    # Pipeline
    "run_pipeline",
    "run_match_events_pipeline",
    "PipelineResult",
]
