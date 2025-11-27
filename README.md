## Development Setup

1. Install dependencies: `uv sync --group dev`
2. Install pre-commit hooks: `uv run pre-commit install`
3. Run tests: `uv run pytest`

**Note:** Pre-commit hooks and tests are automatically enforced on GitHub via CI/CD. All PRs must pass linting and tests before merging.
