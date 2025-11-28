FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . .

RUN mkdir -p /app/data

# Set environment variables to point to the data directory
ENV DATABASE_URL="sqlite+aiosqlite:////app/data/newsfeed.db"
ENV CHROMADB_PATH="/app/data/chroma"

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "newsfeed.app:app", "--host", "0.0.0.0", "--port", "8000"]
