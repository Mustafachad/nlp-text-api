import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.rate_limit import limiter


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """
    The rate limiter's default storage is in-memory and shared across tests
    within the same process. Reset it before every test so one test's
    requests never count against another test's rate limit.
    """
    limiter.reset()
    yield
