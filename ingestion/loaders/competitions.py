"""Loader for StatsBomb competitions data."""
import statsbombpy.sb as sb
from typing import Union


def load_competitions() -> Union[list, dict]:
    """Load competitions list from StatsBomb open data.

    Returns:
        Raw competitions data as list or dict (JSON-serializable).
        The exact format depends on statsbombpy's response.

    Raises:
        Exception: If the API call fails
    """
    # Use fmt="dict" to get raw dict/list instead of DataFrame
    competitions = sb.competitions(fmt="dict")
    return competitions
