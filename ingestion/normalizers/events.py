"""Normalizer for StatsBomb events data.

Transforms raw events (dict/list) into a normalized pandas DataFrame with a stable schema
suitable for team-level analysis in Phase 1.

Schema:
    - event_id: Unique event identifier (UUID string)
    - match_id: Match identifier
    - period: Period number (1, 2, etc.)
    - timestamp: Event timestamp within period
    - type_name: Event type name (e.g., "Pass", "Shot", "Ball Receipt")
    - team_id: Team ID
    - team_name: Team name
    - player_id: Player ID (nullable)
    - player_name: Player name (nullable)
    - x: Starting x-coordinate (0-120)
    - y: Starting y-coordinate (0-80)
    - end_x: Ending x-coordinate (nullable)
    - end_y: Ending y-coordinate (nullable)
    - outcome: Event outcome (nullable)
    - ... (other flattened attributes as needed)
"""
import pandas as pd
from typing import Union


def normalize_events(raw_events: Union[list, dict], match_id: Union[int, None] = None) -> pd.DataFrame:
    """Normalize raw events data into a structured DataFrame.

    Handles both list and dict formats from StatsBomb API.

    Args:
        raw_events: Raw events data - can be:
            - List of event dicts
            - Dict keyed by event type, each value being a list of events
        match_id: Optional match ID to add to all events. If not provided,
                  will attempt to extract from event data.

    Returns:
        Normalized DataFrame with one row per event and consistent schema.
        All events are flattened into a single table.

    Raises:
        ValueError: If raw_events format is not recognized
    """
    # Handle dict format (events split by type)
    if isinstance(raw_events, dict):
        # Flatten all event types into a single list
        all_events = []
        for event_type, events_list in raw_events.items():
            if isinstance(events_list, list):
                all_events.extend(events_list)
            else:
                all_events.append(events_list)
        events_list = all_events
    elif isinstance(raw_events, list):
        events_list = raw_events
    else:
        raise ValueError(f"raw_events must be list or dict, got {type(raw_events)}")

    if not events_list:
        # Return empty DataFrame with expected schema
        return pd.DataFrame(
            columns=[
                "event_id",
                "match_id",
                "period",
                "timestamp",
                "type_name",
                "team_id",
                "team_name",
                "player_id",
                "player_name",
                "x",
                "y",
                "end_x",
                "end_y",
                "outcome",
            ]
        )

    # Normalize each event
    normalized = []
    for event in events_list:
        if not isinstance(event, dict):
            continue

        # Extract core fields
        # Use provided match_id or try to extract from event
        event_match_id = match_id if match_id is not None else _extract_match_id(event)
        
        normalized_event = {
            "event_id": event.get("id"),
            "match_id": event_match_id,
            "period": event.get("period"),
            "timestamp": event.get("timestamp"),
            "type_name": event.get("type", {}).get("name") if isinstance(event.get("type"), dict) else event.get("type"),
            "team_id": event.get("team", {}).get("id") if isinstance(event.get("team"), dict) else event.get("team"),
            "team_name": event.get("team", {}).get("name") if isinstance(event.get("team"), dict) else None,
            "player_id": event.get("player", {}).get("id") if isinstance(event.get("player"), dict) else event.get("player"),
            "player_name": event.get("player", {}).get("name") if isinstance(event.get("player"), dict) else None,
            "x": event.get("location", [None, None])[0] if isinstance(event.get("location"), list) and len(event.get("location", [])) > 0 else None,
            "y": event.get("location", [None, None])[1] if isinstance(event.get("location"), list) and len(event.get("location", [])) > 1 else None,
            "end_x": None,
            "end_y": None,
            "outcome": None,
        }

        # Extract end location if available
        if "end_location" in event and isinstance(event["end_location"], list):
            if len(event["end_location"]) > 0:
                normalized_event["end_x"] = event["end_location"][0]
            if len(event["end_location"]) > 1:
                normalized_event["end_y"] = event["end_location"][1]

        # Extract outcome if available
        if "outcome" in event:
            if isinstance(event["outcome"], dict):
                normalized_event["outcome"] = event["outcome"].get("name")
            else:
                normalized_event["outcome"] = event["outcome"]

        # Flatten additional attributes (for extensibility)
        # Add common event-specific fields
        if "pass" in event:
            pass_data = event["pass"]
            if isinstance(pass_data, dict):
                normalized_event["pass_type"] = pass_data.get("type", {}).get("name") if isinstance(pass_data.get("type"), dict) else pass_data.get("type")
                normalized_event["pass_outcome"] = pass_data.get("outcome", {}).get("name") if isinstance(pass_data.get("outcome"), dict) else pass_data.get("outcome")
                normalized_event["pass_length"] = pass_data.get("length")
                normalized_event["pass_angle"] = pass_data.get("angle")

        if "shot" in event:
            shot_data = event["shot"]
            if isinstance(shot_data, dict):
                normalized_event["shot_type"] = shot_data.get("type", {}).get("name") if isinstance(shot_data.get("type"), dict) else shot_data.get("type")
                normalized_event["shot_outcome"] = shot_data.get("outcome", {}).get("name") if isinstance(shot_data.get("outcome"), dict) else shot_data.get("outcome")
                normalized_event["shot_body_part"] = shot_data.get("body_part", {}).get("name") if isinstance(shot_data.get("body_part"), dict) else shot_data.get("body_part")

        if "dribble" in event:
            dribble_data = event["dribble"]
            if isinstance(dribble_data, dict):
                normalized_event["dribble_outcome"] = dribble_data.get("outcome", {}).get("name") if isinstance(dribble_data.get("outcome"), dict) else dribble_data.get("outcome")

        normalized.append(normalized_event)

    df = pd.DataFrame(normalized)

    # Ensure consistent dtypes
    if "event_id" in df.columns:
        df["event_id"] = df["event_id"].astype("string")
    if "match_id" in df.columns:
        df["match_id"] = df["match_id"].astype("Int64")
    if "period" in df.columns:
        df["period"] = df["period"].astype("Int64")
    if "team_id" in df.columns:
        df["team_id"] = df["team_id"].astype("Int64")
    if "player_id" in df.columns:
        df["player_id"] = df["player_id"].astype("Int64")
    if "x" in df.columns:
        df["x"] = df["x"].astype("float64")
    if "y" in df.columns:
        df["y"] = df["y"].astype("float64")
    if "end_x" in df.columns:
        df["end_x"] = df["end_x"].astype("float64")
    if "end_y" in df.columns:
        df["end_y"] = df["end_y"].astype("float64")

    return df


def _extract_match_id(event: dict) -> Union[int, None]:
    """Extract match_id from event dict.

    Match ID might be at the top level or nested in match_info.
    """
    if "match_id" in event:
        return event["match_id"]
    if "match" in event and isinstance(event["match"], dict):
        return event["match"].get("id")
    return None
