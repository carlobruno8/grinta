# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added - Ingestion Pipeline (Phase 1)

#### Core Implementation
- **Ingestion Pipeline**: Complete modular pipeline for StatsBomb data ingestion
  - `ingestion/config.py`: Configuration management with environment variable support
  - `ingestion/loaders/`: StatsBomb API loaders (competitions, matches, events)
  - `ingestion/storage/`: Raw JSON and processed DataFrame storage
  - `ingestion/normalizers/`: Event normalization to structured DataFrame
  - `ingestion/pipeline.py`: Orchestration pipeline with error handling

#### Features
- Load competitions, matches, and events from StatsBomb Open Data
- Save raw JSON files to `data/raw/` with deterministic naming
- Normalize events to pandas DataFrame with stable schema
- Save processed data as Parquet or CSV to `data/processed/`
- Support for cache mode (skip API calls, use existing raw files)
- Configurable via environment variables

#### Testing
- Comprehensive test suite:
  - `tests/test_syntax.py`: Structure and import validation
  - `tests/test_components.py`: Component-level testing with real API
  - `tests/test_manual.py`: Full pipeline end-to-end test
  - `tests/test_ingestion.py`: Unit tests with pytest
  - `tests/test_integration.py`: Integration tests
  - `tests/scripts/run_tests.sh`: Automated test runner

#### Documentation
- `README.md`: Project overview and quick start guide
- `TESTING.md`: Comprehensive testing documentation
- `docs/INSTALL.md`: Installation instructions
- `docs/project_context.md`: Architecture and design philosophy
- `docs/CHANGELOG.md`: This file

#### Configuration
- `.gitignore`: Updated to exclude test artifacts, data files, and cache
- `requirements.txt`: All project dependencies

### Technical Details

#### Data Schema
- Event normalization produces DataFrame with:
  - Core fields: `event_id` (UUID string), `match_id`, `period`, `timestamp`, `type_name`
  - Team fields: `team_id`, `team_name`
  - Player fields: `player_id`, `player_name` (nullable)
  - Location fields: `x`, `y`, `end_x`, `end_y`
  - Event-specific fields: `pass_type`, `shot_type`, `dribble_outcome`, etc.

#### Supported Data Sources
- StatsBomb Open Data (free, public dataset)
- Champions League, Premier League, La Liga, World Cup, Euro, etc.
- Historical seasons from various competitions

### Known Limitations
- Competitions loading has minor JSON serialization warning (non-critical)
- Currently supports team-level analysis only (Phase 1 scope)
