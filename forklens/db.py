"""
forklens/db.py
==============
Qdrant vector-database connection.
Exposes `qdrant_client` and `QDRANT_AVAILABLE` for use in other modules.
"""

from . import config

try:
    from qdrant_client import QdrantClient as _QdrantClient

    qdrant_client = _QdrantClient(
        url=config.QDRANT_HOST,
        api_key=config.QDRANT_API_KEY,
        timeout=config.QDRANT_TIMEOUT,
        prefer_grpc=False,   # Force HTTP REST to avoid gRPC issues
        https=True,
        port=443,
    )

    # Smoke-test the connection
    qdrant_client.get_collections()
    print("✅ Qdrant connected successfully")
    QDRANT_AVAILABLE = True

except Exception as exc:
    print(f"⚠️  Qdrant unavailable: {str(exc)[:120]}")
    print("📝 Running in fallback mode (emotion + LLM only)")
    qdrant_client = None       # type: ignore[assignment]
    QDRANT_AVAILABLE = False
