# ──────────────────────────────────────────────
# Flask API - Dockerfile
# Multi-stage build for production deployment
# ──────────────────────────────────────────────

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (Docker cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose API port
EXPOSE 5000

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" || exit 1

# Run with Gunicorn (production WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
