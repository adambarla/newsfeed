import pytest
from unittest.mock import AsyncMock, patch
from newsfeed.scheduler import run_ingestion, start_scheduler
from newsfeed.models import RawArticle


@pytest.mark.asyncio
async def test_run_ingestion():
    # Mock data
    mock_article = RawArticle(
        url="http://test.com",
        title="Test Article",
        content="Test Content",
        source="test_source",
        published_at=None,
    )

    # Mock Service
    mock_service = AsyncMock()
    mock_service.process_article.return_value = True  # Simulate saved article

    # Mock Fetcher
    mock_fetcher_instance = AsyncMock()
    mock_fetcher_instance.fetch.return_value = [mock_article]

    # Patch dependencies
    with patch("newsfeed.scheduler.get_news_service", return_value=mock_service), patch(
        "newsfeed.scheduler.RSSFetcher", return_value=mock_fetcher_instance
    ) as mock_rss_cls, patch(
        "newsfeed.scheduler.RedditFetcher", return_value=mock_fetcher_instance
    ) as mock_reddit_cls:
        # Override SOURCES for the test to be deterministic and fast
        with patch(
            "newsfeed.scheduler.SOURCES",
            [
                {"type": "rss", "url": "http://rss.test", "name": "RSS Test"},
                {"type": "reddit", "name": "reddit_test"},
            ],
        ):
            await run_ingestion()

            # Verify Fetchers were initialized and called
            mock_rss_cls.assert_called_with(
                feed_url="http://rss.test", source_name="RSS Test"
            )
            mock_reddit_cls.assert_called_with(subreddit="reddit_test")
            assert mock_fetcher_instance.fetch.call_count == 2

            # Verify Service processed the article
            # 2 sources * 1 article each = 2 calls
            assert mock_service.process_article.call_count == 2
            mock_service.process_article.assert_called_with(mock_article)


def test_start_scheduler():
    with patch("newsfeed.scheduler.AsyncIOScheduler") as mock_scheduler_cls, patch(
        "newsfeed.scheduler.get_settings"
    ) as mock_settings:
        mock_settings.return_value.FETCH_INTERVAL_MINUTES = 10
        mock_scheduler = mock_scheduler_cls.return_value

        start_scheduler()

        assert mock_scheduler.add_job.call_count == 2
        mock_scheduler.start.assert_called_once()
