"""Loader for StatsBomb events data."""
import statsbombpy.sb as sb
from typing import Union


def load_events(match_id: int) -> Union[list, dict]:
    """Load raw event data for a specific match.

    Args:
        match_id: StatsBomb match ID

    Returns:
        Raw events data as list or dict (JSON-serializable).
        Typically a list of event dicts.

    Raises:
        Exception: If the API call fails
    """
    # Use fmt="dict" to get raw dict/list instead of DataFrame
    # split=False to get all events in one structure
    events = sb.events(match_id, fmt="dict", split=False)
    return events
