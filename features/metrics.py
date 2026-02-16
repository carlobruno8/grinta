"""Team-level metrics computation from event data.

All metric functions take a pandas DataFrame of events and return aggregated team-level stats.
Functions are grouped by category: possession, shots, territory, and spatial/tactical.
"""
import pandas as pd


# ==============================================================================
# POSSESSION METRICS
# ==============================================================================

def possession_share_from_passes(df: pd.DataFrame) -> dict[str, float]:
    """Possession share by team using pass counts as proxy.

    Each team's share = (team passes) / (total passes). Ties yield 0.5 each.

    Args:
        df: Events DataFrame with team_id and type_name.

    Returns:
        Dict mapping team_id (as string) to share in [0, 1].
    """
    if df.empty or "team_id" not in df.columns or "type_name" not in df.columns:
        return {}
    passes = df[df["type_name"] == "Pass"].copy()
    if passes.empty:
        return {}
    counts = passes["team_id"].value_counts()
    total = counts.sum()
    if total == 0:
        return {}
    return {str(tid): count / total for tid, count in counts.items()}


def ball_receipts_by_team(df: pd.DataFrame) -> dict[int, int]:
    """Count ball receipt events by team_id."""
    if df.empty or "team_id" not in df.columns or "type_name" not in df.columns:
        return {}
    receipts = df[df["type_name"] == "Ball Receipt"]
    return receipts["team_id"].value_counts().to_dict()


def pass_counts_by_team(df: pd.DataFrame) -> dict[int, int]:
    """Count pass events by team_id."""
    if df.empty or "team_id" not in df.columns or "type_name" not in df.columns:
        return {}
    passes = df[df["type_name"] == "Pass"]
    return passes["team_id"].value_counts().to_dict()


def successful_pass_counts_by_team(df: pd.DataFrame) -> dict[int, int]:
    """Count successful passes (no outcome or outcome Complete) by team."""
    if df.empty or "team_id" not in df.columns or "type_name" not in df.columns:
        return {}
    passes = df[df["type_name"] == "Pass"].copy()
    if passes.empty:
        return {}
    if "pass_outcome" in passes.columns:
        successful = passes[passes["pass_outcome"].isna() | (passes["pass_outcome"] == "Complete")]
    else:
        successful = passes
    return successful["team_id"].value_counts().to_dict()


# ==============================================================================
# SHOT METRICS
# ==============================================================================

def shot_counts_by_team(df: pd.DataFrame) -> dict[int, int]:
    """Count shot events by team_id."""
    if df.empty or "team_id" not in df.columns or "type_name" not in df.columns:
        return {}
    shots = df[df["type_name"] == "Shot"]
    return shots["team_id"].value_counts().to_dict()


def shots_on_target_by_team(df: pd.DataFrame) -> dict[int, int]:
    """Count shots with outcome 'Saved' or 'Goal' (on target) by team."""
    if df.empty or "team_id" not in df.columns or "type_name" not in df.columns:
        return {}
    shots = df[df["type_name"] == "Shot"].copy()
    if shots.empty:
        return {}
    if "shot_outcome" not in shots.columns:
        return shot_counts_by_team(df)
    on_target = shots[shots["shot_outcome"].isin(["Saved", "Goal"])]
    return on_target["team_id"].value_counts().to_dict()


def goals_by_team(df: pd.DataFrame) -> dict[int, int]:
    """Count goals (shot outcome = Goal) by team."""
    if df.empty or "team_id" not in df.columns or "type_name" not in df.columns:
        return {}
    shots = df[df["type_name"] == "Shot"].copy()
    if shots.empty or "shot_outcome" not in shots.columns:
        return {tid: 0 for tid in shots["team_id"].unique()}
    goals = shots[shots["shot_outcome"] == "Goal"]
    return goals["team_id"].value_counts().to_dict()


# ==============================================================================
# TERRITORY METRICS
# ==============================================================================

def average_position_by_team(df: pd.DataFrame) -> dict[int, dict[str, float]]:
    """Average (x, y) position of events by team. Uses start location (x, y)."""
    if df.empty or "team_id" not in df.columns:
        return {}
    has_xy = df["x"].notna() & df["y"].notna()
    valid = df.loc[has_xy]
    if valid.empty:
        return {}
    out = {}
    for tid in valid["team_id"].dropna().unique():
        team_events = valid[valid["team_id"] == tid]
        out[int(tid)] = {
            "avg_x": float(team_events["x"].mean()),
            "avg_y": float(team_events["y"].mean()),
        }
    return out


def final_third_entries_by_team(df: pd.DataFrame) -> dict[int, int]:
    """Count events with x >= 80 (attacking third) by team. Simple proxy for pressure in final third."""
    if df.empty or "team_id" not in df.columns or "x" not in df.columns:
        return {}
    valid = df[df["x"].notna() & (df["x"] >= 80)]
    return valid["team_id"].value_counts().to_dict()


# ==============================================================================
# SPATIAL / TACTICAL METRICS
# ==============================================================================
# Note: spatial.py is kept separate as it contains more complex spatial analysis
# Import it directly: from features import spatial
