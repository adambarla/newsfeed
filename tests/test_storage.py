import pytest
from newsfeed.models import ProcessedArticle, NewsCategory
from newsfeed.storage import SQLModelStore
from datetime import datetime


@pytest.mark.asyncio
async def test_storage_save_and_retrieve():
    # Use an in-memory SQLite DB for testing
    store = SQLModelStore(database_url="sqlite+aiosqlite:///:memory:")
    await store.init_db()

    article = ProcessedArticle(
        url="https://example.com/article",
        title="Test Article",
        content="This is a test article content.",
        category=NewsCategory.CYBERSECURITY,
        source="test_source",
        published_at=datetime.now(),
        metadata_fields={"tags": ["test", "security"]},
    )

    # Test save
    saved = await store.save_article(article)
    assert saved.id is not None
    assert saved.url == "https://example.com/article"

    # Test retrieval
    retrieved = await store.get_article(saved.id)
    assert retrieved is not None
    assert retrieved.title == "Test Article"
    assert retrieved.category == NewsCategory.CYBERSECURITY
    assert retrieved.metadata_fields["tags"] == ["test", "security"]

    # Test existence check
    exists = await store.article_exists("https://example.com/article")
    assert exists is True

    not_exists = await store.article_exists("https://example.com/nonexistent")
    assert not_exists is False
