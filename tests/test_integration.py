"""Integration tests for full pipeline."""
import os
import tempfile
from pathlib import Path
import pytest

from config import GrintaConfig
from ingestion import run_pipeline, run_match_events_pipeline


@pytest.mark.integration
def test_single_match_pipeline():
    """Test processing a single match."""
    # Use a known match ID from Champions League 2018/2019
    os.environ["GRINTA_COMPETITION_ID"] = "16"
    os.environ["GRINTA_SEASON_ID"] = "4"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config = GrintaConfig(
            competition_id=16,
            season_id=4,
            raw_dir=Path(tmpdir) / "raw",
            processed_dir=Path(tmpdir) / "processed",
            processed_format="parquet"
        )
        
        # First, get a real match ID
        from ingestion.loaders import load_matches
        matches = load_matches(16, 4)
        
        if isinstance(matches, dict):
            match_id = int(list(matches.keys())[0])
        else:
            match_id = matches[0]["match_id"]
        
        # Test single match pipeline
        result = run_match_events_pipeline(match_id, config=config)
        
        assert result.success, f"Pipeline failed: {result.errors}"
        assert len(result.saved_raw_paths) == 1
        assert len(result.saved_processed_paths) == 1
        
        # Verify files exist
        assert Path(result.saved_raw_paths[0]).exists()
        assert Path(result.saved_processed_paths[0]).exists()


@pytest.mark.integration
@pytest.mark.slow
def test_full_pipeline_small():
    """Test full pipeline with limited matches."""
    os.environ["GRINTA_COMPETITION_ID"] = "16"
    os.environ["GRINTA_SEASON_ID"] = "4"
    
    # Get matches first to find a few match IDs
    from ingestion.loaders import load_matches
    matches = load_matches(16, 4)
    
    if isinstance(matches, dict):
        match_ids = [int(mid) for mid in list(matches.keys())[:2]]  # Just 2 matches
    else:
        match_ids = [m["match_id"] for m in matches[:2]]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config = GrintaConfig(
            competition_id=16,
            season_id=4,
            match_ids=match_ids,  # Limit to 2 matches for testing
            raw_dir=Path(tmpdir) / "raw",
            processed_dir=Path(tmpdir) / "processed",
            processed_format="parquet"
        )
        
        result = run_pipeline(config=config)
        
        assert result.success, f"Pipeline failed: {result.errors}"
        # API may return 1 or 2 matches for this competition/season
        assert len(result.processed_match_ids) >= 1
        assert len(result.processed_match_ids) == len(result.saved_processed_paths)


@pytest.mark.integration
def test_cache_mode():
    """Test pipeline with use_cache=True."""
    os.environ["GRINTA_COMPETITION_ID"] = "16"
    os.environ["GRINTA_SEASON_ID"] = "4"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config = GrintaConfig(
            competition_id=16,
            season_id=4,
            raw_dir=Path(tmpdir) / "raw",
            processed_dir=Path(tmpdir) / "processed",
            processed_format="parquet"
        )
        
        # First run: fetch and save
        from ingestion.loaders import load_matches, load_events
        matches = load_matches(16, 4)
        
        if isinstance(matches, dict):
            match_id = int(list(matches.keys())[0])
        else:
            match_id = matches[0]["match_id"]
        
        # Save raw events first
        events = load_events(match_id)
        from ingestion.storage import save_events
        save_events(events, match_id, config.raw_dir)
        
        # Second run: use cache
        result = run_match_events_pipeline(match_id, config=config, use_cache=True)
        
        assert result.success, f"Cache mode failed: {result.errors}"
        assert len(result.saved_processed_paths) == 1
        # Should not have saved raw again (was already there)
        assert len(result.saved_raw_paths) == 0
