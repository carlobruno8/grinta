"""Match selection component for choosing competitions, seasons, and matches."""
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import streamlit as st


def get_available_matches() -> List[Dict[str, any]]:
    """Get list of available matches from processed data directory.
    
    Returns:
        List of dicts with match_id and filename info
    """
    # Get processed data directory from environment or default
    processed_dir = os.getenv("GRINTA_PROCESSED_DIR", "data/processed")
    processed_path = Path(processed_dir)
    
    if not processed_path.exists():
        return []
    
    matches = []
    # Look for events_*.parquet or events_*.csv files
    for file_path in processed_path.glob("events_*"):
        if file_path.suffix in [".parquet", ".csv"]:
            # Extract match_id from filename (e.g., events_22912.parquet)
            try:
                match_id_str = file_path.stem.replace("events_", "")
                match_id = int(match_id_str)
                matches.append({
                    "match_id": match_id,
                    "filename": file_path.name,
                    "path": str(file_path),
                })
            except ValueError:
                # Skip files that don't have numeric match IDs
                continue
    
    # Sort by match_id
    matches.sort(key=lambda x: x["match_id"])
    return matches


def render_match_selector() -> Optional[int]:
    """Render match selection UI and return selected match_id.
    
    Returns:
        Selected match_id or None if no selection
    """
    st.header("⚽ Match Selection")
    
    # Get available matches
    available_matches = get_available_matches()
    
    if len(available_matches) == 0:
        st.warning(
            "No processed match data found. "
            "Run the ingestion pipeline first to load match data."
        )
        st.code("python3 -m ingestion", language="bash")
        return None
    
    # Create options for selectbox
    match_options = {
        f"Match {m['match_id']}": m['match_id'] 
        for m in available_matches
    }
    
    # Add "Select a match" placeholder
    match_options_display = ["Select a match..."] + list(match_options.keys())
    
    # Selection UI
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_display = st.selectbox(
            "Choose a match:",
            options=match_options_display,
            help=f"Available matches with processed data ({len(available_matches)} total)",
        )
    
    with col2:
        st.metric(
            label="Available Matches",
            value=len(available_matches),
        )
    
    # Return match_id if valid selection
    if selected_display == "Select a match...":
        return None
    
    selected_match_id = match_options[selected_display]
    
    # Show match info
    with st.expander("ℹ️ Match Details", expanded=False):
        match_info = next(m for m in available_matches if m["match_id"] == selected_match_id)
        st.json(match_info)
    
    return selected_match_id


def render_match_selector_simple(available_match_ids: List[int]) -> Optional[int]:
    """Simplified match selector when you already have match IDs.
    
    Args:
        available_match_ids: List of match IDs to choose from
        
    Returns:
        Selected match_id or None
    """
    if len(available_match_ids) == 0:
        st.warning("No matches available.")
        return None
    
    selected = st.selectbox(
        "Select Match:",
        options=[None] + available_match_ids,
        format_func=lambda x: "Select a match..." if x is None else f"Match {x}",
    )
    
    return selected
