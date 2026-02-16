"""High-level builder/orchestrator for the reasoning pipeline.

Connects features → input → LLM → validated output.
"""
from typing import Optional
from pathlib import Path

import pandas as pd

from config import GrintaConfig, get_config
from features.utils import load_match_events, filter_last_n_minutes, filter_first_n_minutes, filter_by_period
from features.metrics import (
    possession_share_from_passes,
    pass_counts_by_team,
    successful_pass_counts_by_team,
    shot_counts_by_team,
    shots_on_target_by_team,
    goals_by_team,
    average_position_by_team,
    final_third_entries_by_team,
)
from features import spatial

from reasoning.input_schema import (
    ReasoningInput, 
    TeamMetrics, 
    MatchContext, 
    TimeWindowContext
)
from reasoning.output_schema import ExplanationResponse
from reasoning.client import ReasoningClient, create_reasoning_client
from reasoning.prompts import build_user_prompt


def compute_team_metrics(
    events_df: pd.DataFrame,
    team_id: int,
    team_name: str
) -> TeamMetrics:
    """Compute all team-level metrics from events DataFrame.
    
    Args:
        events_df: Events DataFrame (possibly filtered by time window)
        team_id: Team ID to compute metrics for
        team_name: Team name
        
    Returns:
        TeamMetrics with all computed values
    """
    # Filter to this team's events
    team_events = events_df[events_df['team_id'] == team_id] if 'team_id' in events_df.columns else events_df
    
    # Compute possession metrics
    possession_shares = possession_share_from_passes(events_df)
    possession_share = possession_shares.get(str(team_id))
    
    pass_count_dict = pass_counts_by_team(events_df)
    pass_count = pass_count_dict.get(team_id)
    
    successful_passes_dict = successful_pass_counts_by_team(events_df)
    successful_passes = successful_passes_dict.get(team_id)
    
    # Compute shot metrics
    shot_count_dict = shot_counts_by_team(events_df)
    shot_count = shot_count_dict.get(team_id)
    
    shots_on_target_dict = shots_on_target_by_team(events_df)
    shots_on_target = shots_on_target_dict.get(team_id)
    
    goals_dict = goals_by_team(events_df)
    goals = goals_dict.get(team_id, 0)  # Default to 0 if no goals
    
    # Compute territory metrics
    avg_positions = average_position_by_team(events_df)
    avg_position = avg_positions.get(team_id, {})
    avg_position_x = avg_position.get('avg_x')
    avg_position_y = avg_position.get('avg_y')
    
    final_third_dict = final_third_entries_by_team(events_df)
    final_third_entries = final_third_dict.get(team_id)
    
    # Compute spatial distribution metrics (tactical insights)
    spatial_dist = spatial.attack_distribution_by_zone(events_df, team_id)
    left_flank_pct = spatial_dist.get('left_flank_attacks_pct')
    center_pct = spatial_dist.get('center_attacks_pct')
    right_flank_pct = spatial_dist.get('right_flank_attacks_pct')
    attacking_half_actions = spatial_dist.get('attacking_half_actions')
    
    # Compute defensive metrics
    defensive_metrics = spatial.defensive_zone_activity(events_df, team_id)
    high_press_actions = defensive_metrics.get('high_press_actions')
    low_block_actions = defensive_metrics.get('low_block_actions')
    
    # Compute passing patterns
    passing_patterns = spatial.passing_concentration(events_df, team_id)
    pass_width_spread = passing_patterns.get('pass_width_spread')
    back_passes_pct = passing_patterns.get('back_passes_pct')
    
    return TeamMetrics(
        team_id=team_id,
        team_name=team_name,
        possession_share=possession_share,
        pass_count=pass_count,
        successful_passes=successful_passes,
        shot_count=shot_count,
        shots_on_target=shots_on_target,
        goals=goals,
        avg_position_x=avg_position_x,
        avg_position_y=avg_position_y,
        final_third_entries=final_third_entries,
        # Spatial/tactical metrics
        left_flank_attacks_pct=left_flank_pct,
        center_attacks_pct=center_pct,
        right_flank_attacks_pct=right_flank_pct,
        attacking_half_actions=attacking_half_actions,
        high_press_actions=high_press_actions,
        low_block_actions=low_block_actions,
        pass_width_spread=pass_width_spread,
        back_passes_pct=back_passes_pct
    )


