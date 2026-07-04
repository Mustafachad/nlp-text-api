import pytest

# TextRequest.max_length=20_000 is shared by /analyze, /keywords, and
# /summarize, so this validation only needs to be proven once per route.
ENDPOINTS = ["/analyze", "/keywords", "/summarize"]


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_oversized_text_rejected(client, endpoint):
    oversized_text = "word " * 5000  # 25,000 characters, over the limit

    response = client.post(endpoint, json={"text": oversized_text})

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "string_too_long"


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_text_at_max_length_accepted(client, endpoint):
    text_at_limit = "word " * 4000  # 20,000 characters exactly

    response = client.post(endpoint, json={"text": text_at_limit})

    assert response.status_code == 200
