# Newsfeed Aggregator

A real-time, intelligent news aggregation system that collects IT news, classifies it using LLMs (Gemini), and provides a semantic search API.

## Features

The system fetches news from RSS feeds (Ars Technica, Tom's Hardware) and Reddit. It automatically categorizes articles using Google Gemini 2.0 and enables natural language search via local embeddings and ChromaDB. Background jobs ensure data is updated every 15 minutes.

## Architecture

The system uses a Modular Monolith design:

1.  **Ingestion**: `APScheduler` triggers fetchers to pull raw data.
2.  **Processing**:
    *   Deduplicates URLs.
    *   Classifies content using LLMs.
    *   Generates vector embeddings.
3.  **Storage**: SQLite stores metadata; ChromaDB stores vectors.
4.  **Serving**: FastAPI exposes endpoints for search and retrieval.

## Development Setup

1.  Install dependencies: `uv sync --group dev`
2.  Configure environment: `cp .env.example .env` (Set `GEMINI_API_KEY`)
3.  Run tests: `uv run pytest`

## Deployment & Running

### Option 1: Docker (Recommended)
Builds a self-contained environment with persistent storage.

```bash
docker compose up --build -d
```

The API is available at [http://localhost:8000/docs](http://localhost:8000/docs). The ingestion job runs immediately on startup.

### Option 2: Local Development
```bash
uv run main.py
```

## API Usage

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/articles/search?query=...` | Semantic search for conceptually similar articles. |
| `GET` | `/api/v1/articles?category=...` | List articles with optional filtering. |
| `GET` | `/api/v1/articles/{id}` | Retrieve full article details. |
| `GET` | `/health` | System health check. |
