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

### Philosophy

The LLM is not allowed to:
- Fetch data
- Compute metrics  
- Use external football knowledge

It only reasons over structured inputs. The goal is disciplined, explainable AI.

## Architecture

```
data/
├── raw/          → Raw StatsBomb JSON files
└── processed/    → Cleaned event-level data

ingestion/        → Data loading + normalization
features/         → Team-level metric computation  
reasoning/        → LLM schemas, prompts, contracts
app/              → Streamlit UI
tests/            → Test suite
scripts/          → Demo and utility scripts
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
# Clone the repository
git clone https://github.com/carlobruno8/grinta.git
cd grinta

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Setup API Key

1. Get your Google AI API key from: https://aistudio.google.com/apikey
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your API key:
   ```bash
   GOOGLE_API_KEY="your-actual-api-key-here"
   ```

**Important:** Never commit your `.env` file to git!

### Run the Streamlit App

```bash
# Activate virtual environment
source venv/bin/activate

# Run the app
streamlit run app/main.py
```

The app provides:
- Match selection from processed data
- Team-level metrics visualization
- Natural language question input
- AI-generated tactical explanations

### Usage

**Run the Streamlit app:**
```bash
streamlit run app/main.py
```

**Set environment variables:**
```bash
# API key (required for AI explanations)
# Add to .env file - see Setup API Key section above
GOOGLE_API_KEY="your-google-api-key"

# For ingestion (optional)
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

**Compute team-level metrics (after ingestion):**
```python
from features import get_match_metrics

metrics = get_match_metrics(match_id=22912)
# metrics["teams"] -> possession, passes, shots, goals, etc.
# Optional: get_match_metrics(22912, period=2, last_n_minutes=10)
```

Or run the demo: `python3 scripts/run_features_demo.py` (requires processed data for match 22912).

### Reasoning Module

Generate evidence-based explanations for match events:

```python
from reasoning import generate_explanation

# Generate explanation with time filter
response = generate_explanation(
    match_id=22912,
    question="Why did Team A concede in the last 10 minutes?",
    time_filter="last_10_min"
)

print(response.explanation.summary)
for claim in response.explanation.claims:
    print(f"- {claim.statement} (confidence: {claim.confidence})")
```

**Tactical Intelligence**: Enhanced with real football insights:
- Spatial attack distribution (which flanks were targeted?)
- Defensive positioning (high press vs low block)
- Passing patterns (wide vs narrow, progressive vs cautious)
- Tactical mismatches and vulnerabilities

**Example**: Instead of "Team A had 55% possession", get "Team A controlled possession but played narrow (spread: 12.5), allowing Team B to compress centrally and force wide shots".

📖 **See**: [`docs/HOW_TO_GET_INTELLIGENT_INSIGHTS.md`](docs/HOW_TO_GET_INTELLIGENT_INSIGHTS.md) for complete guide

**Requirements:**
- Set `GOOGLE_API_KEY` environment variable
- Processed match events must exist

**Time filters:**
- `"last_10_min"` - Last 10 minutes of match
- `"period_2"` - Second half only
- `"first_15_min"` - First 15 minutes
- `None` - Full match

See [`reasoning/contract.md`](reasoning/contract.md) for detailed documentation.

## Testing

```bash
# Run all tests
./run_tests.sh

# Or individually
pytest tests/test_ingestion.py -v
pytest tests/test_features.py -v
pytest tests/test_reasoning.py -v
pytest tests/test_spatial.py -v
pytest tests/test_integration.py -v

# Integration test (requires GOOGLE_API_KEY)
pytest tests/test_reasoning.py -v --run-integration
```

See [`docs/TESTING.md`](docs/TESTING.md) for detailed testing documentation.

## Data Sources

Currently uses **StatsBomb Open Data** (free, public dataset):
- Available competitions: Champions League, Premier League, La Liga, World Cup, Euro, etc.
- Historical data from various seasons
- Event-level data with detailed attributes

See [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md) for detailed architecture.

## Development

### Adding New Features

1. **Ingestion**: Add loaders/storage in `ingestion/`
2. **Features**: Compute metrics in `features/`
3. **Reasoning**: Add new evidence types or modify prompts in `reasoning/`
4. **UI**: Build interfaces in `app/`

### Documentation

- **Setup**: [`docs/INSTALL.md`](docs/INSTALL.md) - Installation guide
- **Architecture**: [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md) - System design
- **Usage**: [`docs/HOW_TO_GET_INTELLIGENT_INSIGHTS.md`](docs/HOW_TO_GET_INTELLIGENT_INSIGHTS.md) - User guide
- **Reasoning**: [`reasoning/contract.md`](reasoning/contract.md) - LLM module spec
- **Testing**: [`docs/TESTING.md`](docs/TESTING.md) - Test guidelines

### Code Style

- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Write tests for new features
