# Use the official slim Python image to keep the final image size down.
# "slim" omits build tools and docs that aren't needed at runtime.
FROM python:3.13-slim

# Set the working directory inside the container.
# All subsequent commands run relative to this path.
WORKDIR /app

# Copy and install dependencies before copying the rest of the code.
# Docker caches each layer — putting this step first means a code change
# won't re-download all packages, only the layers that actually changed.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the spaCy English model.
RUN python -m spacy download en_core_web_sm

# Download the NLTK corpora required by TextBlob and textstat.
RUN python -m nltk.downloader cmudict punkt punkt_tab

# Copy the application source code.
COPY app/ ./app/

# Document that the container listens on port 8000.
# This doesn't publish the port — that's done at `docker run` time with -p.
EXPOSE 8000

# Start the API server.
# --host 0.0.0.0 makes it reachable from outside the container (not just localhost).
# --workers 1: each worker loads its own copy of spaCy (~160MB), so a single
# worker keeps the memory footprint within free-tier hosting limits (e.g.
# Render's 512MB cap). CPU-bound requests queue briefly under this worker
# instead of running in parallel — an acceptable tradeoff for low-traffic use.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
