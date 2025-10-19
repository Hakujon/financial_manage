# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Workdir
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml /app/
COPY src /app/src
COPY README.md /app/

# Install the `uv` package manager and use it to install project dependencies globally
RUN pip install --upgrade pip setuptools wheel \
    && pip install uv \
    && uv pip install --system || (echo "uv install failed, falling back to pip install ." && pip install .)

# Entrypoint: run bot with system python
CMD ["python", "-u", "-m", "src.main"]
