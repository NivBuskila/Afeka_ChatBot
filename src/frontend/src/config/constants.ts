export const CHAT_CONFIG = {
    MAX_MESSAGE_LENGTH: 1000,
    TYPING_INDICATOR_DELAY: 500,
    BOT_NAME: 'APEX',
    INITIAL_MESSAGE: 'ברוך הבא! איך אפשר לעזור?',
  } as const;

export const API_CONFIG = {
  // Route through backend proxy endpoints (port 8000)
  CHAT_ENDPOINT: 'http://localhost:8000/api/proxy/ai/chat',
  SEARCH_ENDPOINT: 'http://localhost:8000/api/proxy/ai/search',
  HYBRID_SEARCH_ENDPOINT: 'http://localhost:8000/api/proxy/ai/search/hybrid',
  ENHANCED_SEARCH_ENDPOINT: 'http://localhost:8000/api/proxy/ai/search/enhanced',
  DOCUMENTS_ENDPOINT: 'http://localhost:8000/api/proxy/documents',
  HEALTH_ENDPOINT: 'http://localhost:8000/api/proxy/ai/health',
  RAG_STATS_ENDPOINT: 'http://localhost:8000/api/proxy/ai/stats',
  DEFAULT_TIMEOUT: 30000,
} as const;