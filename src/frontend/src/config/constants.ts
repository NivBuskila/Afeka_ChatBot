export const CHAT_CONFIG = {
    MAX_MESSAGE_LENGTH: 1000,
    TYPING_INDICATOR_DELAY: 500,
    BOT_NAME: 'APEX',
    INITIAL_MESSAGE: 'ברוך הבא! איך אפשר לעזור?',
  } as const;

export const API_CONFIG = {
  CHAT_ENDPOINT: 'http://localhost:5000/api/chat',
  DOCUMENTS_ENDPOINT: 'http://localhost:5000/api/documents',
  HEALTH_ENDPOINT: 'http://localhost:5000/api/health',
  DEFAULT_TIMEOUT: 30000,
} as const;