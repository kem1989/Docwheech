FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install system dependencies (Alpine uses apk instead of apt)
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    postgresql-dev \
    curl \
    file \
    libmagic \
    qpdf-dev \
    && rm -rf /var/cache/apk/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads logs

# Set permissions
RUN chmod -R 755 uploads logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
