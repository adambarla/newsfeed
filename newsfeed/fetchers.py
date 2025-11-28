from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any
import logging

from bs4 import BeautifulSoup
import feedparser
import httpx

from newsfeed.models import RawArticle

logger = logging.getLogger(__name__)


class NewsFetcher(ABC):
    @abstractmethod
    async def fetch(self) -> List[RawArticle]:
        """Fetches raw articles from the source."""

    @staticmethod
    def _parse_date(time_struct: Any) -> datetime:
        if time_struct:
            return datetime(*time_struct[:6])
        return datetime.now()

    @classmethod
    def _extract_content(cls, entry: Any) -> str:
        content = ""
        if hasattr(entry, "content") and entry.content:
            content = entry.content[0].value
        elif hasattr(entry, "summary"):
            content = entry.summary

        cleaned = cls._clean_html(content)

        # Check for Reddit placeholder text
        if "submitted by" in cleaned and "/u/" in cleaned and "[link]" in cleaned:
            # It's just a Reddit link wrapper, use the title as content or empty string
            # Using title ensures embeddings have some semantic meaning to work with
            if hasattr(entry, "title"):
                return entry.title
            return ""

        return cleaned

    @staticmethod
    def _clean_html(html_content: str) -> str:
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator="\n", strip=True)

    @staticmethod
    def _extract_tags(entry: Any) -> List[str]:
        tags = []
        if hasattr(entry, "tags"):
            for tag in entry.tags:
                if term := tag.get("term"):
                    tags.append(term)
        return tags

    @staticmethod
    def _extract_image(entry: Any) -> str | None:
        if hasattr(entry, "media_content"):
            for media in entry.media_content:
                if media.get("medium") == "image" and media.get("url"):
                    return media.get("url")
        return None


class RSSFetcher(NewsFetcher):
    def __init__(self, feed_url: str, source_name: str):
        self.feed_url = feed_url
        self.source_name = source_name

    async def fetch(self) -> List[RawArticle]:
        logger.debug(f"Fetching RSS feed for {self.source_name}: {self.feed_url}")
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(self.feed_url)
                response.raise_for_status()
                feed = feedparser.parse(response.text)
        except Exception as e:
            logger.error(f"Failed to fetch RSS feed {self.feed_url}: {e}")
            raise

        articles = []
        for entry in feed.entries:
            time_struct = entry.get("published_parsed") or entry.get("updated_parsed")
            author = entry.get("author") or entry.get("dc:creator")

            articles.append(
                RawArticle(
                    url=entry.link,
                    title=entry.title,
                    content=self._extract_content(entry),
                    source=self.source_name,
                    published_at=self._parse_date(time_struct),
                    author=author,
                    tags=self._extract_tags(entry),
                    image_url=self._extract_image(entry),
                )
            )

        logger.info(f"Fetched {len(articles)} articles from {self.source_name}")
        return articles


class RedditFetcher(NewsFetcher):
    def __init__(self, subreddit: str):
        self.subreddit = subreddit
        self.feed_url = f"https://www.reddit.com/r/{subreddit}/.rss"

    async def fetch(self) -> List[RawArticle]:
        logger.debug(f"Fetching Reddit feed for r/{self.subreddit}: {self.feed_url}")
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                headers = {"User-Agent": "newsfeed-bot/1.0"}
                response = await client.get(self.feed_url, headers=headers)
                response.raise_for_status()
                feed = feedparser.parse(response.text)
        except Exception as e:
            logger.error(f"Failed to fetch Reddit feed {self.feed_url}: {e}")
            raise

        articles = []
        for entry in feed.entries:
            time_struct = entry.get("published_parsed") or entry.get("updated_parsed")
            author = entry.get("author") or self._extract_reddit_author(entry)

            articles.append(
                RawArticle(
                    url=entry.link,
                    title=entry.title,
                    content=self._extract_content(entry),
                    source=f"reddit/r/{self.subreddit}",
                    published_at=self._parse_date(time_struct),
                    author=author,
                    tags=self._extract_tags(entry),
                    image_url=self._extract_image(entry),
                )
            )

        logger.info(f"Fetched {len(articles)} articles from r/{self.subreddit}")
        return articles

    @staticmethod
    def _extract_reddit_author(entry: Any) -> str | None:
        if hasattr(entry, "author_detail") and entry.author_detail:
            return entry.author_detail.get("name")
        return None
