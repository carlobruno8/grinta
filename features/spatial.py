"""Spatial analysis features for tactical insights.

Analyzes the spatial distribution of team actions to reveal tactical patterns:
- Which flanks were targeted?
- Where did attacks concentrate?
- Spatial efficiency and coverage
"""
import pandas as pd
from typing import Dict, Optional


def attack_distribution_by_zone(
    events_df: pd.DataFrame,
    team_id: int
) -> Dict[str, Optional[float]]:
    """Analyze spatial distribution of team's attacking actions.
    
    Divides the pitch into zones and calculates where team focused attacks.
    Uses passes, carries, and shots in attacking half (x > 60).
    
    Pitch layout (StatsBomb coordinates):
    - X axis: 0 (own goal) to 120 (opponent goal)
    - Y axis: 0 (left touchline) to 80 (right touchline)
    
    Zones:
    - Left flank: y < 26.67 (left third)
    - Center: 26.67 <= y <= 53.33 (middle third)  
    - Right flank: y > 53.33 (right third)
    - Attacking half: x > 60
    - Final third: x > 80
    
    Args:
        events_df: Normalized events DataFrame
        team_id: Team ID to analyze
        
    Returns:
        Dictionary with spatial distribution metrics:
        - left_flank_attacks_pct: % of attacks down left (0-1)
        - center_attacks_pct: % of attacks through center (0-1)
        - right_flank_attacks_pct: % of attacks down right (0-1)
        - attacking_half_actions: Count of actions in attacking half
        - final_third_dominance: % of opponent's final third occupied
    """
    team_events = events_df[events_df["team_id"] == team_id].copy()
    
    # Filter to attacking actions with location data
    attacking_types = ["Pass", "Carry", "Dribble", "Shot"]
    attacking_events = team_events[
        team_events["type_name"].isin(attacking_types) &
        team_events["x"].notna() &
        team_events["y"].notna()
    ]
    
    if len(attacking_events) == 0:
        return {
            "left_flank_attacks_pct": None,
            "center_attacks_pct": None,
            "right_flank_attacks_pct": None,
            "attacking_half_actions": 0,
            "final_third_dominance": None,
        }
    
    # Filter to attacking half (x > 60)
    attacking_half = attacking_events[attacking_events["x"] > 60]
    attacking_half_count = len(attacking_half)
    
    if attacking_half_count == 0:
        return {
            "left_flank_attacks_pct": None,
            "center_attacks_pct": None,
            "right_flank_attacks_pct": None,
            "attacking_half_actions": 0,
            "final_third_dominance": None,
        }
    
    # Classify by flank (based on y-coordinate)
    # Y zones: 0-26.67 (left), 26.67-53.33 (center), 53.33-80 (right)
    left_flank = len(attacking_half[attacking_half["y"] < 26.67])
    center = len(attacking_half[(attacking_half["y"] >= 26.67) & (attacking_half["y"] <= 53.33)])
    right_flank = len(attacking_half[attacking_half["y"] > 53.33])
    
    total = left_flank + center + right_flank
    
    # Calculate percentages
    left_pct = left_flank / total if total > 0 else None
    center_pct = center / total if total > 0 else None
    right_pct = right_flank / total if total > 0 else None
    
    # Final third analysis (x > 80)
    final_third = attacking_half[attacking_half["x"] > 80]
    
    # Calculate "dominance" - what % of the final third width was covered?
    # Group by y-coordinate bins and measure spread
    if len(final_third) > 0:
        y_spread = final_third["y"].max() - final_third["y"].min()
        final_third_dominance = min(y_spread / 80, 1.0)  # Normalize to 0-1
    else:
        final_third_dominance = None
    
    return {
        "left_flank_attacks_pct": left_pct,
        "center_attacks_pct": center_pct,
        "right_flank_attacks_pct": right_pct,
        "attacking_half_actions": attacking_half_count,
        "final_third_dominance": final_third_dominance,
    }


def defensive_zone_activity(
    events_df: pd.DataFrame,
    team_id: int
) -> Dict[str, Optional[float]]:
    """Analyze where team performed defensive actions.
    
    Identifies pressure zones and defensive positioning.
    
    Args:
        events_df: Normalized events DataFrame
        team_id: Team ID to analyze
        
    Returns:
        Dictionary with defensive metrics:
        - high_press_actions: Defensive actions in opponent's half (x > 60)
        - low_block_actions: Defensive actions in own third (x < 40)
        - possession_losses_attacking_third: Times lost ball in attacking third
    """
    team_events = events_df[events_df["team_id"] == team_id].copy()
    
    # Defensive action types
    defensive_types = ["Pressure", "Tackle", "Interception", "Block", "Clearance", "Duel"]
    defensive_events = team_events[
        team_events["type_name"].isin(defensive_types) &
        team_events["x"].notna()
    ]
    
    # Count by zone
    high_press = len(defensive_events[defensive_events["x"] > 60])
    low_block = len(defensive_events[defensive_events["x"] < 40])
    
    # Possession losses (unsuccessful passes, dispossessions, etc.)
    loss_types = ["Dispossessed", "Miscontrol"]
    
    # Check if pass_outcome column exists
    if "pass_outcome" in team_events.columns:
        losses = team_events[
            (team_events["type_name"].isin(loss_types) | 
             ((team_events["type_name"] == "Pass") & (team_events["pass_outcome"].notna()))) &
            team_events["x"].notna()
        ]
    else:
        # Fallback if pass_outcome not available
        losses = team_events[
            team_events["type_name"].isin(loss_types) &
            team_events["x"].notna()
        ]
    
    losses_attacking_third = len(losses[losses["x"] > 80])
    
    return {
        "high_press_actions": high_press,
        "low_block_actions": low_block,
        "possession_losses_attacking_third": losses_attacking_third,
    }


def passing_concentration(
    events_df: pd.DataFrame,
    team_id: int
) -> Dict[str, Optional[float]]:
    """Analyze spatial concentration of passing.
    
    Determines if team's passing was spread across pitch or concentrated.
    
    Args:
        events_df: Normalized events DataFrame
        team_id: Team ID to analyze
        
    Returns:
        Dictionary with passing concentration metrics:
        - pass_width_spread: Std dev of pass y-coordinates (higher = more spread)
        - pass_depth_spread: Std dev of pass x-coordinates
        - back_passes_pct: % of passes backward (end_x < start_x)
    """
    team_passes = events_df[
        (events_df["team_id"] == team_id) &
        (events_df["type_name"] == "Pass") &
        events_df["x"].notna() &
        events_df["y"].notna() &
        events_df["end_x"].notna()
    ].copy()
    
    if len(team_passes) == 0:
        return {
            "pass_width_spread": None,
            "pass_depth_spread": None,
            "back_passes_pct": None,
        }
    
    # Calculate spread (standard deviation)
    width_spread = team_passes["y"].std()
    depth_spread = team_passes["x"].std()
    
    # Calculate backward passes
    backward = len(team_passes[team_passes["end_x"] < team_passes["x"]])
    back_passes_pct = backward / len(team_passes) if len(team_passes) > 0 else None
    
    return {
        "pass_width_spread": width_spread,
        "pass_depth_spread": depth_spread,
        "back_passes_pct": back_passes_pct,
    }
