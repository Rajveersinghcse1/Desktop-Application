# AI Avatar Studio - Docker Configuration (Optimized)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libglib2.0-0 \
    libsndfile1 \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy and install dependencies
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/database \
    /app/data/cache \
    /app/data/logs \
    /app/models \
    /app/output/videos \
    /app/output/thumbnails

# Set permissions
RUN chmod +x docker-entrypoint.py

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DATABASE_PATH=/app/data/database/projects.db \
    MODELS_PATH=/app/models \
    OUTPUT_PATH=/app/output \
    CACHE_PATH=/app/data/cache

# Expose port
EXPOSE 8080

# Volume mount points
VOLUME ["/app/data", "/app/models", "/app/output"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sqlite3; conn = sqlite3.connect('/app/data/database/projects.db'); conn.close()" || exit 1

# Run the application
CMD ["python", "docker-entrypoint.py"]
