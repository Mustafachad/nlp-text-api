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

from fastapi import FastAPI
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
