"""Metrics display component for showing team-level statistics."""
from typing import Any, Dict, List, Optional

import streamlit as st


def render_team_metrics_card(team_data: Dict[str, Any], col) -> None:
    """Render a single team's metrics in a card format.
    
    Args:
        team_data: Dict with team metrics (from features.aggregator)
        col: Streamlit column to render into
    """
    with col:
        # Team header
        st.subheader(team_data.get("team_name", "Unknown Team"))
        
        # Possession
        st.metric(
            label="Possession",
            value=f"{team_data.get('possession_share', 0) * 100:.1f}%",
        )
        
        # Passes
        passes = team_data.get("passes", 0)
        passes_ok = team_data.get("passes_successful", 0)
        pass_pct = team_data.get("pass_completion_pct")
        st.metric(
            label="Passes",
            value=f"{passes} ({passes_ok} successful)",
            delta=f"{pass_pct:.1f}% completion" if pass_pct is not None else None,
        )
        
        # Shots
        shots = team_data.get("shots", 0)
        sot = team_data.get("shots_on_target", 0)
        goals = team_data.get("goals", 0)
        st.metric(
            label="Shots",
            value=f"{shots} ({sot} on target)",
            delta=f"{goals} goals" if goals > 0 else None,
        )
        
        # Territory
        avg_x = team_data.get("avg_x", 0)
        avg_y = team_data.get("avg_y", 0)
        st.metric(
            label="Average Position",
            value=f"({avg_x:.1f}, {avg_y:.1f})",
        )
        
        # Final third
        final_third = team_data.get("final_third_entries", 0)
        st.metric(
            label="Final Third Entries",
            value=final_third,
        )


def render_segment_metrics(segment_data: Dict[str, Any], default_expanded: bool = True) -> None:
    """Render metrics for a single time segment (e.g., full match, period 2).
    
    Args:
        segment_data: Dict with segment, teams list, and totals
        default_expanded: Whether the expander should be open by default
    """
    segment_label = segment_data.get("segment", "Unknown Segment")
    teams = segment_data.get("teams", [])
    
    # Format segment label for display
    display_label = segment_label.replace("_", " ").title()
    
    with st.expander(f"📊 {display_label}", expanded=default_expanded):
        if len(teams) == 0:
            st.warning("No team data available for this segment.")
            return
        
        # Two-column layout for team comparison
        cols = st.columns(len(teams))
        
        for idx, team_data in enumerate(teams):
            render_team_metrics_card(team_data, cols[idx])
        
        # Optional: Show totals
        totals = segment_data.get("totals", {})
        if totals:
            st.caption(
                f"Match totals: {totals.get('total_passes', 0)} passes, "
                f"{totals.get('total_shots', 0)} shots"
            )


def render_metrics_display(metrics_data: Dict[str, Any]) -> None:
    """Render the full metrics display with multiple segments.
    
    Args:
        metrics_data: Result from get_match_metrics or get_match_metrics_multi_segment
    """
    st.header("📊 Match Metrics (Evidence)")
    st.markdown(
        "These metrics are computed from match events. "
        "All explanations must be grounded in this data."
    )
    
    # Check if multi-segment format
    if "segments" in metrics_data:
        # Multi-segment format: {"match_id": ..., "segments": [...]}
        segments = metrics_data.get("segments", [])
        
        if len(segments) == 0:
            st.warning("No metrics data available.")
            return
        
        # Render each segment
        for idx, segment in enumerate(segments):
            # Expand first segment by default
            render_segment_metrics(segment, default_expanded=(idx == 0))
    
    elif "segment" in metrics_data:
        # Single segment format
        render_segment_metrics(metrics_data, default_expanded=True)
    
    else:
        st.error("Invalid metrics data format.")


def render_metrics_placeholder() -> None:
    """Show a placeholder when no metrics are loaded yet."""
    st.header("📊 Match Metrics (Evidence)")
    st.info("👈 Select a match to view metrics")
