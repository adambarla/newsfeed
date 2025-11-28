from contextlib import asynccontextmanager
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException

from newsfeed.dependencies import get_repository, get_news_service
from newsfeed.models import NewsCategory, ArticleResponse
from newsfeed.scheduler import start_scheduler
from newsfeed.services.news_service import NewsService
from newsfeed.storage import ArticleRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the database and scheduler
    repo = get_repository()
    await repo.init_db()

    scheduler = start_scheduler()

    yield

    # Shutdown: clean up resources
    scheduler.shutdown()


app = FastAPI(title="Newsfeed API", lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/v1/articles/search", response_model=List[ArticleResponse])
async def search_articles(
    query: str,
    limit: int = 20,
    service: NewsService = Depends(get_news_service),
):
    """
    Semantic search for articles.
    """
    return await service.search_articles(query, limit)


@app.get("/api/v1/articles/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: UUID, repo: ArticleRepository = Depends(get_repository)
):
    article = await repo.get(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.get("/api/v1/articles", response_model=List[ArticleResponse])
async def list_articles(
    category: Optional[NewsCategory] = None,
    limit: int = 20,
    offset: int = 0,
    repo: ArticleRepository = Depends(get_repository),
):
    """
    List articles with optional category filtering.
    """
    cat_str = category.value if category else None
    return await repo.list_articles(category=cat_str, limit=limit, offset=offset)
