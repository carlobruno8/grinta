"""Question parser to extract match context from natural language."""
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path

import pandas as pd


def get_available_matches() -> Dict[int, Dict]:
    """Get metadata for all available matches.
    
    Returns:
        Dict mapping match_id to metadata (teams, date, etc.)
    """
    from features.utils import load_match_events
    from config import get_config
    
    config = get_config()
    processed_dir = Path(config.processed_dir)
    
    matches = {}
    for file_path in processed_dir.glob(f"events_*.{config.processed_format}"):
        try:
            match_id_str = file_path.stem.replace("events_", "")
            match_id = int(match_id_str)
            
            # Load a sample to get team names
            df = load_match_events(match_id, config=config)
            if not df.empty:
                teams = df[["team_id", "team_name"]].drop_duplicates()
                team_names = teams["team_name"].unique().tolist()
                
                matches[match_id] = {
                    "match_id": match_id,
                    "teams": team_names,
                    "file": str(file_path),
                }
        except Exception:
            continue
    
    return matches


def extract_team_names(question: str) -> List[str]:
    """Extract potential team names from question.
    
    Args:
        question: User's natural language question
        
    Returns:
        List of potential team names found
    """
    # Common team name patterns
    # This is a simple version - could be enhanced with a team database
    potential_teams = []
    
    # Look for capitalized words (potential team names)
    words = question.split()
    for i, word in enumerate(words):
        # Multi-word team names (e.g., "Manchester City", "Tottenham Hotspur")
        if i < len(words) - 1 and word[0].isupper():
            two_words = f"{word} {words[i+1]}"
            if words[i+1][0].isupper():
                potential_teams.append(two_words)
        
        # Single word team names
        if word[0].isupper() and len(word) > 3:
            potential_teams.append(word)
    
    return potential_teams


def find_match_by_teams(team_names: List[str], available_matches: Dict[int, Dict]) -> Optional[int]:
    """Find match ID by team names.
    
    Args:
        team_names: List of team names from question
        available_matches: Dict of available matches
        
    Returns:
        Match ID if found, None otherwise
    """
    for match_id, match_info in available_matches.items():
        match_teams = [t.lower() for t in match_info["teams"]]
        
        for team_name in team_names:
            team_lower = team_name.lower()
            # Check if team name matches any team in this match
            for match_team in match_teams:
                if team_lower in match_team or match_team in team_lower:
                    return match_id
    
    return None


def parse_time_reference(question: str) -> Tuple[Optional[int], Optional[float]]:
    """Extract time reference from question.
    
    Args:
        question: User's natural language question
        
    Returns:
        Tuple of (period, last_n_minutes)
    """
    question_lower = question.lower()
    
    # Check for period references
    period = None
    if "second half" in question_lower or "period 2" in question_lower:
        period = 2
    elif "first half" in question_lower or "period 1" in question_lower:
        period = 1
    elif "halftime" in question_lower or "after halftime" in question_lower:
        period = 2
    
    # Check for last N minutes
    last_n_minutes = None
    last_min_pattern = r"last\s+(\d+)\s+min"
    match = re.search(last_min_pattern, question_lower)
    if match:
        last_n_minutes = float(match.group(1))
    elif "late" in question_lower or "end of" in question_lower:
        last_n_minutes = 10.0
    
    return period, last_n_minutes


def parse_question(question: str) -> Dict:
    """Parse question to extract match context and time filters.
    
    Args:
        question: User's natural language question
        
    Returns:
        Dict with parsed components:
        - question: Original question
        - teams: Extracted team names
        - match_id: Identified match ID (if found)
        - period: Period filter (if specified)
        - last_n_minutes: Time window filter (if specified)
        - confidence: Confidence in match identification
    """
    # Get available matches
    available_matches = get_available_matches()
    
    # Extract team names
    team_names = extract_team_names(question)
    
    # Find matching match
    match_id = None
    if team_names:
        match_id = find_match_by_teams(team_names, available_matches)
    
    # If only one match available, use it
    if match_id is None and len(available_matches) == 1:
        match_id = list(available_matches.keys())[0]
    
    # Parse time references
    period, last_n_minutes = parse_time_reference(question)
    
    # Determine confidence
    confidence = "high" if team_names and match_id else "medium" if match_id else "low"
    
    return {
        "question": question,
        "teams": team_names,
        "match_id": match_id,
        "period": period,
        "last_n_minutes": last_n_minutes,
        "confidence": confidence,
        "available_matches": available_matches,
    }
