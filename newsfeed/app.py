from contextlib import asynccontextmanager
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException

from newsfeed.config import get_settings, Settings
from newsfeed.storage import SQLModelStore, NewsStore
from newsfeed.models import ProcessedArticle, NewsCategory


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the database
    settings = get_settings()
    store = SQLModelStore(settings.DATABASE_URL)
    await store.init_db()
    yield
    # clean up resources if needed (e.g. close connections)


app = FastAPI(title="Newsfeed API", lifespan=lifespan)


async def get_store(settings: Settings = Depends(get_settings)) -> NewsStore:
    # we might cache this or use a singleton
    return SQLModelStore(settings.DATABASE_URL)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/v1/articles/{article_id}", response_model=ProcessedArticle)
async def get_article(article_id: UUID, store: NewsStore = Depends(get_store)):
    article = await store.get_article(str(article_id))
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.get("/api/v1/articles", response_model=List[ProcessedArticle])
async def list_articles(
    category: Optional[NewsCategory] = None,
    limit: int = 20,
    offset: int = 0,
    store: NewsStore = Depends(get_store),
):
    """
    List articles with optional category filtering.
    """
    # convert enum to string for the store
    cat_str = category.value if category else None
    return await store.list_articles(category=cat_str, limit=limit, offset=offset)
