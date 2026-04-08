# 📝 CHANGES — ForkLens Project Log

All notable changes to this project are recorded here in reverse chronological order.

## [2026-03-30] — Groq Architecture Migration & Full Modularization

### 🚀 Groq API Integration (Goodbye 402 Quotas)
-   **Migrated Primary LLM**: Switched the core conversation engine in `forklens/llm_client.py` away from HuggingFace Inference to use Groq's blindingly fast API endpoints.
-   **Groq LLM-as-a-Judge**: Upgraded `forklens/evaluator.py` to optionally use a dedicated Groq client when `GROQ_API_KEY` is present.
-   **Native JSON Forcing**: Re-architected the Evaluator to use Groq's native `response_format={"type": "json_object"}` mode, guaranteeing zero structured-parsing crashes.
-   **Versatile Defaults**: Changed the default `.env` models from `meta-llama/Llama-3.3-70B-Instruct` to `llama-3.3-70b-versatile` to match Groq's string standards.

### 🐛 Backend Stability Fixes
-   **Erased `.join()` NoneType Crashes**: Fixed a fatal `500 Server Error` inside `server.py` and `forklens/conversation.py` that occurred when extracting `display_content` mappings from previously saved RAG histories.

### 🏗️ Complete Codebase Modularization
-   Completed the final phase of codebase isolation by safely deleting the obsolete `app.py` script.
-   Absorbed the scattered `server.py` router and `prompts.py` rules into the `forklens` package (`forklens/api.py` and `forklens/prompts.py`).
-   Created a tiny root-level `server.py` wrapper shim bridging legacy execute commands securely into the new `forklens.api:app`.

### 🧠 LLM Prompts & Memory Binding
-   Updated **Rule 6** in the Master Prompt: If a user asks a follow-up conversational question (e.g. *"How is this connected to me?"*), the LLM is now strictly instructed to deepen the connection to the *same* literary character rather than introducing a completely new one.

### 💬 UI/UX Improvements
-   **Dynamic Auto-expanding Input Box**: The user chat box now natively wraps and expands vertically (up to 250px inside) while typing long emotional texts, complete with customized gold scrollbars.
-   **Graceful Auto-scrolling**: React natively issues a 100ms async paint timeout when a new message or emotion badge appears, forcefully scrolling the chat layout above the heavily padded sticky footer so the result is immediately visible without manual scrolling.

---

## [2026-03-27] — Unified Proactive RAG & Master Prompt

### 🧠 Master Prompt Integration (Rules 1-5)
-   Replaced the basic counselor prompt with a **5-Rule Master Prompt** that governs proactive character surfacing, context matching, and empathy balance.
-   Introduced strict **Rule-based triggers**: The LLM now proactively surfaces characters only if `emotion_score >= 0.65` and labels match specific distress categories.
-   Added **Mature/Youth context matching** guidance to ensure character age matches the user's implied life stage.

### 🏗️ Architectural Shift: Proactive Intelligence
-   **Deleted Intent-Based Branching**: Removed `wants_advice()` and `check_wants_advice()` from `app.py`. The chatbot no longer "waits to be asked" for a story.
-   **Unified Turn Execution**: Every conversation turn (excluding greetings/goodbyes) now runs the full RAG pipeline.
-   **Decision Offloading**: The decision to "follow up" vs. "surface a character" is now handled by the LLM itself based on the new context block and Master Rules.

### 🧱 Unified Context Block
-   Refactored `get_rag_emotion_prompt` to output a structured key-value context block:
    -   `user_message`
    -   `emotion_label`
    -   `emotion_score`
    -   `retrieved_passages`
    -   `conversation_history`

### 🚀 `start.sh` — New Utility
-   Created a foolproof launch script that calls the virtual environment's Streamlit binary directly.
-   Prevents `ModuleNotFoundError` by ensuring the correct Python environment is always used.

---

## [2026-03-27] — System Check Bash Runner

### 🛠️ `run_checks.sh` — New File
Added a single-command bash runner that executes all diagnostic and smoke-test scripts in sequence:

| Stage | Covers |
|---|---|
| **1 / Env** | Python 3 check, `.env` presence, venv activation, package imports |
| **2 / LLM API** | `scripts/test_api.py` — HuggingFace token + live API call |
| **3 / Qdrant** | `scripts/test_qdrant.py` + `diagnose_qdrant.py` — connection, collection, port/DNS |
| **4 / Models** | Emotion model directory, `forklens.emotion` import, embedding model load |
| **5 / Evaluator** | `forklens.evaluator` import + sample evaluation case |

- Supports `--skip-eval`, `--only <stage>` flags.
- Coloured terminal output with per-step pass/fail icons.
- Prints a final summary table; exits non-zero if any step fails (CI-compatible).

