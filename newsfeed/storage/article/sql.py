from typing import List, Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from newsfeed.models import ProcessedArticle
from newsfeed.storage.article.base import ArticleRepository


class SQLArticleRepository(ArticleRepository):
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

    async def save(self, article: ProcessedArticle) -> ProcessedArticle:
        async with self.async_session() as session:
            session.add(article)
            await session.commit()
            await session.refresh(article)
            return article

    async def exists(self, url: str) -> bool:
        async with self.async_session() as session:
            statement = select(ProcessedArticle).where(ProcessedArticle.url == url)
            result = await session.execute(statement)
            return result.scalars().first() is not None

    async def get(self, article_id: str) -> Optional[ProcessedArticle]:
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

    async def get_by_urls(self, urls: List[str]) -> List[ProcessedArticle]:
        if not urls:
            return []
        async with self.async_session() as session:
            statement = select(ProcessedArticle).where(ProcessedArticle.url.in_(urls))
            result = await session.execute(statement)
            return list(result.scalars().all())
