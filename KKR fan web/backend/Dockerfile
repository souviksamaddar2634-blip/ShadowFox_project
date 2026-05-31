# Production Dockerfile placeholder for Render/production deployment
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies list
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application files
COPY . .

# Set execution environment settings
ENV ENVIRONMENT=production
EXPOSE 8000

# Run FastAPI using Uvicorn, dynamically respecting PORT environment variable
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
