import asyncio
from typing import List, Optional

from newsfeed.models import ProcessedArticle, RawArticle
from newsfeed.storage import ArticleRepository, VectorIndex
from newsfeed.classification import NewsClassifier
from newsfeed.embedding import NewsEmbedder


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
            return None

        full_text = f"{raw.title}\n\n{raw.content}"
        category = await self.classifier.classify(full_text)
        embedding = await asyncio.to_thread(self.embedder.embed, full_text)

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

    async def add_article(self, article: ProcessedArticle) -> ProcessedArticle:
        if not article.embedding:
            print(f"Article {article.url} has no embedding, skipping index")
            return None

        await asyncio.to_thread(self.index.index, article)
        return await self.repo.save(article)

    async def search_articles(
        self, query: str, limit: int = 20
    ) -> List[ProcessedArticle]:
        """
        Semantic search using vector embeddings.
        """
        query_embedding = await asyncio.to_thread(self.embedder.embed, query)

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
