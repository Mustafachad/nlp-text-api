def test_summarize_rate_limit_returns_429_after_limit_exceeded(client):
    payload = {"text": "This is a short sentence used to test the rate limiter."}

    # The limit is 20/minute. The first 20 requests should succeed; the 21st
    # should be rejected with 429 before it ever reaches the summarisation logic.
    for _ in range(20):
        response = client.post("/summarize", json=payload)
        assert response.status_code == 200

    response = client.post("/summarize", json=payload)
    assert response.status_code == 429
