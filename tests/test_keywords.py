def test_keywords_happy_path(client):
    response = client.post(
        "/keywords",
        json={"text": "Marie Curie was a physicist who worked in Paris."},
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body["keywords"]) == {"marie", "curie", "physicist", "paris"}
    entities = {(e["text"], e["label"]) for e in body["entities"]}
    assert ("Marie Curie", "PERSON") in entities
    assert ("Paris", "GPE") in entities


def test_keywords_empty_text_rejected(client):
    response = client.post("/keywords", json={"text": ""})

    assert response.status_code == 422


def test_keywords_whitespace_only_returns_empty_results(client):
    # Unlike /analyze and /summarize, /keywords never checks for
    # blank-after-strip input -- spaCy just finds no nouns/entities in
    # whitespace, so this returns 200 with empty lists rather than a 422.
    # This inconsistency is tracked in CLAUDE.md's known gaps.
    response = client.post("/keywords", json={"text": "   "})

    assert response.status_code == 200
    assert response.json() == {"keywords": [], "entities": []}
