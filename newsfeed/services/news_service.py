import asyncio
import logging
from typing import List, Optional

from newsfeed.models import ProcessedArticle, RawArticle
from newsfeed.storage import ArticleRepository, VectorIndex
from newsfeed.classification import NewsClassifier
from newsfeed.embedding import NewsEmbedder

logger = logging.getLogger(__name__)


class NewsService:
    def __init__(
        self,
        repository: ArticleRepository,
        index: VectorIndex,
        classifier: NewsClassifier,
        embedder: NewsEmbedder,
    ):
        self.repo = repository
        self.index = index
        self.classifier = classifier
        self.embedder = embedder

    async def process_article(self, raw: RawArticle) -> Optional[ProcessedArticle]:
        """
        Flow:
        1. Check existence (dedup)
        2. Classify
        3. Embed
        4. Save (DB + Vector)
        """
        if await self.repo.exists(raw.url):
            logger.debug(f"Article already exists, skipping: {raw.title}")
            return None

        logger.debug(f"Processing new article: {raw.title}")
        full_text = f"{raw.title}\n\n{raw.content}"

        try:
            category = await self.classifier.classify(full_text)
            embedding = await asyncio.to_thread(self.embedder.embed, full_text)
        except Exception as e:
            logger.error(f"Error processing article '{raw.title}': {e}")
            return None

        processed = ProcessedArticle(
            url=raw.url,
            title=raw.title,
            content=raw.content,
            category=category,
            source=raw.source,
            published_at=raw.published_at,
            embedding=embedding,
            metadata_fields={
                "author": raw.author,
                "tags": raw.tags,
                "image_url": raw.image_url,
            },
        )

        return await self.add_article(processed)

    async def add_article(
        self, article: ProcessedArticle
    ) -> Optional[ProcessedArticle]:
        if not article.embedding:
            logger.warning(f"Article {article.url} has no embedding, skipping index")
            return None

        try:
            await asyncio.to_thread(self.index.index, article)
            saved_article = await self.repo.save(article)
            logger.debug(f"Successfully saved and indexed article: {article.title}")
            return saved_article
        except Exception as e:
            logger.error(f"Failed to save/index article '{article.title}': {e}")
            return None

    async def search_articles(
        self, query: str, limit: int = 20
    ) -> List[ProcessedArticle]:
        """
        Semantic search using vector embeddings.
        """
        logger.info(f"Searching articles for query: '{query}'")
        try:
            query_embedding = await asyncio.to_thread(self.embedder.embed, query)

            relevant_urls = await asyncio.to_thread(
                self.index.search, query_embedding, limit
            )
        except Exception as e:
            logger.error(f"Error during search for '{query}': {e}")
            return []

        if not relevant_urls:
            logger.debug(f"No relevant articles found for query: '{query}'")
            return []

        articles = await self.repo.get_by_urls(relevant_urls)

        url_to_article = {a.url: a for a in articles}
        sorted_articles = [
            url_to_article[url] for url in relevant_urls if url in url_to_article
        ]

        logger.info(
            f"Found {len(sorted_articles)} relevant articles for query: '{query}'"
        )
        return sorted_articles
