export const CHAT_CONFIG = {
    MAX_MESSAGE_LENGTH: 1000,
    TYPING_INDICATOR_DELAY: 500,
    BOT_NAME: 'APEX',
    INITIAL_MESSAGE: 'ברוך הבא! איך אפשר לעזור?',
  } as const;

export const API_CONFIG = {
  // הגדרות API 
  API_URL: 'http://localhost:8000', // כתובת שרת ה-backend
  CHAT_ENDPOINT: '/api/chat', // שימוש ב-API המקומי במקום לפנות ישירות ל-Gemini
  DOCUMENTS_ENDPOINT: '/api/documents',
  HEALTH_ENDPOINT: '/api/health',
  DEFAULT_TIMEOUT: 30000, // 30 seconds timeout
  RETRY_COUNT: 3,
  MODEL_MAX_TOKENS: 8192,
  MAX_RETRIES: 2,
  RETRY_DELAY: 1000, // 1 second
} as const;