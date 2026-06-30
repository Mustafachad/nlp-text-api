"""
Pydantic models for request and response validation.

Pydantic automatically validates incoming JSON against these schemas and
returns a 422 error with a clear message if the data doesn't match — no
manual validation code needed. It also drives FastAPI's auto-generated docs.
"""

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared request model (reused by all three NLP endpoints)
# ---------------------------------------------------------------------------

class TextRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="The text to analyse.",
        examples=["FastAPI makes building APIs surprisingly enjoyable."],
    )


# ---------------------------------------------------------------------------
# /analyze response models
# ---------------------------------------------------------------------------

class Sentiment(BaseModel):
    polarity: float = Field(
        description="Ranges from -1.0 (very negative) to 1.0 (very positive)."
    )
    subjectivity: float = Field(
        description="Ranges from 0.0 (objective fact) to 1.0 (personal opinion)."
    )
    label: str = Field(
        description="Human-readable sentiment: 'positive', 'negative', or 'neutral'."
    )


class AnalyzeResponse(BaseModel):
    word_count: int
    sentence_count: int
    sentiment: Sentiment
    flesch_reading_ease: float = Field(
        description="0–100 score. Higher = easier to read. 60–70 is plain English."
    )
    reading_level: str = Field(
        description="Plain-English label derived from the Flesch score."
    )


# ---------------------------------------------------------------------------
# /keywords response models
# ---------------------------------------------------------------------------

class Entity(BaseModel):
    text: str = Field(description="The surface form of the named entity.")
    label: str = Field(description="Entity type, e.g. PERSON, ORG, GPE.")


class KeywordsResponse(BaseModel):
    keywords: list[str] = Field(
        description="High-frequency content words (nouns and proper nouns), deduplicated."
    )
    entities: list[Entity] = Field(
        description="Named entities detected by spaCy's NER model."
    )


# ---------------------------------------------------------------------------
# /summarize response models
# ---------------------------------------------------------------------------

class SummarizeResponse(BaseModel):
    summary: str = Field(
        description="Extractive summary: the top-ranked sentences from the source text."
    )
    sentence_count_original: int
    sentence_count_summary: int
