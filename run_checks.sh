#!/usr/bin/env bash
# =============================================================================
# run_checks.sh — ForkLens full diagnostic & smoke-test runner
# =============================================================================
# Usage:
#   chmod +x run_checks.sh
#   ./run_checks.sh              # run all checks
#   ./run_checks.sh --skip-eval  # skip the slow LLM evaluator
#   ./run_checks.sh --only api   # run only the API test
# =============================================================================

set -euo pipefail

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# ── Helpers ───────────────────────────────────────────────────────────────────
PASS=0
FAIL=0
SKIP=0

print_header() {
    echo ""
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${CYAN}${BOLD}  $1${RESET}"
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
}

run_step() {
    local label="$1"
    local cmd="$2"

    echo ""
    echo -e "${BOLD}▶ $label${RESET}"
    echo -e "${YELLOW}  $ $cmd${RESET}"
    echo ""

    if eval "$cmd"; then
        echo ""
        echo -e "${GREEN}  ✅ PASSED: $label${RESET}"
        PASS=$((PASS + 1))
    else
        echo ""
        echo -e "${RED}  ❌ FAILED: $label${RESET}"
        FAIL=$((FAIL + 1))
    fi
}

skip_step() {
    echo -e "${YELLOW}  ⏭  SKIPPED: $1${RESET}"
    SKIP=$((SKIP + 1))
}

# ── Argument parsing ──────────────────────────────────────────────────────────
SKIP_EVAL=false
ONLY=""

for arg in "$@"; do
    case "$arg" in
        --skip-eval) SKIP_EVAL=true ;;
        --only)      shift; ONLY="$1" ;;
    esac
done

# ── Locate project root (directory containing this script) ────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
cd "$PROJECT_ROOT"

# ── Banner ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║         📚  ForkLens — Full System Check Runner         ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════╝${RESET}"
echo -e "  Project root : ${CYAN}$PROJECT_ROOT${RESET}"
echo -e "  Timestamp    : ${CYAN}$(date '+%Y-%m-%d %H:%M:%S')${RESET}"

# ── 1. Environment ────────────────────────────────────────────────────────────
print_header "1 / 5  —  Environment"

if [[ "$ONLY" == "" || "$ONLY" == "env" ]]; then
    # Check Python
    run_step "Python 3 available" "python3 --version"

    # Check .env exists
    run_step ".env file present" \
        "test -f '$PROJECT_ROOT/.env' && echo '.env found' || (echo '❌ .env not found — copy .env.example and fill in your keys' && exit 1)"

    # Activate venv if present
    if [ -d "$PROJECT_ROOT/venv" ]; then
        echo ""
        echo -e "${BOLD}▶ Activating virtual environment${RESET}"
        # shellcheck disable=SC1091
        source "$PROJECT_ROOT/venv/bin/activate"
        echo -e "${GREEN}  ✅ venv activated: $(which python3)${RESET}"
    else
        echo -e "${YELLOW}  ⚠  No venv/ directory found. Using system Python.${RESET}"
    fi

    # Check required packages
    run_step "Core packages importable" \
        "python3 -c 'import openai, qdrant_client, sentence_transformers, streamlit, transformers; print(\"All packages OK\")'"
fi

# ── 2. LLM / HuggingFace API ──────────────────────────────────────────────────
print_header "2 / 5  —  LLM API  (HuggingFace)"

if [[ "$ONLY" == "" || "$ONLY" == "api" ]]; then
    run_step "HuggingFace API smoke-test" \
        "python3 '$PROJECT_ROOT/scripts/test_api.py'"
else
    skip_step "HuggingFace API smoke-test"
fi

# ── 3. Qdrant Vector Database ─────────────────────────────────────────────────
print_header "3 / 5  —  Qdrant Vector Database"

if [[ "$ONLY" == "" || "$ONLY" == "qdrant" ]]; then
    run_step "Qdrant Cloud connection + collection check" \
        "python3 '$PROJECT_ROOT/scripts/test_qdrant.py'"

    run_step "Qdrant deep network diagnostics" \
        "python3 '$PROJECT_ROOT/scripts/diagnose_qdrant.py'"
else
    skip_step "Qdrant tests"
fi

# ── 4. Local Model Files ──────────────────────────────────────────────────────
print_header "4 / 5  —  Local Models"

if [[ "$ONLY" == "" || "$ONLY" == "models" ]]; then
    run_step "Emotion model directory exists" \
        "test -d '$PROJECT_ROOT/final_models/emotion_model' && echo 'emotion_model/ found' || (echo 'Run scripts/setup_models.py to set up local models' && exit 1)"

    run_step "Emotion model importable (forklens.emotion)" \
        "python3 -c 'from forklens.emotion import predict_emotion; print(\"✅ emotion module loaded\")'"

    run_step "Embedding model loads (SentenceTransformer)" \
        "python3 -c 'from forklens.rag import _embed_model; print(\"✅ embed model ready\")'"
else
    skip_step "Local model checks"
fi

# ── 5. LLM-as-Judge Evaluator ─────────────────────────────────────────────────
print_header "5 / 5  —  LLM Evaluator (Judge)"

if [[ "$ONLY" == "" || "$ONLY" == "eval" ]]; then
    if [ "$SKIP_EVAL" = true ]; then
        skip_step "LLM evaluator (--skip-eval flag set)"
    else
        run_step "Evaluator module importable" \
            "python3 -c 'from forklens.evaluator import evaluate; print(\"✅ evaluator ready\")'"

        run_step "Evaluator — sample case #1 (career crossroads)" \
            "python3 '$PROJECT_ROOT/scripts/evaluate.py' --case 1"
    fi
else
    skip_step "LLM evaluator"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║                    📊  Run Summary                      ║${RESET}"
echo -e "${BOLD}╠══════════════════════════════════════════════════════════╣${RESET}"
echo -e "${BOLD}║  ${GREEN}✅ Passed : $PASS${RESET}${BOLD}                                           ║${RESET}"
echo -e "${BOLD}║  ${RED}❌ Failed : $FAIL${RESET}${BOLD}                                           ║${RESET}"
echo -e "${BOLD}║  ${YELLOW}⏭  Skipped: $SKIP${RESET}${BOLD}                                           ║${RESET}"
echo -e "${BOLD}╠══════════════════════════════════════════════════════════╣${RESET}"

if [ "$FAIL" -eq 0 ]; then
    echo -e "${BOLD}║  ${GREEN}🎉 All systems good — ready to run: streamlit run app.py${RESET}${BOLD}  ║${RESET}"
else
    echo -e "${BOLD}║  ${RED}⚠  $FAIL check(s) failed — review output above${RESET}${BOLD}              ║${RESET}"
fi

echo -e "${BOLD}╚══════════════════════════════════════════════════════════╝${RESET}"
echo ""

# Return non-zero exit code if any step failed (useful for CI)
exit "$FAIL"
