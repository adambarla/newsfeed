import pytest
import os
import shutil
from datetime import datetime
from newsfeed.models import ProcessedArticle, NewsCategory
from newsfeed.storage import SQLArticleRepository, ChromaVectorIndex
from newsfeed.services.news_service import NewsService
from newsfeed.embedding import SentenceTransformerEmbedder


@pytest.mark.asyncio
async def test_repository_crud():
    repo = SQLArticleRepository(database_url="sqlite+aiosqlite:///:memory:")
    await repo.init_db()

    article = ProcessedArticle(
        url="https://example.com/article",
        title="Test Article",
        content="This is a test article content.",
        category=NewsCategory.CYBERSECURITY,
        source="test_source",
        published_at=datetime.now(),
        metadata_fields={"tags": ["test", "security"]},
    )

    # save
    saved = await repo.save(article)
    assert saved.id is not None
    assert saved.url == "https://example.com/article"

    # retrieval
    retrieved = await repo.get(saved.id)
    assert retrieved is not None
    assert retrieved.title == "Test Article"

    # list
    articles = await repo.list_articles()
    assert len(articles) == 1

    # existence check
    exists = await repo.exists("https://example.com/article")
    assert exists is True


@pytest.fixture
async def news_service():
    db_url = "sqlite+aiosqlite:///:memory:"
    chroma_path = "./test_chroma_db_service"

    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)

    repo = SQLArticleRepository(db_url)
    await repo.init_db()

    index = ChromaVectorIndex(chroma_path)

    service = NewsService(repo, index)

    yield service

    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)


@pytest.mark.asyncio
async def test_service_search_flow(news_service):
    embedder = SentenceTransformerEmbedder()

    article_text = (
        "Hackers have discovered a new vulnerability in the firewall firmware."
    )
    article = ProcessedArticle(
        url="https://example.com/security-alert",
        title="Critical Firewall Vulnerability",
        content=article_text,
        category=NewsCategory.CYBERSECURITY,
        source="security_news",
        published_at=datetime.now(),
        # Embed
        embedding=embedder.embed(article_text),
    )

    await news_service.add_article(article)

    query = "firewall bugs"
    query_vector = embedder.embed(query)

    results = await news_service.search_articles(query_vector, limit=1)

    # 5. Verify
    assert len(results) == 1
    assert results[0].url == "https://example.com/security-alert"
