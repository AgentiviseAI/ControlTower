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
COPY . .

# Environment variables (production defaults)
ENV ENVIRONMENT=prod
ENV DEBUG=false
ENV HOST=0.0.0.0
ENV PORT=8000
ENV RELOAD=false

# Database settings
ENV DATABASE_TYPE=postgres
ENV DATABASE_URL=""
ENV POSTGRES_HOST=""
ENV POSTGRES_PORT=5432
ENV POSTGRES_USER=""
ENV POSTGRES_PASSWORD=""
ENV POSTGRES_DB=ai_platform

# Security settings
ENV SECRET_KEY=""
ENV JWT_SECRET_KEY=""
ENV JWT_ALGORITHM=HS256
ENV JWT_EXPIRATION_HOURS=24

# CORS settings
ENV CORS_ORIGINS=""
ENV CORS_CREDENTIALS=true
ENV CORS_METHODS="GET,POST,PUT,DELETE,OPTIONS"
ENV CORS_HEADERS="*"

# Auth Service Configuration
ENV AUTH_SERVICE_URL=""

# External services
ENV OPENAI_API_KEY=""
ENV ANTHROPIC_API_KEY=""
ENV AZURE_OPENAI_ENDPOINT=""
ENV AZURE_OPENAI_API_KEY=""

# Logging
ENV LOG_LEVEL=INFO
ENV LOG_FORMAT=json

# Monitoring
ENV ENABLE_METRICS=true
ENV METRICS_PORT=9090

# Expose port
EXPOSE 8000

# Run the application with database initialization
CMD ["sh", "-c", "python startup.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
