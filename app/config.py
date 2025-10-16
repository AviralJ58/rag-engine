import os
from dotenv import load_dotenv
from redis import Redis
from qdrant_client import QdrantClient

load_dotenv()

# Environment Variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Initialize Clients
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
qdrant_client = QdrantClient(path="qdrant_storage")  # embedded local mode
# qdrant = QdrantClient(url=os.getenv("QDRANT_URL"))
