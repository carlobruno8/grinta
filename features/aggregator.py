"""Aggregate all team-level metrics into a single structure for reasoning."""
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from config import GrintaConfig, get_config
from features.metrics import (
    pass_counts_by_team,
    possession_share_from_passes,
    successful_pass_counts_by_team,
    shot_counts_by_team,
    shots_on_target_by_team,
    goals_by_team,
    average_position_by_team,
    final_third_entries_by_team,
)
from features.utils import load_match_events, filter_by_period, filter_last_n_minutes


def _team_id_to_name_map(df: pd.DataFrame) -> dict[int, str]:
    """Build team_id -> team_name from first occurrence in df."""
    if df.empty or "team_id" not in df.columns:
        return {}
    name_col = "team_name" if "team_name" in df.columns else None
    out = {}
    for _, row in df.drop_duplicates("team_id").iterrows():
        tid = row["team_id"]
        if pd.notna(tid):
            out[int(tid)] = str(row[name_col]) if name_col and pd.notna(row.get(name_col)) else f"Team_{tid}"
    return out


def compute_match_metrics(
    df: pd.DataFrame,
    segment_label: str = "full_match",
) -> dict[str, Any]:
    """Compute all team-level metrics for an events DataFrame (or segment).

    Args:
        df: Normalized events DataFrame (e.g. full match or time window).
        segment_label: Label for this segment (e.g. "full_match", "period_2", "last_10_min").

    Returns:
        Nested dict suitable for reasoning input:
        - segment: segment_label
        - teams: list of { team_id, team_name, possession_share, passes, passes_successful, ... }
        - totals: { total_passes, total_shots, ... } where useful
    """
    teams_map = _team_id_to_name_map(df)
    possession = possession_share_from_passes(df)
    pass_counts = pass_counts_by_team(df)
    pass_success = successful_pass_counts_by_team(df)
    shot_counts = shot_counts_by_team(df)
    shots_ot = shots_on_target_by_team(df)
    goals = goals_by_team(df)
    avg_pos = average_position_by_team(df)
    final_third = final_third_entries_by_team(df)

    team_ids = sorted(teams_map.keys())
    teams = []
    for tid in team_ids:
        name = teams_map.get(tid, f"Team_{tid}")
        pct = possession.get(str(tid), 0.0)
        passes = pass_counts.get(tid, 0)
        passes_ok = pass_success.get(tid, 0)
        pass_pct = (passes_ok / passes * 100) if passes else None
        shots = shot_counts.get(tid, 0)
        sot = shots_ot.get(tid, 0)
        g = goals.get(tid, 0)
        pos = avg_pos.get(tid, {})
        ft = final_third.get(tid, 0)
        teams.append({
            "team_id": tid,
            "team_name": name,
            "possession_share": round(pct, 4),
            "passes": passes,
            "passes_successful": passes_ok,
            "pass_completion_pct": round(pass_pct, 2) if pass_pct is not None else None,
            "shots": shots,
            "shots_on_target": sot,
            "goals": g,
            "avg_x": round(pos.get("avg_x", 0), 2),
            "avg_y": round(pos.get("avg_y", 0), 2),
            "final_third_entries": ft,
        })
    total_passes = sum(pass_counts.values())
    total_shots = sum(shot_counts.values())
    return {
        "segment": segment_label,
        "teams": teams,
        "totals": {
            "total_passes": total_passes,
            "total_shots": total_shots,
        },
    }


def get_match_metrics(
    match_id: int,
    *,
    period: Optional[int] = None,
    last_n_minutes: Optional[float] = None,
    config: Optional[GrintaConfig] = None,
) -> dict[str, Any]:
    """Load events for a match and compute metrics (optionally for a time window).

    Args:
        match_id: StatsBomb match ID.
        period: If set, restrict to this period only.
        last_n_minutes: If set, restrict to last N minutes (of the period or match).
        config: Override config for processed dir/format.

    Returns:
        Single segment: compute_match_metrics(...) result with segment label set.
    """
    if config is None:
        config = get_config()
    df = load_match_events(match_id, config=config)
    if period is not None:
        df = filter_by_period(df, period)
        segment_label = f"period_{period}"
    else:
        segment_label = "full_match"
    if last_n_minutes is not None:
        df = filter_last_n_minutes(df, last_n_minutes, period=period)
        segment_label = f"last_{int(last_n_minutes)}_min"
        if period is not None:
            segment_label = f"period_{period}_{segment_label}"
    return compute_match_metrics(df, segment_label=segment_label)


def get_match_metrics_multi_segment(
    match_id: int,
    segments: Optional[list[dict[str, Any]]] = None,
    config: Optional[GrintaConfig] = None,
) -> dict[str, Any]:
    """Get metrics for multiple segments (e.g. full match + period 2 + last 10 min).

    Args:
        match_id: StatsBomb match ID.
        segments: List of dicts with optional 'period', 'last_n_minutes'. If None, only full match.
        config: Override config.

    Returns:
        { "match_id": int, "segments": [ compute_match_metrics result, ... ] }
    """
    if config is None:
        config = get_config()
    df_full = load_match_events(match_id, config=config)
    result_segments = []
    # Full match
    result_segments.append(compute_match_metrics(df_full, segment_label="full_match"))
    if segments:
        for seg in segments:
            period = seg.get("period")
            last_n = seg.get("last_n_minutes")
            if period is not None:
                df = filter_by_period(df_full, period)
                label = f"period_{period}"
            else:
                df = df_full.copy()
                label = "full_match"
            if last_n is not None:
                df = filter_last_n_minutes(df, last_n, period=period)
                label = f"last_{int(last_n)}_min" + (f"_p{period}" if period else "")
            result_segments.append(compute_match_metrics(df, segment_label=label))
    return {"match_id": match_id, "segments": result_segments}
