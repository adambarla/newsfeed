from contextlib import asynccontextmanager
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException

from newsfeed.config import get_settings, Settings
from newsfeed.storage import SQLArticleRepository, ChromaVectorIndex, ArticleRepository
from newsfeed.services.news_service import NewsService
from newsfeed.models import ProcessedArticle, NewsCategory


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the database
    settings = get_settings()
    repo = SQLArticleRepository(settings.DATABASE_URL)
    await repo.init_db()
    yield
    # clean up resources if needed


app = FastAPI(title="Newsfeed API", lifespan=lifespan)


async def get_service(settings: Settings = Depends(get_settings)) -> NewsService:
    # In production, use singletons/DI container
    repo = SQLArticleRepository(settings.DATABASE_URL)
    index = ChromaVectorIndex(settings.CHROMADB_PATH)
    return NewsService(repo, index)


async def get_repo(settings: Settings = Depends(get_settings)) -> ArticleRepository:
    return SQLArticleRepository(settings.DATABASE_URL)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/v1/articles/{article_id}", response_model=ProcessedArticle)
async def get_article(article_id: UUID, repo: ArticleRepository = Depends(get_repo)):
    article = await repo.get(str(article_id))
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.get("/api/v1/articles", response_model=List[ProcessedArticle])
async def list_articles(
    category: Optional[NewsCategory] = None,
    limit: int = 20,
    offset: int = 0,
    repo: ArticleRepository = Depends(get_repo),
):
    """
    List articles with optional category filtering.
    """
    cat_str = category.value if category else None
    return await repo.list_articles(category=cat_str, limit=limit, offset=offset)
