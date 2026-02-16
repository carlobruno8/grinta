"""Test individual components of the ingestion pipeline."""
import os
import tempfile
from pathlib import Path

# Set test env vars
os.environ["GRINTA_COMPETITION_ID"] = "16"
os.environ["GRINTA_SEASON_ID"] = "4"

from ingestion.loaders import load_competitions, load_matches, load_events
from ingestion.storage import save_competitions, save_matches, save_events, load_events as load_events_cached
from ingestion.normalizers import normalize_events

def test_loaders():
    """Test that loaders can fetch data."""
    print("Testing loaders...")
    
    # Test competitions
    try:
        competitions = load_competitions()
        print(f"✓ Competitions loaded: {type(competitions)}")
        if isinstance(competitions, dict):
            print(f"  Found {len(competitions)} competitions")
        elif isinstance(competitions, list):
            print(f"  Found {len(competitions)} competitions")
    except Exception as e:
        print(f"✗ Competitions failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None
    
    # Test matches
    try:
        matches = load_matches(16, 4)
        print(f"✓ Matches loaded: {type(matches)}")
        if isinstance(matches, dict):
            print(f"  Found {len(matches)} matches")
            # Get first match ID for testing
            first_match_id = list(matches.keys())[0]
            if isinstance(first_match_id, str):
                first_match_id = int(first_match_id)
        elif isinstance(matches, list):
            print(f"  Found {len(matches)} matches")
            first_match_id = matches[0].get("match_id") or matches[0].get("id")
    except Exception as e:
        print(f"✗ Matches failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None
    
    # Test events (use first match)
    try:
        events = load_events(first_match_id)
        print(f"✓ Events loaded for match {first_match_id}: {type(events)}")
        if isinstance(events, list):
            print(f"  Found {len(events)} events")
        elif isinstance(events, dict):
            print(f"  Found {len(events)} event types")
    except Exception as e:
        print(f"✗ Events failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None
    
    return True, first_match_id, events

def test_storage(first_match_id, events):
    """Test storage save/load."""
    print("\nTesting storage...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_dir = Path(tmpdir) / "raw"
        raw_dir.mkdir()
        
        # Test save events
        try:
            save_path = save_events(events, first_match_id, raw_dir)
            print(f"✓ Saved events to: {save_path}")
            assert save_path.exists(), "File should exist"
        except Exception as e:
            print(f"✗ Save events failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test load events
        try:
            loaded = load_events_cached(first_match_id, raw_dir)
            print(f"✓ Loaded events from cache: {type(loaded)}")
            assert loaded is not None, "Should load data"
        except Exception as e:
            print(f"✗ Load events failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

def test_normalizer(events, match_id):
    """Test normalizer."""
    print("\nTesting normalizer...")
    
    try:
        df = normalize_events(events, match_id=match_id)
        print(f"✓ Normalized events: {df.shape}")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Column names: {list(df.columns)[:10]}...")
        
        # Check required columns exist
        required = ["event_id", "match_id", "period", "type_name", "team_id"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            print(f"✗ Missing columns: {missing}")
            return False
        else:
            print(f"✓ All required columns present")
        
        return True
    except Exception as e:
        print(f"✗ Normalizer failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Component Testing")
    print("=" * 60)
    
    # Test loaders
    loader_result = test_loaders()
    if not loader_result[0]:
        print("\n✗ Loader tests failed, stopping")
        exit(1)
    
    success, match_id, events = loader_result
    
    # Test storage
    if not test_storage(match_id, events):
        print("\n✗ Storage tests failed")
        exit(1)
    
    # Test normalizer
    if not test_normalizer(events, match_id):
        print("\n✗ Normalizer tests failed")
        exit(1)
    
    print("\n" + "=" * 60)
    print("✓ All component tests passed!")
    print("=" * 60)
