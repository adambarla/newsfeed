import pytest
import os
import shutil
from datetime import datetime

from newsfeed.services.news_service import NewsService
from newsfeed.storage import SQLArticleRepository, ChromaVectorIndex
from newsfeed.models import RawArticle
from newsfeed.config import get_settings
from newsfeed.classification import GeminiNewsClassifier
from newsfeed.embedding import SentenceTransformerEmbedder

# Constants
TEST_DB_PATH = "./test_data/test_integration.db"
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
TEST_CHROMA_PATH = "./test_data/test_integration_chroma"


def has_api_key():
    try:
        settings = get_settings()
        return bool(settings.GEMINI_API_KEY)
    except Exception:
        return False


@pytest.fixture
async def integration_service():
    # Setup
    os.makedirs("./test_data", exist_ok=True)
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    if os.path.exists(TEST_CHROMA_PATH):
        shutil.rmtree(TEST_CHROMA_PATH)

    # Initialize components
    repo = SQLArticleRepository(TEST_DB_URL)
    await repo.init_db()

    index = ChromaVectorIndex(TEST_CHROMA_PATH)

    # Use real components
    classifier = GeminiNewsClassifier()
    embedder = SentenceTransformerEmbedder()  # This will download model if not present

    service = NewsService(repo, index, classifier, embedder)

    yield service

    # Teardown
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    if os.path.exists(TEST_CHROMA_PATH):
        shutil.rmtree(TEST_CHROMA_PATH)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(not has_api_key(), reason="No API Key")
async def test_full_ingestion_pipeline_with_search_quality(integration_service):
    """
    Tests the full pipeline from RawArticle -> Processing -> Storage -> Search.
    Inserts multiple articles to verify semantic search precision.
    """

    articles_data = [
        {
            "url": "https://example.com/ai-1",
            "title": "New AI Model Released",
            "content": "OpenAI has released GPT-5. It is very powerful and changes everything in tech.",
            "source": "tech-feed",
        },
        {
            "url": "https://example.com/linux-1",
            "title": "Linux Kernel Vulnerability",
            "content": "A critical bug in Linux kernel allows root access. Patch immediately.",
            "source": "security-feed",
        },
        {
            "url": "https://example.com/baking-1",
            "title": "Best Croissant Recipe",
            "content": "Mix flour and butter. Fold many times. Bake until golden.",
            "source": "food-blog",
        },
        {
            "url": "https://example.com/gpu-1",
            "title": "NVIDIA RTX 5090 Specs",
            "content": "The new GPU has 32GB VRAM and consumes 600W power.",
            "source": "hardware-feed",
        },
    ]

    print("\nIngesting articles...")
    for data in articles_data:
        raw = RawArticle(
            url=data["url"],
            title=data["title"],
            content=data["content"],
            source=data["source"],
            published_at=datetime.now(),
        )
        await integration_service.process_article(raw)

    # Search Case 1: AI
    print("\nSearching for 'LLM advances'...")
    results = await integration_service.search_articles("LLM advances", limit=2)
    print(f"Top result: {results[0].title}")
    assert results[0].url == "https://example.com/ai-1"
    # Ensure baking recipe is NOT in top results for AI
    assert all(r.url != "https://example.com/baking-1" for r in results)

    # Search Case 2: Security
    print("\nSearching for 'security exploits'...")
    results = await integration_service.search_articles("security exploits", limit=1)
    print(f"Top result: {results[0].title}")
    assert results[0].url == "https://example.com/linux-1"

    # Search Case 3: Cooking (irrelevant to tech but good control)
    print("\nSearching for 'pastry'...")
    results = await integration_service.search_articles("pastry", limit=1)
    print(f"Top result: {results[0].title}")
    assert results[0].url == "https://example.com/baking-1"

    print("\nSearch quality verification passed.")
