import logging
from typing import List

import chromadb
from chromadb.config import Settings as ChromaSettings

from newsfeed.models import ProcessedArticle
from newsfeed.storage.semantic.base import VectorIndex

logger = logging.getLogger(__name__)


class ChromaVectorIndex(VectorIndex):
    def __init__(self, path: str):
        logger.info(f"Initializing ChromaDB at path: {path}")
        try:
            self.client = chromadb.PersistentClient(
                path=path, settings=ChromaSettings(allow_reset=True)
            )
            self.collection = self.client.get_or_create_collection("news_articles")
            logger.info("ChromaDB initialized and collection 'news_articles' ready.")
        except Exception as e:
            logger.critical(f"Failed to initialize ChromaDB: {e}")
            raise

    def index(self, article: ProcessedArticle) -> None:
        if not article.embedding:
            logger.warning(
                f"Skipping index for article with no embedding: {article.title}"
            )
            return

        try:
            self.collection.upsert(
                ids=[article.url],
                embeddings=[article.embedding],
                metadatas=[
                    {
                        "category": article.category.value
                        if article.category
                        else "Other",
                        "title": article.title,
                        "uuid": str(article.id),
                    }
                ],
            )
            logger.debug(f"Indexed article in ChromaDB: {article.title}")
        except Exception as e:
            logger.error(f"Failed to index article '{article.title}' in ChromaDB: {e}")
            raise

    def search(self, query_embedding: List[float], limit: int = 10) -> List[str]:
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding], n_results=limit
            )
            # Flatten results
            ids = results["ids"][0] if results["ids"] else []
            logger.debug(f"ChromaDB search returned {len(ids)} results.")
            return ids
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {e}")
            return []
