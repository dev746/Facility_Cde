#!/bin/bash
# tests/run_tests.sh — Run all tests in the correct order
# Usage: bash tests/run_tests.sh
# Or with a specific phase: bash tests/run_tests.sh unit

set -e  # stop on first failure

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

PHASE=${1:-all}
FAILED=0

run() {
    local label=$1
    local cmd=$2
    echo ""
    echo -e "${BOLD}Running: ${label}${NC}"
    if PYTHONPATH=. python $cmd; then
        echo -e "${GREEN}✓ ${label} passed${NC}"
    else
        echo -e "${RED}✗ ${label} failed${NC}"
        FAILED=$((FAILED + 1))
        if [ "$PHASE" != "all" ]; then
            exit 1
        fi
    fi
}

echo -e "${BOLD}======================================${NC}"
echo -e "${BOLD}  Facility CDE v2 — Test Suite${NC}"
echo -e "${BOLD}======================================${NC}"

if [ "$PHASE" = "unit" ] || [ "$PHASE" = "all" ]; then
    echo -e "\n${BOLD}Phase 1: Unit tests (no DB needed)${NC}"
    run "Ingestion + normalisers" "tests/test_ingestion_files.py"
    run "All features unit"       "tests/test_all_features.py --feature ingestion"
    run "Semantic search unit"    "tests/test_all_features.py --feature semantic"
    run "Context unit"            "tests/test_all_features.py --feature context"
    run "Version tracking unit"   "tests/test_all_features.py --feature versioning"
    run "Graph API unit"          "tests/test_all_features.py --feature graph"
fi

if [ "$PHASE" = "integration" ] || [ "$PHASE" = "all" ]; then
    echo -e "\n${BOLD}Phase 2: Integration tests (needs DB)${NC}"
    run "WhatsApp flows"          "tests/test_whatsapp_flows.py"
fi

if [ "$PHASE" = "load" ] || [ "$PHASE" = "all" ]; then
    echo -e "\n${BOLD}Phase 3: Load test (50 workers)${NC}"
    run "Load test"               "tests/load_test.py 50"
fi

echo ""
echo -e "${BOLD}======================================${NC}"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}${BOLD}  All tests passed ✓${NC}"
    echo -e "${BOLD}======================================${NC}"
    exit 0
else
    echo -e "${RED}${BOLD}  ${FAILED} test suite(s) failed ✗${NC}"
    echo -e "${BOLD}======================================${NC}"
    exit 1
fi
