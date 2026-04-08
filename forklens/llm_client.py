"""
forklens/llm_client.py
======================
Creates and exports the shared OpenAI-compatible HuggingFace LLM client.
"""

from openai import OpenAI
from .config import GROQ_API_KEY, LLM_MODEL, log

def get_model_name() -> str:
    return LLM_MODEL

# Shared client instance using Groq to bypass HF 402 limits
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)
log(f"Groq primary client ready — token defined.")


def test_connection() -> bool:
    """Quick smoke-test to verify the LLM API is reachable."""
    try:
        log("Testing LLM connection...")
        resp = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is the capital of France?"},
            ],
        )
        print("🧠 LLM response:", resp.choices[0].message.content)
        return True
    except Exception as exc:
        print(f"❌ LLM connection error: {exc}")
        return False
