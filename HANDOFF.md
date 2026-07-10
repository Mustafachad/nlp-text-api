# Handoff: nlp-text-api — resume portfolio project

Context for Claude Code picking up this project. This session ran in a
separate chat interface (no repo write access), so **changes described below
may or may not be committed/pushed yet** — run `git log --oneline -15` and
`git status` first to check reality against this document before acting on
anything here.

## Goal

Get `nlp-text-api` finished to a resume-ready state: solid tests, green CI,
a professional README, and a live deployment link. This is one of several
portfolio repos being finished up (`nlp-text-api` was the closest to done).

## Repo

`https://github.com/Mustafachad/nlp-text-api` (branch: `main`)

Note: this repo already has a `CLAUDE.md`. **It is currently stale** — it
says "There is no test suite yet," which is no longer true. Update or merge
it with this file once you've confirmed the current state; don't trust its
"Known gaps" section without re-checking.

## What was actually done this session

1. **Diagnosed and fixed a broken CI pipeline.** `.github/workflows/tests.yml`
   existed but every run was failing on GitHub (confirmed via the Actions API,
   not just assumed) with `MissingCorpusError` — TextBlob needs NLTK corpora
   that the `Dockerfile` downloads but the CI workflow didn't. Fix: added a
   `Download NLTK corpora` step running
   `python -m nltk.downloader cmudict punkt punkt_tab` (same corpora set the
   Dockerfile already used) between the install and test steps.

2. **Added `LICENSE`** — MIT, since there wasn't one.

3. **Added badges to `README.md`** — build status (linked to the
   now-fixed workflow), Python version, license. Placed under the title,
   above the fold.

4. **Added rate limiting** (`slowapi`) to `/analyze`, `/keywords`,
   `/summarize` — 20 requests/minute per IP, since these endpoints run
   spaCy/TextBlob and are CPU-bound, so unbounded requests could degrade the
   service once it's publicly deployed. Implementation notes:
   - New file `app/rate_limit.py` holds the shared `Limiter` instance
     (kept out of `app/main.py` to avoid a circular import with the route
     modules).
   - Each of the three route handlers had its body parameter renamed from
     `request: TextRequest` to `payload: TextRequest`, and gained a new
     `request: Request` parameter — slowapi requires a parameter literally
     named `request` typed as `starlette.requests.Request` to inspect the
     client IP.
   - `app/main.py` registers `app.state.limiter` and the
     `RateLimitExceeded` exception handler.
   - `/health` is intentionally NOT rate limited (used by uptime/health
     checks).
   - Rate limits are per-endpoint, not combined — a client could hit all
     three at 20/min each. Acceptable for this project's scope, flagged
     here in case it matters later.

5. **Added `tests/test_rate_limit.py`** — fires 21 requests at `/summarize`
   and asserts the 21st returns 429. This is a real functional test, not a
   mock.

6. **Added an autouse fixture in `tests/conftest.py`** (`reset_rate_limiter`)
   that calls `limiter.reset()` before every test. Necessary because
   slowapi's default storage is in-memory and shared across the whole test
   process — without the reset, test order/count would make unrelated tests
   flaky once the rate-limit test existed.

7. **Added `.github/dependabot.yml`** — weekly checks on both the `pip`
   ecosystem and `github-actions` ecosystem.

8. **Updated `requirements.txt`** — added `slowapi==0.1.10`, `limits==5.8.0`,
   `Deprecated==1.3.1` (slowapi's transitive deps), pinned to exact versions
   installed and tested locally.

9. **Updated `README.md`** — new "Security" section (rate limiting, input
   caps, Dependabot, no data storage), refreshed project-structure diagram
   and tech stack list to include the above.

All 18 tests were passing locally (venv with corpora downloaded) as of the
end of this session.

## Verify before continuing

```bash
git log --oneline -15          # see what's actually committed
git status                     # see what's actually pushed
pip install -r requirements.txt
python -m nltk.downloader cmudict punkt punkt_tab
pytest -v                      # expect 18 passed
```

If `git log` doesn't show these commits, the user has the changed files
locally (delivered as individual files, not a patch) and still needs to
place them at the right paths and commit/push. Don't redo the analysis —
just help them land it if that's where things stand.

## What's left (not done this session)

**Deployment** — the one remaining item on the original checklist. Plan was
Render, Railway, or Fly.io free tier, deploying the existing `Dockerfile`
directly from GitHub. Needs the user's own account/credentials, so it
wasn't something the prior session could do directly. Once live:
- Put the URL at the very top of the README, above the badges
- Link `/docs` specifically (Swagger UI) so recruiters can try it without a
  terminal
- Consider a platform-side billing/usage alert given the new rate limiting
  is per-IP, not global

## Things NOT to change without asking

- Don't add heavy deps (transformers/torch) — CLAUDE.md's existing
  constraint, still valid, keeps the Docker image small.
- Keep the one-router-per-file pattern in `app/routes/`.
- The extractive summarization and keyword-extraction algorithms are
  intentional (frequency-based, not ML-based) — this is a deliberate
  scope choice for a portfolio piece, not a gap to "improve" with a
  transformer model.
