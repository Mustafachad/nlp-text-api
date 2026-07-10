# NLP Text Analysis API

**Live demo:** [nlp-text-api.onrender.com](https://nlp-text-api.onrender.com) — try the endpoints directly in [Swagger UI](https://nlp-text-api.onrender.com/docs).
> Hosted on Render's free tier, which spins down after periods of inactivity — the first request after idle time may take 30–60s to wake it up.

[![Tests](https://github.com/Mustafachad/nlp-text-api/actions/workflows/tests.yml/badge.svg)](https://github.com/Mustafachad/nlp-text-api/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.13-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A REST API that performs natural language processing on text input. Built with FastAPI and spaCy as a portfolio project connecting an Applied Linguistics background to practical software engineering.

## Features

A single-page web UI at `/` calls all three analysis endpoints in parallel
and renders sentiment, readability, annotated entities, keywords, and the
summary side by side.

| Endpoint | What it does |
|---|---|
| `GET /health` | Service liveness check — status and version |
| `POST /analyze` | Sentiment (polarity + subjectivity), Flesch readability score, word count, sentence count |
| `POST /keywords` | Frequency-ranked keywords via POS tagging, named entity recognition (people, places, organisations) |
| `POST /summarize` | Extractive summary — top-ranked sentences returned in original order |

## Tech Stack

- **FastAPI** — API framework with automatic request validation and interactive docs
- **spaCy** (`en_core_web_sm`) — POS tagging, dependency parsing, named entity recognition
- **TextBlob** — sentiment analysis (polarity and subjectivity scoring)
- **textstat** — Flesch Reading Ease score
- **Pydantic** — request/response schema validation
- **slowapi** — per-IP rate limiting on the NLP endpoints
- **Uvicorn** — ASGI server

## Project Structure

```
nlp-text-api/
├── .github/
│   ├── workflows/
│   │   └── tests.yml     # CI: installs deps and runs pytest on every push/PR
│   └── dependabot.yml    # Weekly checks for vulnerable pip/Actions dependencies
├── app/
│   ├── main.py           # FastAPI app setup, router registration, serves the UI
│   ├── nlp.py            # Shared spaCy model instance (loaded once)
│   ├── models.py         # Pydantic request/response schemas
│   ├── rate_limit.py     # Shared slowapi Limiter instance
│   ├── routes/
│   │   ├── health.py     # GET  /health
│   │   ├── analyze.py    # POST /analyze   (rate limited: 20/min per IP)
│   │   ├── keywords.py   # POST /keywords  (rate limited: 20/min per IP)
│   │   └── summarize.py  # POST /summarize (rate limited: 20/min per IP)
│   └── static/
│       └── index.html    # Single-page web UI (vanilla JS, no build step)
├── tests/                 # pytest suite covering all endpoints + rate limiting
├── Dockerfile
├── requirements.txt
├── LICENSE
└── .gitignore
```

## Setup

**Prerequisites:** Python 3.8+, Git

```bash
# Clone the repo
git clone https://github.com/Mustafachad/nlp-text-api.git
cd nlp-text-api

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download the spaCy English model
python -m spacy download en_core_web_sm
```

## Running the API

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

The server starts at `http://127.0.0.1:8000`.

The web UI is served at `/`. Interactive API docs (Swagger UI) are
auto-generated at `http://127.0.0.1:8000/docs`.

## Running with Docker

```bash
docker build -t nlp-text-api .
docker run -p 8000:8000 nlp-text-api
```

The UI and API are then available at `http://127.0.0.1:8000` exactly as
in local development.

## Running Tests

```bash
source venv/bin/activate
pip install pytest   # already in requirements.txt
pytest
```

Tests use FastAPI's `TestClient` and live in `tests/`, with one file per
endpoint plus shared request-validation tests. A GitHub Actions workflow
(`.github/workflows/tests.yml`) runs the suite on every push and pull
request to `main`.

## Example Requests

### `POST /analyze`

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "FastAPI is a brilliant framework. Building APIs has never felt this clean."}'
```

```json
{
  "word_count": 12,
  "sentence_count": 2,
  "sentiment": {
    "polarity": 0.6333,
    "subjectivity": 0.85,
    "label": "positive"
  },
  "flesch_reading_ease": 87.95,
  "reading_level": "Easy"
}
```

### `POST /keywords`

```bash
curl -X POST http://127.0.0.1:8000/keywords \
  -H "Content-Type: application/json" \
  -d '{"text": "Elon Musk founded SpaceX in California to reduce the cost of space transportation."}'
```

```json
{
  "keywords": ["elon", "musk", "spacex", "california", "cost", "space", "transportation"],
  "entities": [
    {"text": "Elon Musk", "label": "PERSON"},
    {"text": "California", "label": "GPE"}
  ]
}
```

### `POST /summarize`

```bash
curl -X POST http://127.0.0.1:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Natural language processing is a subfield of linguistics and AI. It focuses on the interaction between computers and human language. NLP tasks include sentiment analysis, machine translation, and summarisation. Modern systems use neural networks trained on massive corpora."}'
```

```json
{
  "summary": "NLP tasks include sentiment analysis, machine translation, and summarisation.",
  "sentence_count_original": 4,
  "sentence_count_summary": 1
}
```

## How It Works

**Sentiment** — TextBlob assigns a polarity score from -1.0 (negative) to 1.0 (positive) and a subjectivity score from 0.0 (objective) to 1.0 (subjective) using a lexicon-based approach.

**Readability** — The Flesch Reading Ease formula (`206.835 - 1.015×(words/sentences) - 84.6×(syllables/words)`) rewards shorter words and shorter sentences with a higher score. Scores above 60 are considered plain English.

**Keywords** — spaCy's POS tagger identifies nouns and proper nouns. Stop words are filtered out and tokens are lemmatised (`"APIs" → "api"`) before frequency ranking, so surface form variation doesn't split counts.

**Summarisation** — Each sentence is scored by summing the normalised frequencies of its content words. The top-ranked sentences (roughly one-third of the original, capped at 7) are returned in their original order so the summary reads naturally. This is *extractive* summarisation — no text is generated, only selected.

## Security

- **Rate limiting** — `/analyze`, `/keywords`, and `/summarize` are limited to 20 requests/minute per IP ([slowapi](https://github.com/laurentS/slowapi)). These endpoints run spaCy and TextBlob, which are CPU-bound, so an unbounded client could otherwise degrade the service for everyone else.
- **Input limits** — request text is capped at 20,000 characters (`Field(max_length=20_000)` in `app/models.py`) so a single oversized request can't tie up a worker.
- **Dependency scanning** — [Dependabot](.github/dependabot.yml) checks weekly for known vulnerabilities in both pip packages and the GitHub Actions used in CI.
- **No secrets or user data storage** — the API is stateless; nothing submitted is persisted or logged beyond standard request logs.

## License

MIT — see [LICENSE](LICENSE).

## Related Projects

- [Raspberry Pi Crypto Data Pipeline](https://github.com/Mustafachad) — real-time cryptocurrency data collection using Python, PostgreSQL, Grafana, and cron on a Raspberry Pi.
