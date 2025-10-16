from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
import uuid
import json
from app.config import redis_client
from app.utils.supabase_client import supabase

router = APIRouter()


class IngestURLRequest(BaseModel):
    url: HttpUrl
    source: str = "web"


@router.post("/ingest-url", status_code=202)
async def ingest_url(payload: IngestURLRequest):
    """Accept a URL, create a job, and enqueue it for ingestion."""

    # Generate IDs
    doc_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())

    # Insert document metadata into Supabase
    try:
        supabase.table("documents").insert({
            "doc_id": doc_id,
            "url": str(payload.url),
            "source": payload.source,
            "status": "pending"
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase insert failed: {e}")

    # Create ingestion job payload
    job_payload = {
        "job_id": job_id,
        "doc_id": doc_id,
        "url": str(payload.url)
    }

    # Push to Redis queue
    try:
        redis_client.rpush("ingest:jobs", json.dumps(job_payload))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis enqueue failed: {e}")

    return {"message": "Ingestion job queued", "job_id": job_id, "doc_id": doc_id}
