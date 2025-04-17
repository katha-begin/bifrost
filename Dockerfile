FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt setup.py ./
COPY README.md ./
COPY bifrost ./bifrost
COPY scripts ./scripts
COPY config ./config

# Create necessary directories
RUN mkdir -p /app/data

# Install the package and dependencies
RUN pip install --no-cache-dir -e .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV DATABASE_TYPE=sqlite
ENV DATABASE_PATH=/app/data/bifrost.db
ENV JWT_SECRET=your-secret-key-here
ENV BIFROST_ADMIN_USERNAME=admin
ENV BIFROST_ADMIN_EMAIL=admin@bifrost.local
ENV BIFROST_ADMIN_PASSWORD=changeme

# Create startup script that initializes DB and starts the API
RUN echo '#!/bin/bash\n\
python /app/scripts/init_db.py\n\
uvicorn bifrost.api.main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Start the application
CMD ["/app/start.sh"]