from typing import List, Optional
from abc import ABC, abstractmethod
from uuid import UUID
from newsfeed.models import ProcessedArticle


class ArticleRepository(ABC):
    @abstractmethod
    async def save(self, article: ProcessedArticle) -> ProcessedArticle:
        """Saves an article to persistence."""
        pass

    @abstractmethod
    async def exists(self, url: str) -> bool:
        """Checks if an article with the given URL already exists."""
        pass

    @abstractmethod
    async def get(self, article_id: UUID) -> Optional[ProcessedArticle]:
        """Retrieves an article by ID."""
        pass

    @abstractmethod
    async def list_articles(
        self, category: Optional[str] = None, limit: int = 20, offset: int = 0
    ) -> List[ProcessedArticle]:
        """Lists articles with optional filtering."""
        pass

    @abstractmethod
    async def get_by_urls(self, urls: List[str]) -> List[ProcessedArticle]:
        """Retrieves multiple articles by their URLs."""
        pass
