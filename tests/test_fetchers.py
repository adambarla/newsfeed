from datetime import datetime
from pathlib import Path

import httpx
import pytest
from unittest.mock import AsyncMock, patch

from newsfeed.fetchers import RSSFetcher, RedditFetcher
from newsfeed.models import RawArticle


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_rss_content():
    return (FIXTURES_DIR / "sample_rss.xml").read_text()


@pytest.fixture
def reddit_rss_content():
    return (FIXTURES_DIR / "reddit_rss.xml").read_text()


@pytest.mark.asyncio
async def test_rss_fetcher_fetch(sample_rss_content):
    fetcher = RSSFetcher(feed_url="https://example.com/feed", source_name="test-source")

    with patch("newsfeed.fetchers.httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.text = sample_rss_content
        mock_response.raise_for_status = lambda: None

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        articles = await fetcher.fetch()

    assert len(articles) == 3
    assert all(isinstance(article, RawArticle) for article in articles)

    article1 = articles[0]
    assert article1.url == "https://example.com/article1"
    assert article1.title == "Test Article 1"
    assert article1.content == "This is the content of article 1"
    assert article1.source == "test-source"
    assert isinstance(article1.published_at, datetime)
    assert article1.author == "author1@example.com (John Doe)"
    # Tags and image added to fixture
    assert article1.tags == ["Tech", "AI"]
    assert article1.image_url == "https://example.com/image1.jpg"

    article2 = articles[1]
    assert article2.url == "https://example.com/article2"
    assert article2.title == "Test Article 2"
    assert article2.author == "author2@example.com (Jane Smith)"

    article3 = articles[2]
    assert article3.url == "https://example.com/article3"
    assert article3.author is None


@pytest.mark.asyncio
async def test_rss_fetcher_http_error():
    fetcher = RSSFetcher(feed_url="https://example.com/feed", source_name="test-source")

    with patch("newsfeed.fetchers.httpx.AsyncClient") as mock_client:
        mock_request = AsyncMock()
        mock_response_obj = AsyncMock()
        error = httpx.HTTPStatusError(
            "Not Found", request=mock_request, response=mock_response_obj
        )

        def raise_error():
            raise error

        mock_response = AsyncMock()
        mock_response.raise_for_status = raise_error

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        with pytest.raises(httpx.HTTPStatusError):
            await fetcher.fetch()


@pytest.mark.asyncio
async def test_reddit_fetcher_fetch(reddit_rss_content):
    fetcher = RedditFetcher(subreddit="programming")

    with patch("newsfeed.fetchers.httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.text = reddit_rss_content
        mock_response.raise_for_status = lambda: None

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        articles = await fetcher.fetch()

    assert len(articles) == 2
    assert all(isinstance(article, RawArticle) for article in articles)

    article1 = articles[0]
    assert (
        article1.url
        == "https://www.reddit.com/r/programming/comments/abc123/great_article_about_python_async/"
    )
    assert article1.title == "Great article about Python async"
    assert article1.source == "reddit/r/programming"
    assert article1.author == "reddit_user_1"
    assert isinstance(article1.published_at, datetime)
    assert article1.tags == ["programming"]

    article2 = articles[1]
    assert article2.source == "reddit/r/programming"
    assert article2.author == "reddit_user_2"


@pytest.mark.asyncio
async def test_reddit_fetcher_url_construction():
    fetcher = RedditFetcher(subreddit="technology")
    assert fetcher.feed_url == "https://www.reddit.com/r/technology/.rss"


@pytest.mark.asyncio
async def test_reddit_fetcher_http_error():
    fetcher = RedditFetcher(subreddit="programming")

    with patch("newsfeed.fetchers.httpx.AsyncClient") as mock_client:
        mock_request = AsyncMock()
        mock_response_obj = AsyncMock()
        error = httpx.HTTPStatusError(
            "Not Found", request=mock_request, response=mock_response_obj
        )

        def raise_error():
            raise error

        mock_response = AsyncMock()
        mock_response.raise_for_status = raise_error

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        with pytest.raises(httpx.HTTPStatusError):
            await fetcher.fetch()
