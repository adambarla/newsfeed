import asyncio
from typing import List

from newsfeed.models import ProcessedArticle
from newsfeed.storage import ArticleRepository, VectorIndex


class NewsService:
    def __init__(self, repository: ArticleRepository, index: VectorIndex):
        self.repo = repository
        self.index = index

    async def add_article(self, article: ProcessedArticle) -> ProcessedArticle:
        if article.embedding:
            await asyncio.to_thread(self.index.index, article)
        # TODO: log if we don't index the article

        return await self.repo.save(article)

    async def search_articles(
        self, query_embedding: List[float], limit: int = 20
    ) -> List[ProcessedArticle]:
        relevant_urls = await asyncio.to_thread(
            self.index.search, query_embedding, limit
        )

        if not relevant_urls:
            return []

        articles = await self.repo.get_by_urls(relevant_urls)

        url_to_article = {a.url: a for a in articles}
        sorted_articles = [
            url_to_article[url] for url in relevant_urls if url in url_to_article
        ]

        return sorted_articles
