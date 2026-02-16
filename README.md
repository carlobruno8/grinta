# Grinta

A football analytics reasoning engine that explains match outcomes using structured, evidence-based analysis.

> **Grinta does not predict results. It explains them.**

## Overview

Grinta generates grounded, auditable explanations using only provided metrics. The system enforces strict evidence-based reasoning with no hallucinated metrics.

### Core Principles

1. **Evidence > Fluency** - All claims must map to computed data
2. **No hallucinated metrics** - Only metrics computed from ingested data
3. **Uncertainty must be explicitly stated** - Confidence must be calibrated
4. **All claims must be auditable** - Trace explanations back to source data

## Architecture

```
data/raw/         → raw StatsBomb JSON
data/processed/   → cleaned event-level data

ingestion/        → data loading + normalization
features/         → team-level metric computation
reasoning/        → schemas, contracts, system prompt
app/              → Streamlit UI
```

## Phase 1: Team-Level Explanations

Currently focused on **team-level** explanations only:

- Why did Liverpool concede in the last 10 minutes?
- Why did Arsenal lose control after halftime?
- Why did Team X struggle to create chances?

**Not yet supported:**
- Player-level decline analysis
- Tactical formation inference
- Prediction models

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or use trusted hosts if SSL issues
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

See [docs/INSTALL.md](docs/INSTALL.md) for detailed installation instructions.

### Usage

**Set environment variables:**
```bash
export GRINTA_COMPETITION_ID=16  # Champions League
export GRINTA_SEASON_ID=4        # 2018/2019
```

**Run ingestion pipeline:**
```python
from ingestion import run_pipeline, get_ingestion_config

config = get_ingestion_config()
result = run_pipeline(config)
```

**Or use the command line:**
```bash
python3 -m ingestion
```

## Project Structure

```
Grinta/
├── ingestion/          # Data ingestion pipeline
│   ├── loaders/        # StatsBomb API loaders
│   ├── storage/        # Raw & processed data storage
│   ├── normalizers/    # Data normalization
│   └── pipeline.py     # Orchestration
├── features/           # Team-level metric computation (coming soon)
├── reasoning/          # LLM reasoning schemas (coming soon)
├── app/                # Streamlit UI (coming soon)
├── data/
│   ├── raw/           # Raw JSON files
│   └── processed/     # Normalized DataFrames
├── tests/              # Test suite
└── docs/               # Documentation
```

## Testing

Run the test suite:

```bash
# Quick syntax validation
python3 tests/test_syntax.py

# Component tests (requires network)
python3 tests/test_components.py

# Full pipeline test
python3 tests/test_manual.py

# Unit tests
pytest tests/test_ingestion.py -v

# Or use the test runner
./tests/scripts/run_tests.sh
```

See [TESTING.md](TESTING.md) for detailed testing documentation.

## Data Sources

Currently uses **StatsBomb Open Data** (free, public dataset):
- Available competitions: Champions League, Premier League, La Liga, World Cup, Euro, etc.
- Historical data from various seasons
- Event-level data with detailed attributes

See [docs/project_context.md](docs/project_context.md) for architecture details.

## Development

### Adding New Features

1. **Ingestion**: Add loaders/storage in `ingestion/`
2. **Features**: Compute metrics in `features/`
3. **Reasoning**: Define schemas in `reasoning/`
4. **UI**: Build interfaces in `app/`

### Code Style

- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Write tests for new features

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
