FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including cron
RUN apt-get update && apt-get install -y \
    gcc \
    cron \
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

# Copy cron script and make it executable
COPY daily_stats_cron.sh /app/daily_stats_cron.sh
RUN chmod +x /app/daily_stats_cron.sh

# Create cron job for daily stats at 9:10 AM
RUN echo "10 9 * * * /app/daily_stats_cron.sh >> /var/log/cron.log 2>&1" | crontab -

# Create log directory
RUN mkdir -p /var/log

# Create startup script
RUN echo '#!/bin/bash\n\
# Start cron service\n\
service cron start\n\
# Keep container running\n\
tail -f /dev/null' > /app/start.sh && chmod +x /app/start.sh

# Default command - start cron and keep container running
CMD ["/app/start.sh"]