---

## [2026-03-27] — LLM-as-Judge Evaluator

### 🔍 `forklens/evaluator.py` — New Module
Built a quality-scoring judge that uses Llama-3.1 to evaluate ForkLens end-to-end responses across four dimensions:

| Dimension | What It Checks |
|---|---|
| `emotion_accuracy` | Did BERT correctly predict the user's emotion? |
| `retrieval_relevance` | Are the Qdrant passages genuinely relevant? |
| `literary_fit` | Are the characters a meaningful match for the crossroads? |
| `empathy_helpfulness` | Is the LLM response warm, human, and useful? |

- Returns a typed `EvaluationResult` dataclass with per-dimension scores (1–5), overall verdict (`good` / `needs_improvement` / `poor`), and a concrete `suggested_fix`.
- Temperature set to `0.1` for deterministic, consistent scoring.
- Regex-based JSON extraction handles markdown-fenced LLM output safely.
- Pretty ASCII bar chart printed via `__str__()`.

### 🧪 `scripts/evaluate.py` — New CLI Runner
Three sample test cases designed to stress-test all four judge dimensions, including a deliberately poor-retrieval case (#2) to verify the judge is genuinely critical.

```bash
python scripts/evaluate.py              # all cases
python scripts/evaluate.py --case 2    # single case
python scripts/evaluate.py --json      # full JSON dump
```

### 📦 `forklens/__init__.py` — Updated
Exposed `evaluate`, `EvaluationResult`, and `DimensionScore` at the package level for clean imports:
```python
from forklens import evaluate
```

---

## [2026-03-27] — README Rewrite

### 📄 `README.md` — Fully Rewritten
Complete overhaul to reflect the current modular architecture:
- Mermaid architecture diagram (User → Streamlit → RAG → Qdrant → LLM).
- Accurate `forklens/` package module table with descriptions.
- Updated setup guide referencing `.env.example` and all three model vars.
- New **Customization** section explaining zero-code model swapping via `.env`.
- Removed stale references to `anaar.py`, old test script paths, and notebooks.

---

## [2026-03-27] — Model Configuration Upgrade

### 🔧 Flexible Model Settings
-   Moved all model names from code to `.env` file for easier customization.
-   Added `LLM_MODEL`, `EMBED_MODEL`, and `EMOTION_MODEL_PATH` to configuration.
-   Updated `forklens/config.py` to read these values via `os.getenv` with sensible fallbacks.
-   Updated `README.md` and `.env.example` with the new configuration schema.

---

## [2026-03-27] — Project Modularisation

### 🏗️ New Structure: `forklens/` Package
Broke the monolithic `anaar.py` (600+ lines) into a clean Python package:

| New File | What It Contains |
|---|---|
| `forklens/__init__.py` | Package marker |
| `forklens/config.py` | All env vars & constants (single source of truth) |
| `forklens/llm_client.py` | Shared HuggingFace OpenAI-compatible client |
| `forklens/db.py` | Qdrant connection + `QDRANT_AVAILABLE` flag |
| `forklens/emotion.py` | Fine-tuned BERT emotion model loading + `predict_emotion()` |
| `forklens/rag.py` | Full RAG pipeline, emotion filtering, context builder, fallback |
| `forklens/conversation.py` | Greeting, follow-up, intent detection, closure, more-examples |

### 🗑️ Files Removed
- `anaar.py` — replaced entirely by the `forklens/` package
- `prepare_github.py` — one-off GitHub prep script, not needed at runtime
- `bert_model.ipynb` — development notebook
- `gutenberg-books.ipynb` — development notebook
- `upload_qdrant.ipynb` — development notebook

### 📁 Files Moved → `scripts/`
- `test_api.py` → `scripts/test_api.py`
- `test_qdrant.py` → `scripts/test_qdrant.py`
- `diagnose_qdrant.py` → `scripts/diagnose_qdrant.py`
- `setup_models.py` → `scripts/setup_models.py`
- `setup_new_qdrant.py` → `scripts/setup_new_qdrant.py`

### 🔧 Files Modified
- `app.py` — rewritten to import from `forklens.*` only; zero business logic
- `scripts/test_api.py` — updated imports to use `forklens.llm_client`
- `scripts/test_qdrant.py` — updated to read credentials from `forklens.config`

### 🐛 Bug Fixed
- Old `anaar.py` had hardcoded fallback Qdrant credentials pointing to an old
  cluster, causing `⚠️ Qdrant unavailable` on every startup.
  `forklens/config.py` now reads **only from `.env`**, so Qdrant connects correctly.

---

<!-- Add new entries above this line, newest first -->
