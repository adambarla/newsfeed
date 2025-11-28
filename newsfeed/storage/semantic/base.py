from abc import ABC, abstractmethod
from typing import List

from newsfeed.models import ProcessedArticle


class VectorIndex(ABC):
    """Interface for Vector Storage operations."""

    @abstractmethod
    def index(self, article: ProcessedArticle) -> None:
        """Upserts an article's embedding into the vector store."""
        pass

    @abstractmethod
    def search(self, query_embedding: List[float], limit: int = 10) -> List[str]:
        """Returns list of article URLs matching the query embedding."""
        pass
