## Development Setup

1. Install dependencies: `uv sync --group dev`
2. Configure Environment: `cp .env.example .env # Edit .env to set GEMINI_API_KEY if needed`
3. Install pre-commit hooks: `uv run pre-commit install`
4. Run tests:
    - All tests: `uv run pytest`
    - Unit tests only (fast): `uv run pytest -m "not integration"`
    - Integration tests (network calls): `uv run pytest -m integration -s`

**Note:** Pre-commit hooks and tests are automatically enforced on GitHub via CI/CD. All PRs must pass linting and tests before merging.
