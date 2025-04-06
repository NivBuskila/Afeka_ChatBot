FROM python:3.9-slim AS build

# Add build labels
LABEL maintainer="Afeka ChatBot Team"
LABEL version="1.0"
LABEL description="AI service for Afeka College Regulations ChatBot"

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.9-slim

# Add labels directly to this stage
LABEL maintainer="Afeka ChatBot Team"
LABEL version="1.0"
LABEL description="AI service for Afeka College Regulations ChatBot"

# Set working directory
WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from build stage
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application files
COPY --chown=appuser:appuser src/ai /app/ai
COPY --chown=appuser:appuser requirements.txt /app/ai/requirements.txt

# Re-run pip install if requirements moved or WORKDIR changed context
# RUN pip install --no-cache-dir -r /app/ai/requirements.txt

# Create models directory and set permissions
RUN mkdir -p /app/ai/models && \
    chown -R appuser:appuser /app/ai

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Switch to non-root user
USER appuser

# Expose AI service port
EXPOSE 5000

# Define health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# Start application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "ai.app:create_app()"] 