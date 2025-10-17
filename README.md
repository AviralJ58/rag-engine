# 🧠 Scalable RAG Engine

A **production-grade Retrieval-Augmented Generation (RAG) pipeline** designed for scalability and modularity.  
The system supports **parallel ingestion**, **distributed document processing**, and **query-time retrieval with context-aware LLM generation**, using **Supabase**, **Redis**, and **Qdrant Cloud**.

---

## 🏗️ Architecture Overview

The system follows a **distributed worker-based architecture**:

- **FastAPI Server** — handles user requests for ingestion and querying.
- **Redis Queue** — decouples ingestion requests from heavy processing.
- **Ingestion Workers** — fetch content, chunk, embed, and store it in Qdrant.
- **Supabase (PostgreSQL)** — manages document metadata and ingestion job tracking.
- **Qdrant Cloud** — vector store for similarity search.
- **Google Gemini API** — provides LLM responses using retrieved context.

### 🧩 Final Architecture Diagram

![System Architecture](./images/architecture.png)

---

## 🔁 Sequence Diagram (Pipeline Flow)

![Sequence Diagram](./images/sequence.png)
---

## ⚙️ Technology Stack & Justifications

| Component | Technology | Reasoning |
|------------|-------------|------------|
| **Backend API** | FastAPI | Lightweight, async, and production-friendly. |
| **Task Queue** | Redis | Simple, fast message broker for decoupled ingestion. |
| **Database** | Supabase (PostgreSQL) | Manages metadata and ingestion states; integrates easily. |
| **Vector Store** | Qdrant Cloud | Cloud-hosted, scalable, and efficient for similarity search. |
| **Embeddings** | `all-MiniLM-L6-v2` (384-dim) | Compact yet high-quality embeddings for semantic retrieval. |
| **LLM** | Google Gemini API | High-quality contextual reasoning and summarization. |

---

## 🗃️ Database Schema

### Documents (Supabase)
| Column | Type | Description |
|--------|------|-------------|
| `doc_id` | `uuid` | Primary key |
| `url` | `text` | Source document URL |
| `source` | `text` | Origin identifier (e.g., "website", "pdf") |
| `status` | `text` | Processing status |
| `created_at` | `timestamp` | Record creation time |

### Vector Store (Qdrant)
| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Unique chunk ID |
| `vector` | `float[384]` | Embedding vector |
| `text_snippet` | `TEXT` | Extracted document chunk |
| `url` | `TEXT` | Source document URL |

---

## 🧩 API Documentation

### 1️⃣ Ingest URL
**Endpoint:**  
`POST /ingest-url`

**Body:**
```json
{
  "url": "https://python.langchain.com/docs/get_started/introduction/",
  "source": "LangChain Docs"
}
```

**Response:**
```json
{
  "job_id": "c89a7a7e-9129-4a3a-a2f9-b5af0b25a643",
  "status": "queued"
}
```

**Curl Example:**
```bash
curl -X POST http://localhost:8000/ingest-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://python.langchain.com/docs/get_started/introduction/", "source": "LangChain Docs"}'
```

---

### 2️⃣ Query Endpoint
**Endpoint:**  
`POST /query`

**Body:**
```json
{
  "query": "What is LangChain used for?"
}
```

**Response:**
```json
{
  "response": "LangChain is used to build applications powered by large language models.",
  "sources": ["https://python.langchain.com/docs/get_started/introduction/"]
}
```

**Curl Example:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is LangChain used for?"}'
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/rag-engine.git
cd rag-engine
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Environment Variables
Create a `.env` file based on `.env.example`:

```
SUPABASE_URL=<your_supabase_url>
SUPABASE_KEY=<your_supabase_key>
QDRANT_URL=<your_qdrant_cloud_url>
QDRANT_API_KEY=<your_qdrant_api_key>
REDIS_URL=redis://localhost:6379
GOOGLE_API_KEY=<your_gemini_api_key>
```

### 5️⃣ Run API Server
```bash
uvicorn app.main:app --reload
```

### 6️⃣ Run Ingestion Worker
```bash
python -m app.workers.ingestion_worker
```

(Optional) Run multiple workers to test scalability.

---

## 🧪 Stress Testing

To simulate concurrent ingestion:
```bash
python scripts/stress_test_ingest.py
```
This will trigger 10 simultaneous ingestion jobs against `/ingest-url`.

---

## 📈 Scalability Highlights

- Redis ensures **distributed, idempotent job processing**.
- Workers can scale horizontally (multiple processes or containers).
- Qdrant Cloud handles concurrent read/write loads.
- FastAPI is fully async, capable of handling concurrent queries.
- Supabase maintains ingestion/job consistency.

## ▶️ Demo
See the pipline in action!

https://drive.google.com/file/d/1ydQwsPfh6i1cXSDJ_OeS684h2bDJd8v3/view?usp=sharing