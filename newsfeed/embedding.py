from abc import ABC, abstractmethod
from typing import List
from sentence_transformers import SentenceTransformer


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
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> List[float]:
        # The model returns a numpy array, we convert to list for storage/compat
        embedding = self.model.encode(text)
        return embedding.tolist()
