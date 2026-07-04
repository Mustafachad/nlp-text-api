def test_analyze_happy_path(client):
    response = client.post(
        "/analyze",
        json={"text": "I love this fantastic, wonderful API. It works great!"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["word_count"] == 9
    assert body["sentence_count"] == 2
    assert body["sentiment"]["label"] == "positive"
    assert body["sentiment"]["polarity"] > 0
    assert body["reading_level"] == "Easy"


def test_analyze_empty_text_rejected(client):
    response = client.post("/analyze", json={"text": ""})

    # Pydantic's min_length=1 constraint on TextRequest rejects this before
    # the route body ever runs.
    assert response.status_code == 422


def test_analyze_whitespace_only_rejected(client):
    response = client.post("/analyze", json={"text": "   "})

    # Passes Pydantic's min_length check, so the route's own strip()-and-check
    # is what catches this.
    assert response.status_code == 422
    assert response.json()["detail"] == "Text must not be empty."
