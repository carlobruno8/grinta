#!/bin/bash
# Test runner script for Grinta ingestion pipeline

set -e

echo "============================================================"
echo "Grinta Ingestion Pipeline - Test Suite"
echo "============================================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ python3 not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python3 found${NC}"

# Test 1: Syntax validation
echo ""
echo "============================================================"
echo "Test 1: Syntax and Structure Validation"
echo "============================================================"
python3 tests/test_syntax.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Syntax validation passed${NC}"
else
    echo -e "${RED}✗ Syntax validation failed${NC}"
    exit 1
fi

# Check if dependencies are installed
echo ""
echo "============================================================"
echo "Checking dependencies..."
echo "============================================================"
python3 -c "import dotenv, pandas, statsbombpy" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
    DEPS_INSTALLED=true
else
    echo -e "${YELLOW}⚠ Dependencies not installed${NC}"
    echo "  Install with: pip install -r requirements.txt"
    DEPS_INSTALLED=false
fi

# Test 2: Unit tests (if pytest available)
if command -v pytest &> /dev/null && [ "$DEPS_INSTALLED" = true ]; then
    echo ""
    echo "============================================================"
    echo "Test 2: Unit Tests (pytest)"
    echo "============================================================"
    python3 -m pytest tests/test_ingestion.py -v --tb=short
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Unit tests passed${NC}"
    else
        echo -e "${RED}✗ Unit tests failed${NC}"
        exit 1
    fi
else
    echo ""
    echo "============================================================"
    echo "Test 2: Unit Tests (skipped)"
    echo "============================================================"
    echo -e "${YELLOW}⚠ Skipping unit tests (pytest not installed or dependencies missing)${NC}"
fi

# Test 3: Component tests (requires network and dependencies)
if [ "$DEPS_INSTALLED" = true ]; then
    echo ""
    echo "============================================================"
    echo "Test 3: Component Tests"
    echo "============================================================"
    echo "This will make real API calls to StatsBomb..."
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 tests/test_components.py
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Component tests passed${NC}"
        else
            echo -e "${RED}✗ Component tests failed${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠ Component tests skipped${NC}"
    fi
else
    echo ""
    echo "============================================================"
    echo "Test 3: Component Tests (skipped)"
    echo "============================================================"
    echo -e "${YELLOW}⚠ Skipping component tests (dependencies not installed)${NC}"
fi

echo ""
echo "============================================================"
echo "Test Summary"
echo "============================================================"
echo -e "${GREEN}✓ Syntax validation: PASSED${NC}"
if [ "$DEPS_INSTALLED" = true ]; then
    echo -e "${GREEN}✓ Dependencies: INSTALLED${NC}"
else
    echo -e "${YELLOW}⚠ Dependencies: NOT INSTALLED${NC}"
fi
echo ""
echo "To run full test suite:"
echo "  1. pip install -r requirements.txt"
echo "  2. python3 tests/test_components.py"
echo "  3. python3 tests/test_manual.py"
echo "  4. pytest tests/ -v"
