# Development Report: Newsfeed Fetchers

## Fetching

I implemented the ingestion layer to fetch data from external sources. This involved defining a `RawArticle` data model and a `NewsFetcher` abstract base class to ensure a consistent interface. I then built two concrete implementations: `RSSFetcher` for general RSS feeds and `RedditFetcher` for Reddit-specific endpoints, both using `httpx` for async requests and `feedparser` for XML parsing.

To ensure code quality and maintainability, I refactored shared logic for date parsing and content extraction into the base class, eliminating duplication. I also enriched the data model to capture `tags` and `image_url` from feeds, providing richer metadata for downstream processing. Additionally, I implemented HTML cleaning using `BeautifulSoup` to ensure the `content` field contains clean, readable text rather than raw markup, reducing noise for the classifier.

I established a comprehensive testing strategy that includes fast, mocked unit tests for logic verification and slower integration tests that make real network calls to ensure the system works with live sources.
Verified sources include:
- **NYTimes Technology**
- **Ars Technica**
- **Tom's Hardware**
- **Reddit (r/programming)**

I have verified that the fetchers successfully capture full content from Reddit and summaries from standard news feeds, with tags and images correctly extracted and HTML cleaned. The system also robustly handles HTTP redirects (required for some feeds like Tom's Hardware).

## Storage & API

I implemented the persistent storage layer and the public API to serve the processed news.

For storage, I chose a **Modular Monolith** approach using **SQLite** with `SQLModel`. This provides the reliability of a relational database without the operational overhead of a separate server. I defined a `ProcessedArticle` model that stores the core article data along with metadata like categories and source information. I abstracted the database operations behind a `NewsStore` interface, allowing for easy swapping of storage backends (e.g., for testing) and implemented an asynchronous `SQLModelStore`.

For the API, I built a **FastAPI** application that exposes endpoints to retrieve articles by ID and list them with category filtering. I refactored the project structure to follow Python packaging best practices, moving the core application logic into the `newsfeed` package while keeping a lightweight entry point at the root.

To ensure deployability, I containerized the application using **Docker**. The setup includes a multi-stage build using `uv` for efficient dependency management and configures a persistent volume to ensure data survives container restarts.

I verified this layer with unit tests for the storage logic and integration tests for the API endpoints. I also validated the full deployment flow by building and running the Docker container locally, confirming that the service starts correctly and the persistence layer is active.

## Future Work

While the current implementation provides a solid foundation, there are several areas I plan to address next. I need to add proper logging and retry logic to handle network instability robustly. I also plan to implement the classifier and storage components to complete the ingestion pipeline.

I will continue to refine the error handling and add more comprehensive tests as we encounter edge cases during further development.
