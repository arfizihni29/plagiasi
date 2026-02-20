"""
Plagiarism Detection API — Main Application
=============================================
FastAPI application exposing a single POST endpoint for plagiarism checking.
Designed to be called from any frontend (PHP, JS, etc.) via HTTP.

Run with:
    uvicorn app.main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv

# Load .env file BEFORE any module reads os.getenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.services.plagiarism_service import check_plagiarism

# ---------------------------------------------------------------------------
# Logging configuration — useful for debugging in development
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — runs once on startup (e.g. pre-download NLTK data)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-download NLTK tokenizer data at startup so first request is fast."""
    import nltk
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab", quiet=True)
    yield  # application runs here


# ---------------------------------------------------------------------------
# FastAPI app instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Plagiarism Detection API",
    description="Detects plagiarism by comparing text against web sources using TF-IDF cosine similarity.",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — allow all origins so PHP / JS frontends can call this API freely
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response models (Pydantic)
# ---------------------------------------------------------------------------
class PlagiarismRequest(BaseModel):
    """Input model for the plagiarism check endpoint."""
    text: str = Field(
        ...,
        min_length=1,
        description="The text to check for plagiarism.",
        json_schema_extra={"example": "Machine learning is a subset of artificial intelligence."},
    )


class SentenceResult(BaseModel):
    """Per-sentence plagiarism result."""
    sentence: str
    similarity: float
    source: str


class PlagiarismResponse(BaseModel):
    """Full plagiarism check response."""
    overall_similarity: float
    sentences: list[SentenceResult]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post(
    "/check-plagiarism",
    response_model=PlagiarismResponse,
    summary="Check text for plagiarism",
    description="Splits text into sentences, queries the web via Serper.dev, "
                "and computes TF-IDF cosine similarity to detect plagiarism.",
)
async def check_plagiarism_endpoint(request: PlagiarismRequest):
    """
    Main endpoint — accepts text and returns per-sentence similarity scores.
    """
    try:
        logger.info("Received plagiarism check request (%d chars).", len(request.text))
        result = check_plagiarism(request.text)
        return result

    except Exception as exc:
        logger.exception("Unexpected error during plagiarism check.")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(exc)}",
        ) from exc


# ---------------------------------------------------------------------------
# Health-check endpoint
# ---------------------------------------------------------------------------
@app.get("/health", summary="Health check")
async def health_check():
    """Simple health-check endpoint for monitoring."""
    return {"status": "ok"}
