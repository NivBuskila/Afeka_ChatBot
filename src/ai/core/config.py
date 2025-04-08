import os
from dotenv import load_dotenv

# טען את משתני הסביבה מתוך קובץ .env אם קיים
load_dotenv()

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

# Google Gemini API Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyB0D4QL-SIoR8LR4WkVRjxUV_HyIUQBdCU')
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-pro')
GEMINI_TEMPERATURE = float(os.environ.get('GEMINI_TEMPERATURE', '0.7'))
GEMINI_MAX_OUTPUT_TOKENS = int(os.environ.get('GEMINI_MAX_OUTPUT_TOKENS', '1024')) 