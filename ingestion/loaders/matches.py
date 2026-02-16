"""Loader for StatsBomb matches data."""
import statsbombpy.sb as sb
from typing import Union


def load_matches(competition_id: int, season_id: int) -> dict:
    """Load matches for a specific competition and season.

    Args:
        competition_id: StatsBomb competition ID
        season_id: StatsBomb season ID

    Returns:
        Raw matches data as dict (JSON-serializable).
        Typically keyed by match_id or a list of match dicts.

    Raises:
        Exception: If the API call fails
    """
    # Use fmt="dict" to get raw dict instead of DataFrame
    matches = sb.matches(competition_id, season_id, fmt="dict")
    return matches
