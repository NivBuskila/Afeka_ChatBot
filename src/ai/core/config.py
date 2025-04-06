import os

# Environment Settings
DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true' # Use FLASK_DEBUG standard if possible
ENVIRONMENT = os.environ.get("FLASK_ENV", "development") # Use FLASK_ENV standard

# Service Settings
# Consider making rate limit more sophisticated if needed (e.g., using Flask-Limiter)
API_RATE_LIMIT = int(os.environ.get('AI_API_RATE_LIMIT', '60'))  # Requests per minute per IP (rename env var for clarity)
MAX_MESSAGE_LENGTH = int(os.environ.get('AI_MAX_MESSAGE_LENGTH', '2000'))  # Max length of input message (rename env var for clarity)

# Server Settings
PORT = int(os.environ.get('AI_PORT', 5000))
HOST = os.environ.get('AI_HOST', '0.0.0.0') 