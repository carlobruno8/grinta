"""Loaders for fetching StatsBomb data from external sources."""

from ingestion.loaders.competitions import load_competitions
from ingestion.loaders.events import load_events
from ingestion.loaders.matches import load_matches

__all__ = ["load_competitions", "load_matches", "load_events"]
