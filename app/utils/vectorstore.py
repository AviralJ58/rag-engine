from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Initialize Qdrant client
qdrant_client = QdrantClient(path="qdrant_storage")  # local embedded

def init_collection(name, vector_size):
    """Create collection if not exists."""
    try:
        qdrant_client.recreate_collection(
            collection_name=name,
            vectors={"size": vector_size, "distance": "Cosine"},
        )
    except Exception:
        pass

def upsert_vectors(collection_name, vectors, payloads, ids):
    """Upsert embeddings with payloads into Qdrant."""
    points = [PointStruct(id=i, vector=v, payload=p) for i, v, p in zip(ids, vectors, payloads)]
    qdrant_client.upsert(collection_name=collection_name, points=points)
