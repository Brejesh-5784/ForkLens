#!/usr/bin/env python3
"""
scripts/test_qdrant.py
======================
Tests the Qdrant Cloud connection and verifies the gutenbergbooks collection.
Run from the project root:
    python scripts/test_qdrant.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from forklens.config import QDRANT_HOST, QDRANT_API_KEY, COLLECTION_NAME
from qdrant_client import QdrantClient

print(f"Testing connection to: {QDRANT_HOST}")
print(f"Using API key: {QDRANT_API_KEY[:20]}...")

try:
    client = QdrantClient(url=QDRANT_HOST, api_key=QDRANT_API_KEY, prefer_grpc=False, https=True, port=443)
    print("✅ Client created (REST mode)")

    collections = client.get_collections()
    print(f"✅ Collections: {[c.name for c in collections.collections]}")

    info = client.get_collection(COLLECTION_NAME)
    print(f"✅ '{COLLECTION_NAME}' — {info.points_count} points")

    results = client.query_points(collection_name=COLLECTION_NAME, query=[0.1] * 384, limit=1)
    print(f"✅ Query OK — returned {len(results.points)} result(s)")

except Exception as exc:
    print(f"❌ Connection failed: {exc}")
    print("\nTroubleshooting:")
    print("1. Check if your Qdrant cloud instance is running")
    print("2. Verify your API key in .env")
    print("3. Run scripts/diagnose_qdrant.py for detailed diagnostics")