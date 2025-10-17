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

    # Check if URL is already ingested
    try:
        existing = supabase.table("documents").select("doc_id", "status").eq("url", str(payload.url)).execute()
        if existing.data and len(existing.data) > 0:
            doc = existing.data[0]
            if doc["status"] == "completed":
                return {"message": "URL already ingested", "doc_id": doc["doc_id"]}
            elif doc["status"] == "processing":
                return {"message": "URL ingestion already in progress", "doc_id": doc["doc_id"]}
            elif doc["status"] == "queued":
                return {"message": "URL ingestion already queued", "doc_id": doc["doc_id"]}

            doc_id = doc["doc_id"]
        else:
            # URL is not ingested, create a new job
            doc_id = str(uuid.uuid4())

            supabase.table("documents").insert({
                "doc_id": doc_id,
                "url": str(payload.url),
                "source": payload.source,
                "status": "pending"
            }).execute()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase query failed: {e}")

    # Create ingestion job payload
    job_id = str(uuid.uuid4())
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

    # Update document status to 'queued'
    try:
        supabase.table("documents").update({"status": "queued"}).eq("doc_id", doc_id).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase update failed: {e}")

    return {"message": "Ingestion job queued", "job_id": job_id, "doc_id": doc_id}
