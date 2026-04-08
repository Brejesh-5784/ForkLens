#!/usr/bin/env bash
# =============================================================================
# start.sh — Launch ForkLens using the project's own virtual environment
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_STREAMLIT="$SCRIPT_DIR/venv/bin/streamlit"
VENV_PIP="$SCRIPT_DIR/venv/bin/pip"

# ── Sanity checks ──────────────────────────────────────────────────────────────
if [ ! -f "$VENV_STREAMLIT" ]; then
    echo "❌ venv not found. Run the following first:"
    echo "   python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

cd "$SCRIPT_DIR"

# ── Optional: install any missing packages silently ───────────────────────────
echo "📦 Verifying dependencies..."
"$VENV_PIP" install -q -r requirements.txt

echo "✅ All dependencies OK"
echo "🚀 Starting ForkLens..."
echo ""

# ── Launch with the venv Streamlit directly (no activation needed) ────────────
"$VENV_STREAMLIT" run app.py \
    --server.headless false \
    --browser.gatherUsageStats false
