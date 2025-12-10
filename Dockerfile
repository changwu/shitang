FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./
COPY sql/ ./sql/

# Create data directory
RUN mkdir -p /app/data/import

# Set environment variables
ENV PYTHONPATH=/app
ENV DATA_DIR=/app/data
ENV IMPORT_DIR=import/

# Default command
# CMD ["python", "-u", "import_data.py", "--verbose"]