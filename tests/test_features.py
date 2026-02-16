"""Unit tests for features module."""
import pytest
import pandas as pd

from features.aggregator import compute_match_metrics
from features.metrics import possession_share_from_passes, pass_counts_by_team, shot_counts_by_team, goals_by_team
from features.utils import filter_by_period, filter_last_n_minutes, _timestamp_to_seconds


class TestTimeWindows:
    def test_timestamp_to_seconds(self):
        assert _timestamp_to_seconds("00:00:00.000") == 0.0
        assert _timestamp_to_seconds("00:01:30.000") == 90.0
        assert _timestamp_to_seconds("00:45:00.000") == 45 * 60

    def test_filter_by_period(self):
        df = pd.DataFrame({"period": [1, 1, 2, 2], "type_name": ["Pass", "Pass", "Shot", "Pass"]})
        out = filter_by_period(df, 2)
        assert len(out) == 2
        assert out["period"].unique().tolist() == [2]


class TestPossession:
    def test_possession_share_two_teams(self):
        df = pd.DataFrame({
            "team_id": [1, 1, 1, 2, 2],
            "type_name": ["Pass", "Pass", "Pass", "Pass", "Pass"],
        })
        share = possession_share_from_passes(df)
        assert share["1"] == pytest.approx(0.6)
        assert share["2"] == pytest.approx(0.4)

    def test_pass_counts_by_team(self):
        df = pd.DataFrame({
            "team_id": [1, 1, 2],
            "type_name": ["Pass", "Pass", "Pass"],
        })
        counts = pass_counts_by_team(df)
        assert counts[1] == 2
        assert counts[2] == 1


class TestShots:
    def test_shot_counts_by_team(self):
        df = pd.DataFrame({
            "team_id": [1, 1, 2],
            "type_name": ["Shot", "Shot", "Shot"],
        })
        counts = shot_counts_by_team(df)
        assert counts[1] == 2
        assert counts[2] == 1

    def test_goals_by_team(self):
        df = pd.DataFrame({
            "team_id": [1, 2],
            "type_name": ["Shot", "Shot"],
            "shot_outcome": ["Goal", "Saved"],
        })
        goals = goals_by_team(df)
        assert goals.get(1) == 1
        assert goals.get(2, 0) == 0  # team 2 has no goals so may be absent


class TestAggregator:
    def test_compute_match_metrics_empty_df(self):
        df = pd.DataFrame(columns=["team_id", "team_name", "type_name", "x", "y"])
        out = compute_match_metrics(df, segment_label="test")
        assert out["segment"] == "test"
        assert out["teams"] == []
        assert out["totals"]["total_passes"] == 0
        assert out["totals"]["total_shots"] == 0

    def test_compute_match_metrics_two_teams(self):
        df = pd.DataFrame([
            {"team_id": 1, "team_name": "Team A", "type_name": "Pass", "x": 60, "y": 40},
            {"team_id": 1, "team_name": "Team A", "type_name": "Pass", "x": 61, "y": 41},
            {"team_id": 2, "team_name": "Team B", "type_name": "Pass", "x": 50, "y": 50},
            {"team_id": 1, "team_name": "Team A", "type_name": "Shot", "x": 100, "y": 50},
        ])
        out = compute_match_metrics(df, segment_label="full_match")
        assert out["segment"] == "full_match"
        assert len(out["teams"]) == 2
        team_a = next(t for t in out["teams"] if t["team_name"] == "Team A")
        team_b = next(t for t in out["teams"] if t["team_name"] == "Team B")
        assert team_a["passes"] == 2
        assert team_b["passes"] == 1
        assert team_a["possession_share"] == pytest.approx(2 / 3, rel=1e-3)
        assert team_a["shots"] == 1
        assert out["totals"]["total_passes"] == 3
        assert out["totals"]["total_shots"] == 1
