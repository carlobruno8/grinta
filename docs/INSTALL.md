# Installation Guide

## SSL Certificate Issue

If you encounter SSL certificate errors when installing dependencies, try one of these solutions:

### Option 1: Install with trusted hosts (recommended)
```bash
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Option 2: Use a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Option 3: Install certificates (macOS)
```bash
# Install certificates
/Applications/Python\ 3.13/Install\ Certificates.command

# Then try installing again
pip install -r requirements.txt
```

### Option 4: Update pip and certificates
```bash
python3 -m pip install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org
pip install -r requirements.txt
```

## Manual Installation

If automated installation fails, install packages individually:

```bash
pip install pandas
pip install statsbombpy
pip install pydantic
pip install python-dotenv
pip install pyarrow
pip install pytest
```

## Verify Installation

After installation, verify all packages are installed:

```bash
python3 -c "import pandas, statsbombpy, pydantic, dotenv, pyarrow, pytest; print('All packages installed!')"
```

## Next Steps

Once dependencies are installed, run the test suite:

```bash
./run_tests.sh
```

Or run tests individually:

```bash
python3 test_syntax.py
python3 test_components.py
python3 test_manual.py
pytest tests/test_ingestion.py -v
pytest tests/test_integration.py -v -m integration
```
