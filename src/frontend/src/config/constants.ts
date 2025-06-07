export const CHAT_CONFIG = {
    MAX_MESSAGE_LENGTH: 1000,
    TYPING_INDICATOR_DELAY: 500,
    BOT_NAME: 'APEX',
    INITIAL_MESSAGE: 'ברוך הבא! איך אפשר לעזור?',
  } as const;

// Get the backend URL from environment
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const API_CONFIG = {
  CHAT_ENDPOINT: `${BACKEND_URL}/api/chat`,
  DOCUMENTS_ENDPOINT: `${BACKEND_URL}/api/documents`,
  HEALTH_ENDPOINT: `${BACKEND_URL}/api/health`,
  DEFAULT_TIMEOUT: 20000, // Increased to 20 seconds for RAG processing
} as const;