def apply_time_filter(
    events_df: pd.DataFrame,
    time_filter: Optional[str] = None
) -> tuple[pd.DataFrame, TimeWindowContext]:
    """Apply time window filter to events.
    
    Args:
        events_df: Full match events DataFrame
        time_filter: Optional filter string like "last_10_min", "period_2", "first_15_min"
        
    Returns:
        Tuple of (filtered DataFrame, TimeWindowContext)
    """
    if not time_filter:
        return events_df, TimeWindowContext(description="Full Match")
    
    # Parse filter string
    if time_filter.startswith("last_"):
        # e.g., "last_10_min"
        minutes = int(time_filter.split("_")[1])
        filtered_df = filter_last_n_minutes(events_df, minutes)
        return filtered_df, TimeWindowContext(
            description=f"Last {minutes} minutes",
            time_filter=time_filter
        )
    
    elif time_filter.startswith("first_"):
        # e.g., "first_15_min"
        minutes = int(time_filter.split("_")[1])
        filtered_df = filter_first_n_minutes(events_df, minutes)
        return filtered_df, TimeWindowContext(
            description=f"First {minutes} minutes",
            time_filter=time_filter
        )
    
    elif time_filter.startswith("period_"):
        # e.g., "period_2"
        period = int(time_filter.split("_")[1])
        filtered_df = filter_by_period(events_df, period)
        return filtered_df, TimeWindowContext(
            description=f"Period {period}",
            period=period,
            time_filter=time_filter
        )
    
    else:
        # Unknown filter, return full match
        return events_df, TimeWindowContext(
            description="Full Match (unknown filter ignored)"
        )


def extract_teams_from_events(events_df: pd.DataFrame) -> list[tuple[int, str]]:
    """Extract team IDs and names from events DataFrame.
    
    Args:
        events_df: Events DataFrame with team_id and team_name columns
        
    Returns:
        List of (team_id, team_name) tuples
    """
    if events_df.empty or 'team_id' not in events_df.columns:
        return []
    
    teams = events_df[['team_id', 'team_name']].drop_duplicates()
    return [(int(row['team_id']), str(row['team_name'])) for _, row in teams.iterrows()]


def generate_explanation(
    match_id: int,
    question: str,
    time_filter: Optional[str] = None,
    config: Optional[GrintaConfig] = None,
    client: Optional[ReasoningClient] = None
) -> ExplanationResponse:
    """Generate an explanation for a match question.
    
    This is the main entry point for the reasoning pipeline.
    
    Args:
        match_id: StatsBomb match ID
        question: User's question about the match
        time_filter: Optional time filter (e.g., "last_10_min", "period_2")
        config: Optional configuration (for data paths and LLM settings)
        client: Optional pre-configured reasoning client
        
    Returns:
        ExplanationResponse with structured explanation
        
    Raises:
        FileNotFoundError: If match events file not found
        ValueError: If data is invalid or API call fails
    """
    # Use shared config for both features and reasoning
    if config is None:
        config = get_config()
    
    # 1. Load match events
    events_df = load_match_events(match_id, config=config)
    
    # 2. Apply time filter
    filtered_df, time_context = apply_time_filter(events_df, time_filter)
    
    # 3. Extract teams
    teams_list = extract_teams_from_events(filtered_df)
    if not teams_list:
        raise ValueError(f"No teams found in match {match_id} events")
    
    # 4. Compute metrics for each team
    team_metrics = []
    for team_id, team_name in teams_list:
        metrics = compute_team_metrics(filtered_df, team_id, team_name)
        team_metrics.append(metrics)
    
    # 5. Build match context
    # Try to infer home/away from team order (first team is typically home)
    home_team = teams_list[0][1] if len(teams_list) > 0 else "Unknown"
    away_team = teams_list[1][1] if len(teams_list) > 1 else "Unknown"
    
    match_context = MatchContext(
        match_id=match_id,
        home_team=home_team,
        away_team=away_team
    )
    
    # 6. Build reasoning input
    reasoning_input = ReasoningInput(
        match_context=match_context,
        time_window=time_context,
        team_metrics=team_metrics,
        question=question
    )
    
    # 7. Build user prompt
    user_prompt = build_user_prompt(reasoning_input)
    
    # 8. Call LLM
    if client is None:
        client = create_reasoning_client(config)
    
    explanation_response = client.generate_explanation(user_prompt)
    
    return explanation_response


def explain_match(
    match_id: int,
    question: str,
    time_filter: Optional[str] = None
) -> dict:
    """Convenience function to generate explanation and return as dict.
    
    Args:
        match_id: StatsBomb match ID
        question: User's question
        time_filter: Optional time filter
        
    Returns:
        Explanation as dictionary
    """
    response = generate_explanation(match_id, question, time_filter)
    return response.to_dict()
