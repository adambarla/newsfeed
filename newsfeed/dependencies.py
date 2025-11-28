from functools import lru_cache

from newsfeed.classification import GeminiNewsClassifier
from newsfeed.config import get_settings
from newsfeed.embedding import SentenceTransformerEmbedder
from newsfeed.services.news_service import NewsService
from newsfeed.storage import SQLArticleRepository, ChromaVectorIndex


@lru_cache
def get_repository() -> SQLArticleRepository:
    settings = get_settings()
    return SQLArticleRepository(settings.DATABASE_URL)


@lru_cache
def get_vector_index() -> ChromaVectorIndex:
    settings = get_settings()
    return ChromaVectorIndex(settings.CHROMADB_PATH)


@lru_cache
def get_embedder() -> SentenceTransformerEmbedder:
    return SentenceTransformerEmbedder()


@lru_cache
def get_classifier() -> GeminiNewsClassifier:
    return GeminiNewsClassifier()


@lru_cache
def get_news_service() -> NewsService:
    return NewsService(
        repository=get_repository(),
        index=get_vector_index(),
        classifier=get_classifier(),
        embedder=get_embedder(),
    )
