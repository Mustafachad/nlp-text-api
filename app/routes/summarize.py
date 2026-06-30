from fastapi import APIRouter, HTTPException
from app.models import TextRequest, SummarizeResponse
from app.nlp import nlp

router = APIRouter()


@router.post("/summarize", response_model=SummarizeResponse, tags=["NLP"])
def summarize_text(request: TextRequest):
    """
    Returns an extractive summary of the submitted text.

    **Extractive** means the summary is built by selecting and returning the
    highest-scoring *original* sentences — no new text is generated. This is
    different from abstractive summarisation (e.g. GPT), which paraphrases.

    Scoring method: word-frequency ranking.
    1. Count how often each content word (non-stop, non-punct) appears.
    2. Normalise counts so the most frequent word scores 1.0.
    3. Score each sentence by summing the normalised scores of its words.
    4. Select the top-ranked sentences and return them in original order
       so the summary reads naturally.

    Summary length: roughly one-third of the original sentence count,
    clamped to a minimum of 1 and a maximum of 7 sentences.
    """
    doc = nlp(request.text)
    sentences = list(doc.sents)

    if len(sentences) == 0:
        raise HTTPException(status_code=422, detail="No sentences found in text.")

    # Single-sentence input: nothing to summarise, return as-is.
    if len(sentences) == 1:
        return SummarizeResponse(
            summary=sentences[0].text.strip(),
            sentence_count_original=1,
            sentence_count_summary=1,
        )

    # --- Step 1: word frequency table ---
    # We use lemmas so "running" and "runs" count as the same word.
    freq: dict[str, int] = {}
    for token in doc:
        if not token.is_stop and not token.is_punct and not token.is_space:
            lemma = token.lemma_.lower()
            freq[lemma] = freq.get(lemma, 0) + 1

    # --- Step 2: normalise by the highest frequency ---
    # Dividing by the max means every score is in [0, 1].
    # This prevents very common words in long texts from dominating.
    if not freq:
        # Edge case: text is entirely stop words / punctuation.
        return SummarizeResponse(
            summary=request.text.strip(),
            sentence_count_original=len(sentences),
            sentence_count_summary=len(sentences),
        )

    max_freq = max(freq.values())
    normalised = {word: count / max_freq for word, count in freq.items()}

    # --- Step 3: score each sentence ---
    sentence_scores: dict[int, float] = {}
    for i, sent in enumerate(sentences):
        score = 0.0
        for token in sent:
            if token.lemma_.lower() in normalised:
                score += normalised[token.lemma_.lower()]
        sentence_scores[i] = score

    # --- Step 4: pick top N sentences ---
    # Clamp to [1, 7] so very short texts aren't over-trimmed and
    # very long texts don't produce summaries almost as long as the original.
    n = max(1, min(7, len(sentences) // 3))
    top_indices = sorted(
        sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:n]
    )  # re-sort by position to preserve reading order

    summary = " ".join(sentences[i].text.strip() for i in top_indices)

    return SummarizeResponse(
        summary=summary,
        sentence_count_original=len(sentences),
        sentence_count_summary=len(top_indices),
    )
