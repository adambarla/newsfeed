from abc import ABC, abstractmethod
import logging
from typing import List
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class NewsEmbedder(ABC):
    """
    Abstract Base Class for generating text embeddings.
    """

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Generates a vector embedding for the given text."""
        pass


class SentenceTransformerEmbedder(NewsEmbedder):
    """
    Concrete implementation using local SentenceTransformer models.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # This will download the model on first use (approx 80MB)
        logger.info(f"Loading SentenceTransformer model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            logger.debug("SentenceTransformer model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model: {e}")
            raise

    def embed(self, text: str) -> List[float]:
        # The model returns a numpy array, we convert to list for storage/compat
        try:
            embedding = self.model.encode(text, show_progress_bar=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
