from typing import List

import chromadb
from chromadb.config import Settings as ChromaSettings

from newsfeed.models import ProcessedArticle
from newsfeed.storage.semantic.base import VectorIndex


class ChromaVectorIndex(VectorIndex):
    def __init__(self, path: str):
        self.client = chromadb.PersistentClient(
            path=path, settings=ChromaSettings(allow_reset=True)
        )
        self.collection = self.client.get_or_create_collection("news_articles")

    def index(self, article: ProcessedArticle) -> None:
        if not article.embedding:
            return

        self.collection.upsert(
            ids=[article.url],
            embeddings=[article.embedding],
            metadatas=[
                {
                    "category": article.category.value if article.category else "Other",
                    "title": article.title,
                    "uuid": str(article.id),
                }
            ],
        )

    def search(self, query_embedding: List[float], limit: int = 10) -> List[str]:
        results = self.collection.query(
            query_embeddings=[query_embedding], n_results=limit
        )
        # Flatten results
        return results["ids"][0] if results["ids"] else []
