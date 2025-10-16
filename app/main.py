from fastapi import FastAPI
from app.routes import query
from app.config import redis_client, qdrant_client

app = FastAPI(title="Scalable Web-Aware RAG Engine (Prototype)")

@app.get("/health")
async def health_check():
    """Verify Redis and Qdrant connections."""
    try:
        redis_ok = redis_client.ping()
    except Exception:
        redis_ok = False

    try:
        qdrant_info = qdrant_client.get_collections()
        qdrant_ok = True
    except Exception:
        qdrant_ok = False

    return {
        "status": "ok" if (redis_ok and qdrant_ok) else "partial",
        "redis": redis_ok,
        "qdrant": qdrant_ok
    }

# Include routes
app.include_router(query.router)
