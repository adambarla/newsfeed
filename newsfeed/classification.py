import os
from abc import ABC, abstractmethod
from typing import Optional

import google.generativeai as genai
from newsfeed.models import NewsCategory


class NewsClassifier(ABC):
    """Abstract base class for news classifiers."""

    @abstractmethod
    async def classify(self, text: str) -> NewsCategory:
        """Classifies the given text into a NewsCategory."""
        pass


class GeminiNewsClassifier(NewsClassifier):
    """
    Classifier implementation using Google's Gemini Flash model.
    Requires GOOGLE_API_KEY environment variable.
    """

    def __init__(
        self, api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash"
    ):
        key = api_key

        # Try to get from settings if not provided
        if not key:
            from newsfeed.config import get_settings

            settings = get_settings()
            if settings.GEMINI_API_KEY:
                key = settings.GEMINI_API_KEY.get_secret_value()

        # Fallback to raw env var if needed (e.g. for simple scripts)
        if not key:
            key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

        if not key:
            raise ValueError("GEMINI_API_KEY is required for GeminiNewsClassifier")

        genai.configure(api_key=key)
        self.model = genai.GenerativeModel(model_name)

        # Construct the prompt with valid categories
        self.valid_categories = [c.value for c in NewsCategory]
        self.prompt_template = (
            "You are a tech news classifier. Classify the following news article text "
            "into exactly one of these categories: {categories}.\n"
            "Return ONLY the category name, nothing else.\n\n"
            "Article Text:\n{text}"
        )

    async def classify(self, text: str) -> NewsCategory:
        # Truncate text if too long to save tokens/avoid limits
        truncated_text = text[:10000]

        prompt = self.prompt_template.format(
            categories=", ".join(self.valid_categories), text=truncated_text
        )

        try:
            # Generate content asynchronously
            response = await self.model.generate_content_async(prompt)
            result = response.text.strip()

            # Map string back to Enum
            # We iterate to match case-insensitively or exact match
            for category in NewsCategory:
                if category.value.lower() == result.lower():
                    return category

            # Fallback for unexpected LLM output
            return NewsCategory.OTHER

        except Exception as e:
            # Log error in production (using print for now as per simple setup)
            # retry?
            print(f"Classification error: {e}")
            return NewsCategory.OTHER
