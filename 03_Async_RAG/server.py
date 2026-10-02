import sys
from pathlib import Path
from typing import Any, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from rq.job import Job, NoSuchJobError

# Add current folder to sys.path so modules can be imported directly
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# Add project root to sys.path for utils
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from client.rq_client import queue, redis_conn

app = FastAPI(
    title="Async RAG API",
    description="Asynchronous RAG service using FastAPI, RQ, Redis, Qdrant, and Gemini.",
    version="1.0.0",
)


# ---------------------------------------------------------
# Pydantic Request / Response Models
# ---------------------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The user question / query", example="What is RAG?")


class ChatResponse(BaseModel):
    job_id: str
    status: str
    message: str


class ResultResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------
@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Async RAG API",
        "docs_url": "/docs"
    }


@app.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Chat"],
    summary="Enqueue a chat query for asynchronous processing",
)
def chat_endpoint(payload: ChatRequest):
    """
    Submits a query to the background task queue and immediately returns a job ID.
    """
    try:
        job = queue.enqueue("queues.worker.process_query", payload.message)
        return ChatResponse(
            job_id=job.id,
            status=job.get_status(),
            message="Task enqueued successfully. Poll /result/{job_id} for answers."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enqueue task: {str(e)}"
        )


@app.get(
    "/result/{job_id}",
    response_model=ResultResponse,
    tags=["Chat"],
    summary="Fetch the status and result of a queued query",
)
def get_result(job_id: str):
    """
    Checks the status of the job in Redis.
    Possible statuses: 'queued', 'started', 'finished', 'failed'.
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except NoSuchJobError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found or expired."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking job status: {str(e)}"
        )

    job_status = job.get_status()
    error_msg = str(job.exc_info) if job.is_failed else None

    return ResultResponse(
        job_id=job.id,
        status=job_status,
        result=job.result if job.is_finished else None,
        error=error_msg
    )
