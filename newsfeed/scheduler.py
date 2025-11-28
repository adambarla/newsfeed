import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from newsfeed.config import get_settings
from newsfeed.dependencies import get_news_service
from newsfeed.fetchers import RSSFetcher, RedditFetcher, NewsFetcher

logger = logging.getLogger(__name__)

# Configuration of sources to fetch
SOURCES = [
    # Reddit Sources
    {"type": "reddit", "name": "programming"},
    {"type": "reddit", "name": "technology"},
    {"type": "reddit", "name": "cybersecurity"},
    {"type": "reddit", "name": "artificial"},
    # RSS Sources
    {
        "type": "rss",
        "url": "http://feeds.arstechnica.com/arstechnica/index",
        "name": "Ars Technica",
    },
    {
        "type": "rss",
        "url": "https://www.tomshardware.com/feeds/all",
        "name": "Tom's Hardware",
    },
]


async def run_ingestion():
    """
    Main scheduled task.
    Iterates over all sources, fetches articles, and processes them through the service.
    """
    logger.info("Starting scheduled ingestion job...")
    service = get_news_service()

    for source_config in SOURCES:
        source_name = source_config["name"]
        try:
            fetcher: NewsFetcher
            if source_config["type"] == "reddit":
                fetcher = RedditFetcher(subreddit=source_name)
            elif source_config["type"] == "rss":
                fetcher = RSSFetcher(
                    feed_url=source_config["url"], source_name=source_name
                )
            else:
                logger.warning(f"Unknown source type: {source_config['type']}")
                continue

            logger.info(f"Fetching from {source_name}...")
            articles = await fetcher.fetch()
            logger.info(f"Found {len(articles)} articles from {source_name}")

            new_count = 0
            for article in articles:
                # Process article (Dedup -> Classify -> Embed -> Save)
                result = await service.process_article(article)
                if result:
                    new_count += 1

            logger.info(f"Saved {new_count} new articles from {source_name}")

        except Exception as e:
            logger.error(f"Error processing source {source_name}: {e}", exc_info=True)

    settings = get_settings()
    next_run = datetime.now() + timedelta(minutes=settings.FETCH_INTERVAL_MINUTES)
    logger.info(
        f"Ingestion job completed. Next run scheduled at: {next_run.strftime('%H:%M:%S')}"
    )


def start_scheduler():
    """Starts the AsyncIOScheduler."""
    settings = get_settings()
    scheduler = AsyncIOScheduler()

    # Add the ingestion job
    scheduler.add_job(
        run_ingestion,
        trigger=IntervalTrigger(minutes=settings.FETCH_INTERVAL_MINUTES),
        id="ingestion_job",
        replace_existing=True,
    )

    # Run immediately once on startup
    scheduler.add_job(run_ingestion, id="startup_ingestion")

    scheduler.start()
    logger.info(
        f"Scheduler started with interval: {settings.FETCH_INTERVAL_MINUTES} minutes"
    )
    return scheduler
