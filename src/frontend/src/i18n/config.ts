import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import Hebrew translations directly
const heTranslation = {
  "chat": {
    "sidebar": {
      "chat": "צ'אט",
      "history": "היסטוריה",
      "settings": "הגדרות"
    },
    "history": {
      "title": "היסטוריית שיחות",
      "search": "חיפוש שיחות",
      "newChat": "שיחה חדשה",
      "untitled": "שיחה ללא כותרת",
      "noChats": "לא נמצאו שיחות. התחל שיחה חדשה!",
      "noResults": "לא נמצאו תוצאות לחיפוש שלך",
      "clearSearch": "נקה חיפוש",
      "edit": "ערוך כותרת",
      "delete": "מחק שיחה",
      "confirmDelete": "למחוק שיחה?",
      "confirmDeleteMessage": "פעולה זו אינה ניתנת לביטול. כל ההודעות בשיחה זו יימחקו לצמיתות."
    },
    "welcomeMessage": "ברוכים הבאים ל-APEX - חווית הנדסה מקצועית של אפקה. איך אוכל לעזור לך?",
    "startPrompt": "במה אני יכול לעזור?",
    "untitledChat": "שיחה ללא כותרת",
    "newChat": "שיחה חדשה",
    "processing": "מעבד...",
    "inputPlaceholder": "הקלד את ההודעה שלך כאן...",
    "messageInput": "קלט הודעה"
  },
  "common": {
    "update": "עדכון",
    "cancel": "ביטול",
    "logout": "התנתק",
    "save": "שמור",
    "delete": "מחק",
    "edit": "ערוך"
  }
};

// Import English translations directly
const enTranslation = {
  "chat": {
    "sidebar": {
      "chat": "Chat",
      "history": "History",
      "settings": "Settings"
    },
    "history": {
      "title": "Chat History",
      "search": "Search Chats",
      "newChat": "New Chat",
      "untitled": "Untitled Chat",
      "noChats": "No chats found. Start a new chat!",
      "noResults": "No results found for your search",
      "clearSearch": "Clear Search",
      "edit": "Edit Title",
      "delete": "Delete Chat",
      "confirmDelete": "Delete Chat?",
      "confirmDeleteMessage": "This action cannot be undone. All messages in this chat will be permanently deleted."
    },
    "welcomeMessage": "Welcome to APEX - Afeka Professional Engineering eXperience. How can I help you?",
    "startPrompt": "How can I help you?",
    "untitledChat": "Untitled Chat",
    "newChat": "New Chat",
    "processing": "Processing...",
    "inputPlaceholder": "Type your message here...",
    "messageInput": "Message Input"
  },
  "common": {
    "update": "Update",
    "cancel": "Cancel",
    "logout": "Logout",
    "save": "Save",
    "delete": "Delete",
    "edit": "Edit"
  }
};

// Setup resources with translations defined directly in this file
const resources = {
  he: {
    translation: heTranslation
  },
  en: {
    translation: enTranslation
  }
};

// Initialize i18next
i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: document.documentElement.lang === 'he' ? 'he' : 'en', // Use document language if specified, otherwise default to en
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    },
    returnNull: false,     // Return key instead of null for missing translations
    returnEmptyString: false, // Return key instead of empty string
    debug: false
  });

export const changeLanguage = (lang: 'he' | 'en') => {
  i18n.changeLanguage(lang);
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === 'he' ? 'rtl' : 'ltr';
};

export default i18n;
