import time
import json
import uuid
from app.config import redis_client
from app.utils.supabase_client import supabase
from app.utils.text_processing import fetch_url, extract_main_text, chunk_text
from app.utils.embeddings import embed_texts
from app.utils.vectorstore import upsert_vectors, init_collection

QUEUE_KEY = "ingest:jobs"
COLLECTION_NAME = "documents_chunks"
VECTOR_SIZE = 384  # depends on sentence-transformers model (all-MiniLM-L6-v2)

# Initialize Qdrant collection
init_collection(COLLECTION_NAME, VECTOR_SIZE)


def process_job(job_payload):
    job = json.loads(job_payload)
    job_id = job["job_id"]
    doc_id = job["doc_id"]
    url = job["url"]

    print(f"[Worker] Processing job {job_id} for URL: {url}")

    try:
        # Atomic update: set job status to 'processing'
        current = supabase.table("documents").select("status").eq("doc_id", doc_id).execute()
        if not current.data or current.data[0]["status"] in ["processing", "completed"]:
            print(f"[Worker] Job {job_id} skipped: document already {current.data[0]['status'] if current.data else 'not found'}")
            return
        
        supabase.table("documents").update({"status": "processing"}).eq("doc_id", doc_id).execute()

        # Fetch & extract text
        html = fetch_url(url)
        text = extract_main_text(html)

        # Chunk text
        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("No chunks extracted from URL")

        # Generate embeddings
        embeddings = embed_texts(chunks)

        # Upsert into Qdrant
        vector_ids = [str(uuid.uuid4()) for _ in chunks]
        payloads = [
            {"chunk_id": vid, "doc_id": doc_id, "url": url, "text_snippet": chunk}
            for vid, chunk in zip(vector_ids, chunks)
        ]
        upsert_vectors(COLLECTION_NAME, embeddings, payloads, vector_ids)

        # Update Supabase tables
        supabase.table("documents").update({"status": "completed"}).eq("doc_id", doc_id).execute()

        print(f"[Worker] Job {job_id} completed successfully")

    except Exception as e:
        print(f"[Worker] Job {job_id} failed: {e}")
        supabase.table("documents").update({"status": "failed"}).eq("doc_id", doc_id).execute()

def worker_loop():
    print("[Worker] Started ingestion worker...")
    while True:
        job_payload = redis_client.lpop(QUEUE_KEY)
        if job_payload:
            process_job(job_payload)
        else:
            time.sleep(2)  # no job, wait


if __name__ == "__main__":
    worker_loop()