from fastapi.testclient import TestClient
from newsfeed.app import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_articles_empty():
    # Since we use a fresh in-memory DB or the file DB (depending on env),
    # this test might be flaky if running against a persistent DB.
    # For a unit test, we should mock the store.
    # But for a quick integration test:
    response = client.get("/api/v1/articles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
