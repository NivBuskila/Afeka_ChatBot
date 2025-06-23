import { API_CONFIG } from '../config/constants';

// Get the backend URL from environment
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

// Helper function for API requests
const apiRequest = async (url: string, options: RequestInit = {}) => {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json();
};

export interface Message {
  id: string;
  type: "user" | "bot";
  content: string;
  timestamp: string;
  sessionId?: string;
}

/**
 * Service for automatic chat title generation
 */
export const titleGenerationService = {
  /**
   * Generates a customized title based on chat messages
   * @param messages List of chat messages
   * @param maxLength Maximum title length
   * @returns Generated title or null on error
   */
  generateTitle: async (messages: Message[], maxLength: number = 50): Promise<string | null> => {
    try {
      // Check if there are enough messages
      if (!messages || messages.length < 2) {
        return null;
      }

      // Prepare conversation content
      const conversationContent = messages
        .filter(msg => msg.content.trim().length > 0)
        .slice(0, 10) // Take only first 10 messages to save tokens
        .map(msg => `${msg.type === 'user' ? 'משתמש' : 'בוט'}: ${msg.content}`)
        .join('\n');

      if (!conversationContent.trim()) {
        return null;
      }

      // Create AI prompt
      const prompt = `
אנא צור כותרת קצרה ותמציתית בעברית לשיחה הבאה בין משתמש לבוט תמיכה של מכללת אפקה.

הנחיות:
- הכותרת צריכה להיות באורך של עד ${maxLength} תווים
- הכותרת צריכה לשקף את הנושא העיקרי של השיחה
- השתמש בעברית פשוטה וברורה
- אל תכלול מילים מיותרות כמו "שיחה על" או "שאלה על"
- התמקד בנושא המרכזי בלבד

תוכן השיחה:
${conversationContent}

צור כותרת מתאימה:`;

      // Send request to AI service
      const response = await apiRequest(`${BACKEND_URL}/api/generate-title`, {
        method: 'POST',
        body: JSON.stringify({ prompt }),
      });

      if (response && response.title) {
        const title = response.title.trim();
        // Trim title if needed
        return title.length > maxLength ? title.substring(0, maxLength - 3) + '...' : title;
      }

      return null;
    } catch (error) {
      return null;
    }
  },

  /**
   * Generates a simple title based on the first message
   * @param firstUserMessage First user message
   * @param maxLength Maximum title length
   * @returns Simple title
   */
  generateSimpleTitle: (firstUserMessage: string, maxLength: number = 50): string => {
    if (!firstUserMessage || firstUserMessage.trim().length === 0) {
      return `שיחה חדשה - ${new Date().toLocaleDateString('he-IL')}`;
    }

    const cleanMessage = firstUserMessage.trim();
    
    // Remove unnecessary words
    const wordsToRemove = ['אפשר', 'בבקשה', 'תוכל', 'תוכלי', 'אני רוצה', 'אני צריך', 'איך', 'מה'];
    let title = cleanMessage;
    
    wordsToRemove.forEach(word => {
      const regex = new RegExp(`\\b${word}\\b`, 'gi');
      title = title.replace(regex, '').trim();
    });

    // Clean extra spaces
    title = title.replace(/\s+/g, ' ').trim();

    // Trim if needed
    if (title.length > maxLength) {
      title = title.substring(0, maxLength - 3) + '...';
    }

    return title || `שיחה חדשה - ${new Date().toLocaleDateString('he-IL')}`;
  },

  /**
   * Checks if title should be updated
   * @param currentTitle Current title
   * @param messageCount Number of messages in chat
   * @returns Whether to update title
   */
  shouldUpdateTitle: (currentTitle: string | null, messageCount: number): boolean => {
    // Update title based on message count intervals
    if (messageCount <= 6) {
      return messageCount % 2 === 0; // Every 2 messages
    } else if (messageCount <= 12) {
      return messageCount % 3 === 0; // Every 3 messages
    } else {
      return messageCount % 5 === 0; // Every 5 messages
    }
  },

  /**
   * Checks if title is a default title
   * @param title Title to check
   * @returns Whether it's a default title
   */
  isDefaultTitle: (title: string | null): boolean => {
    if (!title) return true;
    
    const defaultPatterns = [
      /^Chat \d+/,
      /^שיחה חדשה/,
      /^New Chat/,
      /^\d{1,2}\/\d{1,2}\/\d{4}/,
      /^שיחה \d+/
    ];

    return defaultPatterns.some(pattern => pattern.test(title));
  }
};

export default titleGenerationService; 