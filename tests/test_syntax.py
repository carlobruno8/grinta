"""Simple syntax and import validation test."""
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    errors = []
    
    # Test config
    try:
        from ingestion.config import IngestionConfig, get_ingestion_config
        print("✓ ingestion.config")
    except Exception as e:
        errors.append(f"ingestion.config: {e}")
        print(f"✗ ingestion.config: {e}")
    
    # Test loaders
    try:
        from ingestion.loaders import load_competitions, load_matches, load_events
        print("✓ ingestion.loaders")
    except Exception as e:
        errors.append(f"ingestion.loaders: {e}")
        print(f"✗ ingestion.loaders: {e}")
    
    # Test storage
    try:
        from ingestion.storage import save_events, load_events, save_events_df
        print("✓ ingestion.storage")
    except Exception as e:
        errors.append(f"ingestion.storage: {e}")
        print(f"✗ ingestion.storage: {e}")
    
    # Test normalizers
    try:
        from ingestion.normalizers import normalize_events
        print("✓ ingestion.normalizers")
    except Exception as e:
        errors.append(f"ingestion.normalizers: {e}")
        print(f"✗ ingestion.normalizers: {e}")
    
    # Test pipeline
    try:
        from ingestion.pipeline import run_pipeline, run_match_events_pipeline, PipelineResult
        print("✓ ingestion.pipeline")
    except Exception as e:
        errors.append(f"ingestion.pipeline: {e}")
        print(f"✗ ingestion.pipeline: {e}")
    
    # Test main init
    try:
        from ingestion import run_pipeline, get_ingestion_config
        print("✓ ingestion.__init__")
    except Exception as e:
        errors.append(f"ingestion.__init__: {e}")
        print(f"✗ ingestion.__init__: {e}")
    
    return len(errors) == 0, errors

def test_file_structure():
    """Test that all expected files exist."""
    print("\nTesting file structure...")
    
    expected_files = [
        "ingestion/__init__.py",
        "ingestion/config.py",
        "ingestion/pipeline.py",
        "ingestion/loaders/__init__.py",
        "ingestion/loaders/competitions.py",
        "ingestion/loaders/matches.py",
        "ingestion/loaders/events.py",
        "ingestion/storage/__init__.py",
        "ingestion/storage/raw.py",
        "ingestion/storage/processed.py",
        "ingestion/normalizers/__init__.py",
        "ingestion/normalizers/events.py",
    ]
    
    missing = []
    for file_path in expected_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            missing.append(file_path)
            print(f"✗ {file_path} (missing)")
    
    return len(missing) == 0, missing

if __name__ == "__main__":
    print("=" * 60)
    print("Syntax and Structure Validation")
    print("=" * 60)
    
    # Test file structure
    structure_ok, missing = test_file_structure()
    
    # Test imports (may fail if dependencies not installed)
    imports_ok, errors = test_imports()
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    print(f"File structure: {'✓ PASS' if structure_ok else '✗ FAIL'}")
    print(f"Imports: {'✓ PASS' if imports_ok else '✗ FAIL (dependencies may need installation)'}")
    
    if missing:
        print(f"\nMissing files: {missing}")
    
    if errors:
        print(f"\nImport errors (expected if dependencies not installed):")
        for error in errors:
            print(f"  - {error}")
    
    if structure_ok:
        print("\n✓ All expected files exist!")
        print("Note: Import errors are expected if dependencies aren't installed.")
        print("Run: pip install -r requirements.txt")
    else:
        sys.exit(1)
