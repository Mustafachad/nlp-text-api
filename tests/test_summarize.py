TEXT_SIX_SENTENCES = (
    "Marie Curie was a pioneering physicist and chemist. "
    "She conducted groundbreaking research on radioactivity. "
    "Born in Warsaw in 1867, she moved to Paris to study. "
    "She discovered the elements polonium and radium. "
    "She became the first woman to win a Nobel Prize. "
    "She remains the only person to win Nobel Prizes in two sciences."
)


def test_summarize_happy_path(client):
    response = client.post("/summarize", json={"text": TEXT_SIX_SENTENCES})

    assert response.status_code == 200
    body = response.json()
    assert body["sentence_count_original"] == 6
    assert body["sentence_count_summary"] == 2
    assert body["summary"]


def test_summarize_single_sentence_returned_as_is(client):
    response = client.post("/summarize", json={"text": "Just one sentence here."})

    assert response.status_code == 200
    assert response.json() == {
        "summary": "Just one sentence here.",
        "sentence_count_original": 1,
        "sentence_count_summary": 1,
    }


def test_summarize_empty_text_rejected(client):
    response = client.post("/summarize", json={"text": ""})

    assert response.status_code == 422


def test_summarize_whitespace_only_treated_as_single_empty_sentence(client):
    # spaCy parses whitespace-only input as one (empty) sentence, so this
    # hits the single-sentence branch and returns 200 with an empty summary
    # rather than a validation error. Same known inconsistency as /keywords.
    response = client.post("/summarize", json={"text": "   "})

    assert response.status_code == 200
    body = response.json()
    assert body["sentence_count_original"] == 1
    assert body["summary"] == ""
