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

# Copy labels from build stage
COPY --from=build /app/Dockerfile /app/Dockerfile
LABEL maintainer="Afeka ChatBot Team"
LABEL version="1.0"
LABEL description="AI service for Afeka College Regulations ChatBot"

# Set working directory
WORKDIR /app/ai

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from build stage
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application files
COPY --chown=appuser:appuser . .

# Create models directory and set permissions
RUN mkdir -p /app/ai/models && \
    chown -R appuser:appuser /app/ai

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Expose AI service port
EXPOSE 5000

# Define health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/')" || exit 1

# Start application
CMD ["python", "app.py"] 