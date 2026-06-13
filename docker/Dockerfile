FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for compiling certain packages or postgres connection
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
# If requirements.txt is UTF-16LE, we can convert it or install requirements directly
# To be robust, we'll install requirements directly as well
RUN pip install --no-cache-dir requests pandas sqlalchemy psycopg2-binary python-dotenv pytest

# Copy application source
COPY src/ /app/src/
COPY sql/ /app/sql/

# Set Python path
ENV PYTHONPATH=/app/src

CMD ["python", "src/main.py"]
