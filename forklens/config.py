"""
forklens/config.py
==================
Central configuration for ForkLens.
Loads all environment variables and exposes constants used across modules.
"""

import os
from dotenv import load_dotenv

# Load .env from the project root (one level above this file)
load_dotenv()

# Suppress HuggingFace tokenizer parallelism warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ── HuggingFace ──────────────────────────────────────────────────────────────
HF_TOKEN: str = os.getenv("HF_TOKEN", "your_hf_api_key_here")
os.environ["HF_TOKEN"] = HF_TOKEN

HF_BASE_URL: str = "https://router.huggingface.co/v1/"
LLM_MODEL: str = os.getenv("LLM_MODEL", "meta-llama/Llama-3.1-8B-Instruct")

# ── Groq (For LLM Judge) ─────────────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
# Default to Groq's fast Llama 3.1 8B for rapid parallel judging
JUDGE_MODEL: str = os.getenv("JUDGE_MODEL", "llama-3.1-8b-instant")

# ── Qdrant ───────────────────────────────────────────────────────────────────
QDRANT_HOST: str = os.getenv(
    "QDRANT_HOST",
    "https://your-cluster.qdrant.io",
)
QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
COLLECTION_NAME: str = "gutenbergbooks"
QDRANT_TIMEOUT: int = 20

# ── Emotion model ─────────────────────────────────────────────────────────────
EMOTION_MODEL_PATH: str = os.getenv("EMOTION_MODEL_PATH", "./final_models/emotion_model")

# ── Embedding model ───────────────────────────────────────────────────────────
EMBED_MODEL_NAME: str = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

# ── RAG parameters ────────────────────────────────────────────────────────────
TOP_K_RESULTS: int = 5
CONTEXT_WINDOW: int = 5

# ── Debug ─────────────────────────────────────────────────────────────────────
VERBOSE_MODE: bool = True


def log(message: str, level: str = "INFO") -> None:
    """Print a verbose log message when VERBOSE_MODE is enabled."""
    if VERBOSE_MODE:
        print(f"🤖 [{level}] {message}")
