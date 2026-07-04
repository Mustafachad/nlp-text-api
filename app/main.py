"""
NLP Text Analysis API
---------------------
A FastAPI application that exposes REST endpoints for common NLP tasks:
  - /health    — service liveness check
  - /analyze   — sentiment, readability, and basic text stats
  - /keywords  — keyword extraction and named-entity recognition (spaCy)
  - /summarize — extractive sentence summarization

Each route lives in its own module under app/routes/ to keep concerns separated
and make the codebase easy to navigate during a code review or interview.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes import health, analyze, keywords, summarize

app = FastAPI(
    title="NLP Text Analysis API",
    description="REST API for natural language processing tasks built with FastAPI and spaCy.",
    version="1.0.0",
)

# Register route modules.
# Each router groups related endpoints under a shared prefix/tag.
# Adding a new feature = create a new routes module and include it here.
app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(keywords.router)
app.include_router(summarize.router)

# --- Web UI ---
# app/static/ holds the single-page front end. Mounting it under /static
# serves the files as-is; the root route returns index.html so visiting
# http://127.0.0.1:8000/ opens the UI directly. The page calls the same
# /analyze, /keywords and /summarize endpoints documented at /docs.
_STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def serve_ui() -> FileResponse:
    """Serves the web UI."""
    return FileResponse(_STATIC_DIR / "index.html")
