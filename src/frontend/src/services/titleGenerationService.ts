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
 * שירות ליצירת כותרות אוטומטיות לשיחות
 */
export const titleGenerationService = {
  /**
   * יוצר כותרת מותאמת לשיחה בהתבסס על ההודעות
   * @param messages רשימת ההודעות בשיחה
   * @param maxLength אורך מקסימלי של הכותרת
   * @returns כותרת מותאמת או null במקרה של שגיאה
   */
  generateTitle: async (messages: Message[], maxLength: number = 50): Promise<string | null> => {
    try {
      // בדיקה שיש מספיק הודעות לתמצית
      if (!messages || messages.length < 2) {
        return null;
      }

      // הכנת תוכן השיחה לתמצית
      const conversationContent = messages
        .filter(msg => msg.content.trim().length > 0)
        .slice(0, 10) // לוקח רק 10 ההודעות הראשונות לחיסכון ב-tokens
        .map(msg => `${msg.type === 'user' ? 'משתמש' : 'בוט'}: ${msg.content}`)
        .join('\n');

      if (!conversationContent.trim()) {
        return null;
      }

      // יצירת prompt למודל AI
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

      // שליחת בקשה לשירות AI
      const response = await apiRequest(`${BACKEND_URL}/api/generate-title`, {
        method: 'POST',
        body: JSON.stringify({ prompt }),
      });

      if (response && response.title) {
        const title = response.title.trim();
        // חיתוך הכותרת למצב הנדרש
        return title.length > maxLength ? title.substring(0, maxLength - 3) + '...' : title;
      }

      return null;
    } catch (error) {
      console.error('Error generating title:', error);
      return null;
    }
  },

  /**
   * יוצר כותרת פשוטה בהתבסס על ההודעה הראשונה
   * @param firstUserMessage ההודעה הראשונה של המשתמש
   * @param maxLength אורך מקסימלי של הכותרת
   * @returns כותרת פשוטה
   */
  generateSimpleTitle: (firstUserMessage: string, maxLength: number = 50): string => {
    if (!firstUserMessage || firstUserMessage.trim().length === 0) {
      return `שיחה חדשה - ${new Date().toLocaleDateString('he-IL')}`;
    }

    const cleanMessage = firstUserMessage.trim();
    
    // ניקוי המילים המיותרות
    const wordsToRemove = ['אפשר', 'בבקשה', 'תוכל', 'תוכלי', 'אני רוצה', 'אני צריך', 'איך', 'מה'];
    let title = cleanMessage;
    
    wordsToRemove.forEach(word => {
      const regex = new RegExp(`\\b${word}\\b`, 'gi');
      title = title.replace(regex, '').trim();
    });

    // ניקוי רווחים מיותרים
    title = title.replace(/\s+/g, ' ').trim();

    // חיתוך למצב הנדרש
    if (title.length > maxLength) {
      title = title.substring(0, maxLength - 3) + '...';
    }

    return title || `שיחה חדשה - ${new Date().toLocaleDateString('he-IL')}`;
  },

  /**
   * בודק אם כדאי לעדכן את הכותרת
   * @param currentTitle הכותרת הנוכחית
   * @param messageCount מספר ההודעות הנוכחי בשיחה
   * @returns האם כדאי לעדכן את הכותרת
   */
  shouldUpdateTitle: (currentTitle: string | null, messageCount: number): boolean => {
    // עדכון כותרת כל 2-3 הודעות בהתחלה, ואחר כך כל 5-6 הודעות
    if (messageCount <= 6) {
      return messageCount % 2 === 0; // כל 2 הודעות
    } else if (messageCount <= 12) {
      return messageCount % 3 === 0; // כל 3 הודעות
    } else {
      return messageCount % 5 === 0; // כל 5 הודעות
    }
  },

  /**
   * בודק אם הכותרת הנוכחית היא כותרת ברירת מחדל
   * @param title הכותרת לבדיקה
   * @returns האם זו כותרת ברירת מחדל
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