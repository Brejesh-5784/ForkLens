#!/usr/bin/env python3
"""
scripts/test_api.py
===================
Smoke-tests the HuggingFace LLM API connection.
Run from the project root:
    python scripts/test_api.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN", "")

print("🔍 API Configuration Check:")
print(f"HF Token: {'✅ Set' if HF_TOKEN and HF_TOKEN != 'your_hf_api_key_here' else '❌ Not set'}")

if not HF_TOKEN or HF_TOKEN == "your_hf_api_key_here":
    print("❌ Please add your HuggingFace API key to the .env file")
    print("💡 Get your key from: https://huggingface.co/settings/tokens")
    sys.exit(1)

try:
    from forklens.llm_client import client, get_model_name

    print(f"\n🧪 Testing HuggingFace connection...")
    print(f"Model: {get_model_name()}")

    response = client.chat.completions.create(
        model=get_model_name(),
        messages=[{"role": "user", "content": "Say 'API test successful'"}],
        max_tokens=10,
    )
    print(f"✅ API Response: {response.choices[0].message.content}")

except Exception as exc:
    print(f"❌ API Test Failed: {exc}")
    print("\n🔧 Troubleshooting:")
    print("1. Check if your HF token is valid")
    print("2. Make sure you have access to the model")