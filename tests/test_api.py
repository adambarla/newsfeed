import pytest
import os
import shutil
from fastapi.testclient import TestClient
from newsfeed.app import app
from newsfeed.config import get_settings
from newsfeed.storage import SQLArticleRepository

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
