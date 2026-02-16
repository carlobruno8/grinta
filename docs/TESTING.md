# Testing Guide for Grinta Ingestion Pipeline

This document explains how to test the ingestion pipeline.

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify StatsBomb connection:**
   ```python
   import statsbombpy.sb as sb
   comps = sb.competitions()
   print(comps.head())
   ```

## Test Files

### 1. `test_syntax.py` - Structure Validation
**Purpose:** Validates that all files exist and can be imported (if dependencies installed)

**Run:**
```bash
python3 tests/test_syntax.py
```

**What it checks:**
- All expected files exist
- Modules can be imported (requires dependencies)

---

### 2. `test_components.py` - Component Testing
**Purpose:** Tests individual components (loaders, storage, normalizers) with real StatsBomb API calls

**Run:**
```bash
python3 tests/test_components.py
```

**What it tests:**
- `load_competitions()` - Fetches competitions from StatsBomb
- `load_matches()` - Fetches matches for a competition+season
- `load_events()` - Fetches events for a match
- `save_events()` / `load_events()` - Storage save/load
- `normalize_events()` - Event normalization to DataFrame

**Requirements:** Network access (calls StatsBomb API)

---

### 3. `test_manual.py` - Full Pipeline Test
**Purpose:** End-to-end test of the complete pipeline

**Run:**
```bash
# Set environment variables
export GRINTA_COMPETITION_ID=16  # Champions League
export GRINTA_SEASON_ID=4        # 2018/2019

# Or edit tests/test_manual.py to set them

python3 tests/test_manual.py
```

**What it tests:**
- Full pipeline execution
- Config loading from environment
- Data fetching and saving
- Normalization and processed file creation
- File verification

**Requirements:** Network access

**Note:** This will download and process real data. For a quick test, uncomment the `GRINTA_MATCH_ID` line in the script to test just one match.

---

### 4. `tests/test_ingestion.py` - Unit Tests (pytest)
**Purpose:** Unit tests for individual functions with mocked data

**Run:**
```bash
pytest tests/test_ingestion.py -v
```

**What it tests:**
- Config creation and validation
- Storage save/load functions
- Normalizer with various event formats
- Edge cases (empty events, missing fields, etc.)

**Requirements:** pytest installed (`pip install pytest`)

**Advantages:**
- Fast (no network calls)
- Tests edge cases
- Can run in CI/CD

---

### 5. `tests/test_integration.py` - Integration Tests (pytest)
**Purpose:** Full pipeline integration tests with real API calls

**Run:**
```bash
# Run all integration tests
pytest tests/test_integration.py -v -m integration

# Run only fast integration tests (skip slow ones)
pytest tests/test_integration.py -v -m integration -m "not slow"
```

**What it tests:**
- Single match pipeline
- Full pipeline with multiple matches
- Cache mode (load from existing files)

**Requirements:** 
- pytest installed
- Network access
- Can be slow (downloads real data)

---

## Test Execution Order

**Recommended order:**

1. **Quick validation:**
   ```bash
   python3 test_syntax.py
   ```
   ✓ Verifies file structure

2. **Component tests:**
   ```bash
   python3 test_components.py
   ```
   ✓ Tests each piece individually

3. **Unit tests:**
   ```bash
   pytest tests/test_ingestion.py -v
   ```
   ✓ Fast, comprehensive unit tests

4. **Manual pipeline test:**
   ```bash
   python3 test_manual.py
   ```
   ✓ Full end-to-end test

5. **Integration tests (optional):**
   ```bash
   pytest tests/test_integration.py -v -m integration
   ```
   ✓ Full integration tests (slower)

---

## Expected Test Results

### test_syntax.py
```
File structure: ✓ PASS
Imports: ✓ PASS (if dependencies installed)
```

### test_components.py
```
✓ Competitions loaded
✓ Matches loaded
✓ Events loaded
✓ Saved events
✓ Loaded events from cache
✓ Normalized events
✓ All component tests passed!
```

### test_manual.py
```
Success: True
Processed matches: X
Errors: 0
✓ Saved X raw files
✓ Saved X processed files
Raw JSON files found: X
Processed files found: X
```

### pytest tests
```
tests/test_ingestion.py::TestConfig::test_ingestion_config_creation PASSED
tests/test_ingestion.py::TestStorage::test_save_and_load_events PASSED
...
```

---

## Troubleshooting

### Import Errors
**Problem:** `ModuleNotFoundError: No module named 'dotenv'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Network Errors
**Problem:** StatsBomb API calls fail

**Solutions:**
- Check internet connection
- Verify StatsBomb API is accessible
- Try a different competition/season ID

### File Not Found Errors
**Problem:** `FileNotFoundError` when loading from cache

**Solution:** Run pipeline without `use_cache=True` first to create the files

### pytest Not Found
**Problem:** `No module named pytest`

**Solution:**
```bash
pip install pytest
```

---

## Test Data

Tests use real StatsBomb open data:
- **Competition ID 16:** Champions League
- **Season ID 4:** 2018/2019 season

You can change these in the test files or via environment variables.

---

## Continuous Integration

For CI/CD, run:
```bash
# Fast tests only (no network)
pytest tests/test_ingestion.py -v

# With network (if available)
pytest tests/test_integration.py -v -m integration
```
