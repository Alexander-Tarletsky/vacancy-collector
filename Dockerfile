FROM python:3.13-slim

# Set environment variables
ENV POETRY_VERSION=2.0.1 \
    PYTHONUNBUFFERED=1 \
    WAIT_VERSION=2.12.0

# Install dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && curl -sSLo /wait https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait \
    && chmod +x /wait

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock ./

# Install project dependencies
RUN poetry install --no-root --no-dev

# Copy application source
COPY app ./app

# Expose FastAPI port
EXPOSE 8000

# Start the application with wait-for-postgres
CMD ["/wait", "--timeout=30", "--", "poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
