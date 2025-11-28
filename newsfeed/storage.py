from abc import ABC, abstractmethod
from typing import List, Optional

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from newsfeed.models import ProcessedArticle


class NewsStore(ABC):
    @abstractmethod
    async def save_article(self, article: ProcessedArticle) -> ProcessedArticle:
        """Saves an article to storage."""
        pass

    @abstractmethod
    async def article_exists(self, url: str) -> bool:
        """Checks if an article with the given URL already exists."""
        pass

    @abstractmethod
    async def get_article(self, article_id: str) -> Optional[ProcessedArticle]:
        """Retrieves an article by ID."""
        pass

    @abstractmethod
    async def list_articles(
        self, category: Optional[str] = None, limit: int = 20, offset: int = 0
    ) -> List[ProcessedArticle]:
        """Lists articles with optional filtering."""
        pass


class SQLModelStore(NewsStore):
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self):
        """Initializes the database tables."""
        from sqlmodel import SQLModel

        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def save_article(self, article: ProcessedArticle) -> ProcessedArticle:
        async with self.async_session() as session:
            session.add(article)
            await session.commit()
            await session.refresh(article)
            return article

    async def article_exists(self, url: str) -> bool:
        async with self.async_session() as session:
            statement = select(ProcessedArticle).where(ProcessedArticle.url == url)
            result = await session.execute(statement)
            return result.scalars().first() is not None

    async def get_article(self, article_id: str) -> Optional[ProcessedArticle]:
        async with self.async_session() as session:
            return await session.get(ProcessedArticle, article_id)

    async def list_articles(
        self, category: Optional[str] = None, limit: int = 20, offset: int = 0
    ) -> List[ProcessedArticle]:
        async with self.async_session() as session:
            statement = select(ProcessedArticle)
            if category:
                statement = statement.where(ProcessedArticle.category == category)
            statement = statement.offset(offset).limit(limit)
            statement = statement.order_by(ProcessedArticle.published_at.desc())

            result = await session.execute(statement)
            return list(result.scalars().all())
