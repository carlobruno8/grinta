# Grinta Project Structure

This document describes the organization of the Grinta codebase.

## Root Directory

```
Grinta/
├── README.md              # Main project documentation
├── requirements.txt       # Python dependencies
├── pytest.ini            # Pytest configuration
├── run_tests.sh          # Test execution script
└── .gitignore            # Git ignore patterns
```

## Core Modules

### `ingestion/`
Data loading and normalization from StatsBomb JSON format.

- **Purpose**: Parse raw match data and normalize events
- **Output**: Clean, structured event data
- **Key Files**:
  - `loader.py` - Load raw StatsBomb JSON
  - `normalizers/` - Event normalization logic

### `features/`
Team-level metric computation from normalized events.

- **Purpose**: Transform events into analytical features
- **Output**: Team metrics (possession, shots, spatial stats, etc.)
- **Key Files**:
  - `possession.py` - Possession metrics
  - `shots.py` - Shot analysis
  - `spatial.py` - Spatial positioning
  - `territory.py` - Territorial control
  - `time_windows.py` - Time-based aggregation
  - `aggregator.py` - Combine all metrics

### `reasoning/`
Evidence-based explanation generation using Gemini API.

- **Purpose**: Generate grounded tactical explanations
- **Output**: Natural language insights with metric citations
- **Key Files**:
  - `contract.md` - System prompt and reasoning contract
  - `client.py` - Gemini API integration
  - `input_schema.py` - Input validation
  - `output_schema.py` - Structured output format
  - `prompts.py` - Prompt templates

### `app/`
Streamlit-based UI for interactive analysis.

- **Purpose**: User interface for asking questions about matches
- **Key Components**:
  - `main.py` - Streamlit app entry point
  - `question_parser.py` - Parse user questions
  - `components/` - UI components (input, metrics, explanations)

## Frontend & Backend (In Development)

### `frontend/`
React + TypeScript + Vite web application.

- **Stack**: React 18, TypeScript, Tailwind CSS, Vite
- **Key Files**:
  - `src/App.tsx` - Main application
  - `src/components/` - React components
  - `src/api/client.ts` - Backend API client

### `backend/`
FastAPI backend service.

- **Purpose**: REST API for frontend
- **Key Files**:
  - `api.py` - FastAPI routes

## Tests

### `tests/`
Comprehensive test suite for all modules.

- `test_ingestion.py` - Data loading tests
- `test_features.py` - Metric computation tests
- `test_reasoning.py` - Reasoning module tests
- `test_integration.py` - End-to-end tests
- `test_components.py` - App component tests
- `test_spatial.py` - Spatial analysis tests
- `test_gemini_setup.py` - API integration tests
- `test_manual.py` - Manual testing utilities
- `test_syntax.py` - Code syntax validation

### `scripts/`
Utility scripts for development and testing.

- Development utilities
- Test helpers
- Data processing scripts

## Documentation

### `docs/`
Comprehensive project documentation.

**Getting Started**:
- `INSTALL.md` - Installation instructions
- `APP_GUIDE.md` - How to use the application
- `TESTING.md` - Testing guide
- `TEST_RESULTS.md` - Latest test results

**Architecture & Design**:
- `project_context.md` - Project overview and context
- `UI_ARCHITECTURE.md` - UI design principles
- `UI_IMPLEMENTATION.md` - UI implementation details
- `REASONING_MODULE_SUMMARY.md` - Reasoning system design

**Development History**:
- `GEMINI_MIGRATION.md` - Migration to Gemini API
- `UPGRADE_COMPLETE.md` - Intelligence upgrade summary
- `BEFORE_AFTER_COMPARISON.md` - System improvements
- `TACTICAL_INTELLIGENCE_PLAN.md` - Intelligence roadmap
- `TACTICAL_INTELLIGENCE_SUMMARY.md` - Intelligence features
- `HOW_TO_GET_INTELLIGENT_INSIGHTS.md` - Usage guide
- `CHANGELOG.md` - Version history
- `COMMIT_GUIDE.md` - Git workflow

**Implementation Details**:
- `COMPLETE_IMPLEMENTATION_SUMMARY.md` - Full system overview
- `TEST_RESULTS_COMPLETE.md` - Comprehensive test results
- `UI_CHECKLIST.md` - UI feature checklist
- `REACT_SETUP.md` - React frontend setup

## Data

### `data/`
Match data storage (ignored by git).

```
data/
├── raw/           # Raw StatsBomb JSON files
│   └── .gitkeep
└── processed/     # Processed data files
    └── .gitkeep
```

**Note**: Actual data files are gitignored. Only directory structure is tracked.

## Development Environment

### `venv/`
Python virtual environment (gitignored).

Contains all Python dependencies listed in `requirements.txt`.

## File Organization Principles

1. **Tests alongside code**: Test files in `tests/` mirror the module structure
2. **Documentation centralized**: All `.md` files in `docs/` except root `README.md`
3. **Clean root**: Minimal files in root directory for clarity
4. **Separation of concerns**: Each module has a single, clear responsibility
5. **Data isolation**: Data files kept separate and gitignored

## Adding New Features

When adding new functionality:

1. **Code**: Place in appropriate module (`ingestion/`, `features/`, `reasoning/`, `app/`)
2. **Tests**: Add corresponding test in `tests/test_<module>.py`
3. **Documentation**: Update relevant doc in `docs/`
4. **Dependencies**: Add to `requirements.txt` (Python) or `package.json` (frontend)

## Common Development Tasks

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
./run_tests.sh

# Run Streamlit app
streamlit run app/main.py

# Frontend development
cd frontend && npm install && npm run dev

# Backend development
cd backend && uvicorn api:app --reload
```

## Questions?

Refer to:
- `docs/project_context.md` - High-level overview
- `docs/INSTALL.md` - Setup instructions
- `docs/APP_GUIDE.md` - Usage guide
- `README.md` - Quick start
