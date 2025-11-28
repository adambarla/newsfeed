## Development Setup

1. Install dependencies: `uv sync --group dev`
2. Configure Environment: `cp .env.example .env # Edit .env to set GEMINI_API_KEY if needed`
3. Install pre-commit hooks: `uv run pre-commit install`
4. Run tests:
    - All tests: `uv run pytest`
    - Unit tests only (fast): `uv run pytest -m "not integration"`
    - Integration tests (network calls): `uv run pytest -m integration -s`

**Note:** Pre-commit hooks and tests are automatically enforced on GitHub via CI/CD. All PRs must pass linting and tests before merging.

## Deployment & Running

### Option 1: Docker
Builds a self-contained environment with persistent storage. URL: `http://localhost:8000`. Data: Persisted in `./data` folder.
```bash
docker compose up --build -d
```

### Option 2: Local Development
Runs the app directly on your machine. URL: `http://localhost:8000`
```sh
uv run main.py
# or
uv run uvicorn newsfeed.app:app --reload
```

## API Usage

The API provides endpoints to retrieve and search for news articles.

- Interactive Documentation: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
- Health Check: `GET /health`
- List Articles: `GET /api/v1/articles?category=Cybersecurity&limit=10`
- Get Article: `GET /api/v1/articles/{id}`
