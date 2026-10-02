# Async RAG Pipeline Architecture

An asynchronous Retrieval-Augmented Generation (RAG) system using **FastAPI**, **Redis Queue (RQ)**, **Qdrant**, and **Gemini**.

---

## Architecture Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant API as FastAPI Server
    participant Redis as Redis (Queue & Store)
    participant Worker as RQ Worker
    participant Qdrant as Qdrant Vector DB
    participant LLM as Gemini LLM

    Client->>API: POST /chat { "query": "..." }
    API->>Redis: Enqueue job (RQ)
    API-->>Client: 202 Accepted { "job_id": "..." }

    Worker->>Redis: Pop job from queue
    Worker->>Qdrant: Similarity search (Embeddings)
    Qdrant-->>Worker: Relevant document chunks
    Worker->>LLM: Generate answer with context
    LLM-->>Worker: Model response
    Worker->>Redis: Save result with job_id

    Client->>API: GET /result/{job_id}
    API->>Redis: Check job status & fetch result
    API-->>Client: 200 OK { "status": "completed", "result": "..." }
```

---

## Core Components

| Component | Technology | Role |
| :--- | :--- | :--- |
| **API Server** | FastAPI | Receives queries, enqueues jobs, and exposes result-polling endpoints. |
| **Message Broker** | Redis (`:6379`) | Manages the task queue via RQ and stores job status/results. |
| **Worker** | Python RQ Worker | Dequeues tasks asynchronously, queries the vector database, and prompts the LLM. |
| **Vector DB** | Qdrant (`:6333`) | Stores document embeddings and executes semantic similarity search. |
| **LLM Engine** | Google Gemini | Generates grounded responses based on retrieved PDF context. |

---

## API Endpoints

### 1. Submit Query
- **`POST /chat`**
- **Request Body:**
  ```json
  { "message": "What is the summary of section 2?" }
  ```
- **Response (202 Accepted):**
  ```json
  { "job_id": "c1f7a2d4-89b5-4b11-a83e-90c283ef31d0", "status": "queued" }
  ```

### 2. Fetch Result
- **`GET /result/{job_id}`**
- **Response (200 OK):**
  ```json
  {
    "job_id": "c1f7a2d4-89b5-4b11-a83e-90c283ef31d0",
    "status": "finished",
    "result": "Based on page 4...",
    "error": null
  }
  ```

---

## Flow Summary

1. **Decoupled Ingestion:** API stays non-blocking and highly available by immediately acknowledging requests with a `job_id`.
2. **Background Execution:** Dedicated workers process CPU/network-intensive vector retrieval and LLM generation tasks.
3. **Result Polling:** Clients poll `/result/{job_id}` until status reaches `finished` or `failed`.