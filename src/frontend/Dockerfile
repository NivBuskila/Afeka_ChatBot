FROM node:20.10-alpine AS build

# Add build label
LABEL maintainer="Afeka ChatBot Team"
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Use non-root user for security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN chown -R appuser:appgroup /app
USER appuser

# Install dependencies first (leverages Docker cache)
COPY --chown=appuser:appgroup package.json package-lock.json* ./
RUN npm ci --silent || npm install --legacy-peer-deps 

# Copy application source
COPY --chown=appuser:appgroup . .

# Build the application for production
RUN npm run build

# Production stage - uses multi-stage build for smaller image
FROM nginx:1.25-alpine AS production

# Add content labels
LABEL maintainer="Afeka ChatBot Team"
LABEL version="1.0"
LABEL description="Frontend service for Afeka College Regulations ChatBot"

# Security: Run as non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf

# Set permissions
RUN chown -R appuser:appgroup /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html && \
    chown -R appuser:appgroup /var/cache/nginx && \
    chown -R appuser:appgroup /var/log/nginx && \
    chown -R appuser:appgroup /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R appuser:appgroup /var/run/nginx.pid

# Use non-root user
USER appuser

# Expose port
EXPOSE 80

# Define health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]