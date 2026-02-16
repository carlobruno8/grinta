"""Unit tests for ingestion pipeline."""
import os
import tempfile
from pathlib import Path
import pytest
import pandas as pd

from ingestion.config import IngestionConfig, get_ingestion_config
from ingestion.storage import save_events, load_events, save_events_df, load_events_df
from ingestion.normalizers import normalize_events


class TestConfig:
    """Test configuration module."""
    
    def test_ingestion_config_creation(self):
        """Test creating IngestionConfig."""
        config = IngestionConfig(
            competition_id=16,
            season_id=4,
            match_ids=[123, 456],
            raw_dir=Path("test_raw"),
            processed_dir=Path("test_processed"),
            processed_format="parquet"
        )
        assert config.competition_id == 16
        assert config.season_id == 4
        assert config.match_ids == [123, 456]
        assert config.processed_format == "parquet"
    
    def test_ingestion_config_validation(self):
        """Test format validation."""
        with pytest.raises(ValueError):
            IngestionConfig(
                competition_id=16,
                season_id=4,
                processed_format="invalid"
            )
    
    def test_get_ingestion_config_from_env(self):
        """Test loading config from environment."""
        os.environ["GRINTA_COMPETITION_ID"] = "16"
        os.environ["GRINTA_SEASON_ID"] = "4"
        
        config = get_ingestion_config()
        assert config.competition_id == 16
        assert config.season_id == 4


class TestStorage:
    """Test storage modules."""
    
    def test_save_and_load_events(self):
        """Test saving and loading events."""
        test_events = [
            {"id": 1, "type": {"name": "Pass"}, "period": 1},
            {"id": 2, "type": {"name": "Shot"}, "period": 2}
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_dir = Path(tmpdir)
            
            # Save
            save_path = save_events(test_events, match_id=123, raw_dir=raw_dir)
            assert save_path.exists()
            assert save_path.name == "events_123.json"
            
            # Load
            loaded = load_events(match_id=123, raw_dir=raw_dir)
            assert loaded == test_events
    
    def test_save_and_load_processed_df(self):
        """Test saving and loading processed DataFrame."""
        df = pd.DataFrame({
            "event_id": [1, 2],
            "match_id": [123, 123],
            "type_name": ["Pass", "Shot"]
        })
        
        with tempfile.TemporaryDirectory() as tmpdir:
            processed_dir = Path(tmpdir)
            
            # Save as parquet
            save_path = save_events_df(df, match_id=123, processed_dir=processed_dir, fmt="parquet")
            assert save_path.exists()
            
            # Load
            loaded = load_events_df(match_id=123, processed_dir=processed_dir, fmt="parquet")
            assert len(loaded) == 2
            assert list(loaded.columns) == ["event_id", "match_id", "type_name"]
    
    def test_save_and_load_processed_df_csv(self):
        """Test saving and loading processed DataFrame as CSV."""
        df = pd.DataFrame({
            "event_id": [1, 2],
            "match_id": [123, 123],
            "type_name": ["Pass", "Shot"]
        })
        
        with tempfile.TemporaryDirectory() as tmpdir:
            processed_dir = Path(tmpdir)
            
            # Save as CSV
            save_path = save_events_df(df, match_id=123, processed_dir=processed_dir, fmt="csv")
            assert save_path.exists()
            assert save_path.suffix == ".csv"
            
            # Load
            loaded = load_events_df(match_id=123, processed_dir=processed_dir, fmt="csv")
            assert len(loaded) == 2
            assert list(loaded.columns) == ["event_id", "match_id", "type_name"]


class TestNormalizer:
    """Test normalizer module."""
    
    def test_normalize_events_list(self):
        """Test normalizing list of events."""
        events = [
            {
                "id": 1,
                "period": 1,
                "timestamp": "00:00:15.123",
                "type": {"name": "Pass"},
                "team": {"id": 1, "name": "Team A"},
                "player": {"id": 10, "name": "Player X"},
                "location": [60.0, 40.0]
            }
        ]
        
        df = normalize_events(events, match_id=123)
        
        assert len(df) == 1
        assert df["event_id"].iloc[0] == 1
        assert df["match_id"].iloc[0] == 123
        assert df["type_name"].iloc[0] == "Pass"
        assert df["team_id"].iloc[0] == 1
        assert df["x"].iloc[0] == 60.0
    
    def test_normalize_events_dict(self):
        """Test normalizing dict of events by type."""
        events = {
            "Pass": [
                {"id": 1, "period": 1, "type": {"name": "Pass"}},
            ],
            "Shot": [
                {"id": 2, "period": 1, "type": {"name": "Shot"}},
            ]
        }
        
        df = normalize_events(events, match_id=123)
        
        assert len(df) == 2
        assert set(df["type_name"].unique()) == {"Pass", "Shot"}
    
    def test_normalize_empty_events(self):
        """Test normalizing empty events list."""
        events = []
        df = normalize_events(events, match_id=123)
        
        assert len(df) == 0
        # Should still have expected columns
        expected_cols = ["event_id", "match_id", "period", "timestamp", "type_name"]
        for col in expected_cols:
            assert col in df.columns
    
    def test_normalize_events_with_end_location(self):
        """Test normalizing events with end_location."""
        events = [
            {
                "id": 1,
                "period": 1,
                "type": {"name": "Pass"},
                "location": [60.0, 40.0],
                "end_location": [80.0, 50.0]
            }
        ]
        
        df = normalize_events(events, match_id=123)
        
        assert len(df) == 1
        assert df["end_x"].iloc[0] == 80.0
        assert df["end_y"].iloc[0] == 50.0
