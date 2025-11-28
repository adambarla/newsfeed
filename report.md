# Development Report: Newsfeed System

## Fetching

I implemented the ingestion layer to fetch data from external sources. This involved defining a `RawArticle` data model and a `NewsFetcher` abstract base class to ensure a consistent interface. I then built two concrete implementations: `RSSFetcher` for general RSS feeds and `RedditFetcher` for Reddit-specific endpoints, both using `httpx` for async requests and `feedparser` for XML parsing.

To ensure code quality and maintainability, I refactored shared logic for date parsing and content extraction into the base class, eliminating duplication. I also enriched the data model to capture `tags` and `image_url` from feeds, providing richer metadata for downstream processing. Additionally, I implemented HTML cleaning using `BeautifulSoup` to ensure the `content` field contains clean, readable text rather than raw markup.

I verified sources include:
- **NYTimes Technology**
- **Ars Technica**
- **Tom's Hardware**
- **Reddit (r/programming)**

## Storage & API

I chose a **Modular Monolith** approach using **SQLite** with `SQLModel`. This provides the reliability of a relational database without the operational overhead of a separate server. I defined a `ProcessedArticle` model that stores the core article data along with metadata like categories and source information.

To support semantic search, I implemented a split architecture:
1.  Repository Layer: `SQLArticleRepository` manages persistent storage of article metadata.
2.  Vector Index: `ChromaVectorIndex` manages embeddings for similarity search.
3.  Service Layer: `NewsService` orchestrates the two, handling the logic to save to both stores and merge search results.

I built a **FastAPI** application that exposes endpoints to retrieve articles by ID and list them with category filtering. I containerized the application using **Docker**, ensuring a consistent environment with persistent volumes for data.

## Classification & Search

I implemented the classification layer using **Google's Gemini 2.0 Flash** model via the `GeminiNewsClassifier`. This component takes article text and categorizes it into one of the predefined categories (e.g., Cybersecurity, AI & Emerging Tech).

I exposed a new `/api/v1/articles/search` endpoint that enables **semantic search**. This allows users to find relevant articles using natural language queries rather than just keyword matching.

## Scheduler & Observability

I implemented the **Scheduler** using `APScheduler` to automate the ingestion pipeline. It is configured to run every 15 minutes and also triggers an immediate run on application startup to ensure data is available instantly.

To ensure the system is production-ready, I:
1.  **Optimized Resources**: Implemented the **Singleton Pattern** (via `@lru_cache`) for heavy dependencies like the Database connection, Embedding Model, and Classifier. This prevents memory bloat and speeds up startup.
2.  **Improved Logging**: Configured structured `INFO` level logging to provide visibility into the background scheduler's activity directly in the Docker logs.
3.  **Data Quality**: Refined the `RedditFetcher` to detect and handle generic "submitted by" boilerplate text, ensuring that embeddings are generated from meaningful titles.
4.  **API Performance**: Created a dedicated `ArticleResponse` model to exclude large embedding vectors from the API output, reducing the payload size by over 90%.

## Future Work

I plan to improve the system's robustness and feature set in the following areas:

1.  **Observability**: Transition to a more advanced logging solution (e.g., `structlog`) to enable JSON logging, making it easier to ingest logs into monitoring stacks like ELK or Datadog.
2.  **API Enhancements**: Add support for advanced filtering, such as date ranges (`start_date`, `end_date`), source filtering, and full-text search alongside semantic search.
3.  **Resilience**: Implement robust error handling with retry logic (exponential backoff) for external network calls to handle transient failures gracefully.
4.  **Scraping**: Integrate a headless browser (like Playwright) to follow Reddit links and scrape the *actual* destination content, providing richer context for the classifier.
