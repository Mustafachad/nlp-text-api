import spacy

# Loaded once at import time and shared across all route modules.
# spacy.load() reads ~50 MB of model weights from disk — doing it per-request
# would add hundreds of milliseconds of latency to every call.
nlp = spacy.load("en_core_web_sm")
