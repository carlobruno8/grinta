"""Storage for raw JSON data files."""
import json
from pathlib import Path
from typing import Union


def save_competitions(data: Union[list, dict], raw_dir: Path) -> Path:
    """Save competitions data to JSON file.

    Args:
        data: Competitions data (list or dict)
        raw_dir: Directory to save the file

    Returns:
        Path to the saved file
    """
    raw_dir.mkdir(parents=True, exist_ok=True)
    filepath = raw_dir / "competitions.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filepath


def save_matches(data: dict, competition_id: int, season_id: int, raw_dir: Path) -> Path:
    """Save matches data to JSON file.

    Args:
        data: Matches data (dict)
        competition_id: Competition ID for filename
        season_id: Season ID for filename
        raw_dir: Directory to save the file

    Returns:
        Path to the saved file
    """
    raw_dir.mkdir(parents=True, exist_ok=True)
    filepath = raw_dir / f"matches_{competition_id}_{season_id}.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filepath


def save_events(data: Union[list, dict], match_id: int, raw_dir: Path) -> Path:
    """Save events data to JSON file.

    Args:
        data: Events data (list or dict)
        match_id: Match ID for filename
        raw_dir: Directory to save the file

    Returns:
        Path to the saved file
    """
    raw_dir.mkdir(parents=True, exist_ok=True)
    filepath = raw_dir / f"events_{match_id}.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filepath


def load_matches(competition_id: int, season_id: int, raw_dir: Path) -> dict:
    """Load matches data from JSON file.

    Args:
        competition_id: Competition ID for filename
        season_id: Season ID for filename
        raw_dir: Directory containing the file

    Returns:
        Matches data as dict

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    filepath = raw_dir / f"matches_{competition_id}_{season_id}.json"

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_events(match_id: int, raw_dir: Path) -> Union[list, dict]:
    """Load events data from JSON file.

    Args:
        match_id: Match ID for filename
        raw_dir: Directory containing the file

    Returns:
        Events data as list or dict

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    filepath = raw_dir / f"events_{match_id}.json"

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
