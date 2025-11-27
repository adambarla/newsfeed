from datetime import datetime

import pytest

from newsfeed.fetchers import RSSFetcher, RedditFetcher
from newsfeed.models import RawArticle


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rss_fetcher_real_network():
    fetcher = RSSFetcher(
        feed_url="https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
        source_name="nytimes-tech",
    )
    articles = await fetcher.fetch()

    print(f"\nFetched {len(articles)} articles from NYTimes Tech:")
    for i, article in enumerate(articles[:5]):
        print(f"Sample Article {i+1}")
        print(article)
        print("---")

    assert len(articles) > 0
    assert all(isinstance(article, RawArticle) for article in articles)

    article = articles[0]
    assert article.url
    assert article.title
    assert article.source == "nytimes-tech"
    assert isinstance(article.published_at, datetime)
    assert isinstance(article.tags, list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rss_fetcher_ars_technica():
    fetcher = RSSFetcher(
        feed_url="https://feeds.arstechnica.com/arstechnica/index",
        source_name="ars-technica",
    )
    articles = await fetcher.fetch()

    print(f"\nFetched {len(articles)} articles from Ars Technica:")
    for i, article in enumerate(articles[:5]):
        print(f"Sample Article {i+1}")
        print(article)
        print("---")

    assert len(articles) > 0
    assert all(isinstance(article, RawArticle) for article in articles)

    article = articles[0]
    assert article.url
    assert article.title
    assert article.source == "ars-technica"
    assert isinstance(article.published_at, datetime)
    assert isinstance(article.tags, list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rss_fetcher_toms_hardware():
    fetcher = RSSFetcher(
        feed_url="https://www.tomshardware.com/feeds/all", source_name="toms-hardware"
    )
    articles = await fetcher.fetch()

    print(f"\nFetched {len(articles)} articles from Tom's Hardware:")
    for i, article in enumerate(articles[:5]):
        print(f"Sample Article {i+1}")
        print(article)
        print("-------------------")

    assert len(articles) > 0
    assert all(isinstance(article, RawArticle) for article in articles)

    article = articles[0]
    assert article.url
    assert article.title
    assert article.source == "toms-hardware"
    assert isinstance(article.published_at, datetime)
    assert isinstance(article.tags, list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_reddit_fetcher_real_network():
    fetcher = RedditFetcher(subreddit="programming")
    articles = await fetcher.fetch()

    print(f"\nFetched {len(articles)} articles from r/programming:")
    for i, article in enumerate(articles[:5]):
        print(f"Sample Article {i+1}")
        print(article)
        print("---")

    assert len(articles) > 0
    assert all(isinstance(article, RawArticle) for article in articles)

    article = articles[0]
    assert article.url
    assert article.title
    assert article.source == "reddit/r/programming"
    assert isinstance(article.published_at, datetime)
    assert "reddit.com" in article.url
    assert isinstance(article.tags, list)
