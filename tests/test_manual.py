"""Quick manual test of the ingestion pipeline."""
import os
import logging
from pathlib import Path

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Set test environment variables
os.environ["GRINTA_COMPETITION_ID"] = "16"  # Champions League
os.environ["GRINTA_SEASON_ID"] = "4"         # 2018/2019 season
# Optional: test with just one match
# os.environ["GRINTA_MATCH_ID"] = "22912"  # Example match ID

from ingestion import run_pipeline, get_ingestion_config

def test_pipeline():
    """Test the full pipeline."""
    print("=" * 60)
    print("Testing Ingestion Pipeline")
    print("=" * 60)
    
    # Get config
    try:
        config = get_ingestion_config()
        print(f"\n✓ Config loaded:")
        print(f"  Competition ID: {config.competition_id}")
        print(f"  Season ID: {config.season_id}")
        print(f"  Match IDs filter: {config.match_ids}")
        print(f"  Raw dir: {config.raw_dir}")
        print(f"  Processed dir: {config.processed_dir}")
        print(f"  Format: {config.processed_format}")
    except Exception as e:
        print(f"✗ Config failed: {e}")
        return
    
    # Run pipeline
    print(f"\n{'=' * 60}")
    print("Running pipeline...")
    print("=" * 60)
    
    result = run_pipeline(config)
    
    # Check results
    print(f"\n{'=' * 60}")
    print("Results:")
    print("=" * 60)
    print(f"Success: {result.success}")
    print(f"Processed matches: {len(result.processed_match_ids)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  - {error}")
    
    if result.saved_raw_paths:
        print(f"\n✓ Saved {len(result.saved_raw_paths)} raw files:")
        for path in result.saved_raw_paths[:5]:  # Show first 5
            print(f"  - {path}")
        if len(result.saved_raw_paths) > 5:
            print(f"  ... and {len(result.saved_raw_paths) - 5} more")
    
    if result.saved_processed_paths:
        print(f"\n✓ Saved {len(result.saved_processed_paths)} processed files:")
        for path in result.saved_processed_paths[:5]:
            print(f"  - {path}")
        if len(result.saved_processed_paths) > 5:
            print(f"  ... and {len(result.saved_processed_paths) - 5} more")
    
    # Verify files exist
    print(f"\n{'=' * 60}")
    print("Verifying files...")
    print("=" * 60)
    
    raw_dir = Path(config.raw_dir)
    processed_dir = Path(config.processed_dir)
    
    raw_files = list(raw_dir.glob("*.json"))
    processed_files = list(processed_dir.glob(f"*.{config.processed_format}"))
    
    print(f"Raw JSON files found: {len(raw_files)}")
    print(f"Processed files found: {len(processed_files)}")
    
    if processed_files:
        # Try loading one processed file
        import pandas as pd
        test_file = processed_files[0]
        print(f"\n✓ Testing load of: {test_file.name}")
        if config.processed_format == "parquet":
            df = pd.read_parquet(test_file)
        else:
            df = pd.read_csv(test_file)
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {list(df.columns)[:10]}...")  # First 10 columns
        print(f"  Sample row:\n{df.head(1).to_dict()}")

if __name__ == "__main__":
    test_pipeline()
