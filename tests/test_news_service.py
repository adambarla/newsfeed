import pytest
from unittest.mock import MagicMock, AsyncMock
from newsfeed.services.news_service import NewsService
from newsfeed.models import RawArticle, ProcessedArticle, NewsCategory
from datetime import datetime


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.exists = AsyncMock(return_value=False)
    repo.save = AsyncMock(side_effect=lambda x: x)
    repo.get_by_urls = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_index():
    index = MagicMock()
    index.index = MagicMock()
    index.search = MagicMock(return_value=[])
    return index


@pytest.fixture
def mock_classifier():
    classifier = MagicMock()
    classifier.classify = AsyncMock(return_value=NewsCategory.AI_EMERGING_TECH)
    return classifier


@pytest.fixture
def mock_embedder():
    embedder = MagicMock()
    embedder.embed = MagicMock(return_value=[0.1, 0.2, 0.3])
    return embedder


@pytest.fixture
def news_service(mock_repo, mock_index, mock_classifier, mock_embedder):
    return NewsService(mock_repo, mock_index, mock_classifier, mock_embedder)


@pytest.mark.asyncio
async def test_process_article_success(
    news_service, mock_repo, mock_index, mock_classifier
):
    raw_article = RawArticle(
        url="http://example.com/ai-news",
        title="AI Breakthrough",
        content="AI is amazing.",
        source="tech-news",
        published_at=datetime.now(),
    )

    result = await news_service.process_article(raw_article)

    assert result is not None
    assert result.category == NewsCategory.AI_EMERGING_TECH
    assert result.embedding == [0.1, 0.2, 0.3]

    # Verify interactions
    mock_repo.exists.assert_called_once_with(raw_article.url)
    mock_classifier.classify.assert_called_once()
    mock_index.index.assert_called_once()
    mock_repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_process_article_duplicate(news_service, mock_repo, mock_index):
    # Setup repo to return True for exists
    mock_repo.exists.return_value = True

    raw_article = RawArticle(
        url="http://example.com/duplicate",
        title="Duplicate",
        content="Content",
        source="test",
        published_at=datetime.now(),
    )

    result = await news_service.process_article(raw_article)

    assert result is None
    mock_repo.exists.assert_called_once_with(raw_article.url)
    mock_index.index.assert_not_called()
    mock_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_search_articles(news_service, mock_index, mock_repo, mock_embedder):
    query = "AI technology"

    # Setup mocks for search flow
    mock_embedder.embed.return_value = [0.1, 0.2]  # Query embedding
    mock_index.search.return_value = ["http://example.com/1", "http://example.com/2"]

    # Repo returns objects for the URLs found
    articles = [
        ProcessedArticle(
            url="http://example.com/1",
            title="A1",
            content="C1",
            category=NewsCategory.AI_EMERGING_TECH,
            source="s",
            published_at=datetime.now(),
        ),
        ProcessedArticle(
            url="http://example.com/2",
            title="A2",
            content="C2",
            category=NewsCategory.CYBERSECURITY,
            source="s",
            published_at=datetime.now(),
        ),
    ]
    mock_repo.get_by_urls.return_value = articles

    results = await news_service.search_articles(query)

    assert len(results) == 2
    assert results[0].url == "http://example.com/1"

    mock_embedder.embed.assert_called_with(query)
    mock_index.search.assert_called_once()
    mock_repo.get_by_urls.assert_called_once_with(
        ["http://example.com/1", "http://example.com/2"]
    )


@pytest.mark.asyncio
async def test_add_article_no_embedding(news_service, mock_index, mock_repo):
    # Create article without embedding
    article = ProcessedArticle(
        url="http://example.com/no-embed",
        title="No Embed",
        content="Content",
        category=NewsCategory.OTHER,
        source="s",
        published_at=datetime.now(),
        embedding=None,
    )

    result = await news_service.add_article(article)

    assert result is None
    mock_index.index.assert_not_called()
    mock_repo.save.assert_not_called()
