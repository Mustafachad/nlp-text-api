# CLAUDE.md

Repository: https://github.com/Mustafachad/nlp-text-api (origin, branch: main)

## Project overview

FastAPI service for NLP text analysis, plus a single-page web UI. Portfolio
project — code clarity and clean commit history matter as much as features.

Endpoints: `/health`, `/analyze` (TextBlob sentiment + textstat readability),
`/keywords` (spaCy noun/proper-noun extraction + NER), `/summarize`
(frequency-based extractive summary). The UI at `/` calls the three analysis
endpoints in parallel. Swagger stays at `/docs`.

## Commands

- Run dev server: `uvicorn app.main:app --reload` (from repo root, venv active)
- Install deps: `pip install -r requirements.txt` (downloads the spaCy model
  `en_core_web_sm` from a GitHub release URL pinned in requirements.txt)
- Docker: `docker build -t nlp-text-api . && docker run -p 8000:8000 nlp-text-api`
- There is no test suite yet. When adding one, use pytest with FastAPI's
  TestClient, put tests in `tests/`, and add pytest to requirements.

## Architecture

- `app/main.py` — creates the FastAPI app, includes one router per endpoint,
  mounts `app/static/` and serves `index.html` at `/`.
- `app/routes/<name>.py` — one module per endpoint; each defines its own
  APIRouter. To add an endpoint: new module here, then one
  `app.include_router(...)` line in main.py.
- `app/models.py` — all Pydantic request/response schemas live here, not in
  route files.
- `app/nlp.py` — loads the spaCy model ONCE at import; every route imports
  `nlp` from here. Never call `spacy.load()` inside a route.
- `app/static/index.html` — the entire UI: one file, vanilla JS, no build
  step. Design tokens are CSS variables at the top of its `<style>` block.

## Conventions

- Keep the one-router-per-file pattern; don't merge routes into main.py.
- Docstrings and comments explain WHY, written for a reviewer reading the
  code cold.
- Small, focused commits with imperative-mood messages
  ("Add /language endpoint"), matching the existing history.
- Don't add heavy dependencies (no transformers/torch) without asking —
  the Docker image should stay small.

## Known gaps (good candidate tasks)

- No tests.
- No max length limit on TextRequest.text — large inputs tie up a worker.
- No CI workflow.
- README's project-structure section is out of date (missing Dockerfile and
  `app/static/`).
