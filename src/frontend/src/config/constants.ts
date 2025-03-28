export const CHAT_CONFIG = {
    MAX_MESSAGE_LENGTH: 1000,
    TYPING_INDICATOR_DELAY: 500,
    BOT_NAME: 'APEX',
    INITIAL_MESSAGE: 'ברוך הבא! איך אפשר לעזור?',
  } as const;

export const API_CONFIG = {
  CHAT_ENDPOINT: '/api/chat',
  DOCUMENTS_ENDPOINT: '/api/documents',
  HEALTH_ENDPOINT: '/api/health',
  DEFAULT_TIMEOUT: 5000,
} as const;