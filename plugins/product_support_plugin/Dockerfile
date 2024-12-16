FROM python:3.11-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY . .
RUN uv venv
RUN uv sync --frozen
# Run the application
CMD ["uv", "run", "product-support-telegram"]
