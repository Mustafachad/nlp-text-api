from fastapi import APIRouter, HTTPException, Request
from textblob import TextBlob
import textstat

from app.models import TextRequest, AnalyzeResponse, Sentiment
from app.rate_limit import limiter

router = APIRouter()


def _flesch_label(score: float) -> str:
    """
    Maps a Flesch Reading Ease score to a plain-English reading level.

    The Flesch formula was developed by Rudolf Flesch (1948) and is one of
    the oldest and most widely used readability metrics. It rewards shorter
    words and shorter sentences with a higher (easier) score.

    Score ranges (per the original Flesch scale):
      90–100  Very Easy    — comic books, basic English
      80–90   Easy         — pulp fiction
      70–80   Fairly Easy  — popular novels
      60–70   Standard     — plain-English target for most web content
      50–60   Fairly Diff  — academic writing
      30–50   Difficult    — academic journals
      0–30    Very Confus  — legal / scientific documents
    """
    if score >= 90:
        return "Very Easy"
    elif score >= 80:
        return "Easy"
    elif score >= 70:
        return "Fairly Easy"
    elif score >= 60:
        return "Standard"
    elif score >= 50:
        return "Fairly Difficult"
    elif score >= 30:
        return "Difficult"
    else:
        return "Very Confusing"


def _sentiment_label(polarity: float) -> str:
    """Converts a TextBlob polarity float to a human-readable label."""
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"


@router.post("/analyze", response_model=AnalyzeResponse, tags=["NLP"])
@limiter.limit("20/minute")
def analyze_text(request: Request, payload: TextRequest):
    """
    Analyses the submitted text and returns:
    - **sentiment** — polarity, subjectivity, and a plain-English label (TextBlob)
    - **flesch_reading_ease** — readability score from 0 (hardest) to 100 (easiest)
    - **reading_level** — plain-English label for the Flesch score
    - **word_count** and **sentence_count** — basic text statistics
    """
    text = payload.text.strip()

    if not text:
        raise HTTPException(status_code=422, detail="Text must not be empty.")

    # --- TextBlob analysis ---
    # TextBlob wraps NLTK under the hood. .sentiment returns a namedtuple
    # with polarity [-1, 1] and subjectivity [0, 1].
    blob = TextBlob(text)
    polarity = round(blob.sentiment.polarity, 4)
    subjectivity = round(blob.sentiment.subjectivity, 4)

    # --- Readability ---
    # textstat.flesch_reading_ease() implements the Flesch (1948) formula:
    # 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
    flesch = round(textstat.flesch_reading_ease(text), 2)

    # --- Basic counts ---
    # TextBlob tokenises words and sentences using NLTK's Punkt tokeniser,
    # which handles abbreviations and decimals better than a naive split().
    word_count = len(blob.words)
    sentence_count = len(blob.sentences)

    return AnalyzeResponse(
        word_count=word_count,
        sentence_count=sentence_count,
        sentiment=Sentiment(
            polarity=polarity,
            subjectivity=subjectivity,
            label=_sentiment_label(polarity),
        ),
        flesch_reading_ease=flesch,
        reading_level=_flesch_label(flesch),
    )
