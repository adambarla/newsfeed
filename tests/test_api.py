import pytest
import os
import shutil
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient
from newsfeed.app import app
from newsfeed.config import get_settings
from newsfeed.storage import SQLArticleRepository
from newsfeed.models import NewsCategory, ProcessedArticle

# Constants for test paths
TEST_DB_PATH = "./test_data/test_newsfeed.db"
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
TEST_CHROMA_PATH = "./test_data/test_chroma_api"


# Override settings to use file-based test DB
def get_test_settings():
    settings = get_settings()
    settings.DATABASE_URL = TEST_DB_URL
    settings.CHROMADB_PATH = TEST_CHROMA_PATH
    return settings


# Setup the dependency overrides
app.dependency_overrides[get_settings] = get_test_settings

client = TestClient(app)


@pytest.fixture(autouse=True)
async def setup_db():
    # Ensure test directory exists
    os.makedirs("./test_data", exist_ok=True)

    # Remove old DB if exists
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    # Clean up Chroma
    if os.path.exists(TEST_CHROMA_PATH):
        shutil.rmtree(TEST_CHROMA_PATH)

    # Initialize the DB schema
    settings = get_test_settings()
    repo = SQLArticleRepository(settings.DATABASE_URL)
    await repo.init_db()

    yield

    # Teardown
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    if os.path.exists(TEST_CHROMA_PATH):
        shutil.rmtree(TEST_CHROMA_PATH)
    if os.path.exists("./test_data"):
        try:
            os.rmdir("./test_data")
        except OSError:
            pass  # Directory might not be empty


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_articles_empty():
    response = client.get("/api/v1/articles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0


def test_search_endpoint():
    """
    Test the search endpoint by mocking the service internals mostly,
    or better: allow the service to run but mock the LLM/Embedder calls.
    """
    # Mock Embedder
    mock_embedder_instance = MagicMock()
    # Return dummy embedding of length 384 (standard for MiniLM) or just matching Chroma dimension
    # By default Chroma might expect something specific, but for testing we can just use
    # what the code generates.
    # Note: SentenceTransformerEmbedder generates real embeddings.
    # If we want to test end-to-end with Chroma, we need compatible embeddings.
    # So it is easier to mock the Service.search_articles method directly?
    # No, let's mock the embedder to return a fixed list, and ensure we put data in Chroma
    # with that same embedding.

    mock_embedder_instance.embed.return_value = [0.1] * 6  # simplified dimension
    # mock_get_embedder.return_value = mock_embedder_instance

    # We need to Seed some data into the system first using the Service.
    # Since we are testing via API, we can't easily seed via API unless we add an ingestion endpoint.
    # So we should seed via Repository directly.

    # Actually, let's just mock the NewsService.search_articles method
    # to test the API layer handling only.

    with patch(
        "newsfeed.services.news_service.NewsService.search_articles",
        new_callable=AsyncMock,
    ) as mock_search:
        mock_search.return_value = [
            ProcessedArticle(
                url="http://example.com/1",
                title="AI News",
                content="Something about AI",
                category=NewsCategory.AI_EMERGING_TECH,
                source="test",
                published_at=datetime.fromisoformat("2023-01-01T12:00:00"),
            )
        ]

        response = client.get("/api/v1/articles/search?query=AI")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "AI News"
        mock_search.assert_called_once()
