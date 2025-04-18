import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpBackend from 'i18next-http-backend/cjs';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translations from files
import translationEN from './locales/en/translation.json';
import translationHE from './locales/he/translation.json';

// Resources for the languages
const resources = {
  en: {
    translation: translationEN,
  },
  he: {
    translation: translationHE,
  },
};

// Get saved language from localStorage or use browser detection
const savedLanguage = typeof window !== 'undefined' ? localStorage.getItem('i18nextLng') : null;
const defaultLanguage = savedLanguage || 'he';

// Initialize i18next
i18n
  .use(HttpBackend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    lng: defaultLanguage,
    fallbackLng: 'he',
    debug: false,
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['localStorage', 'navigator'],
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage'],
    },
    react: {
      useSuspense: false,
    },
  });

// Function to change the language
export const changeLanguage = (language: string) => {
  i18n.changeLanguage(language);
  if (typeof window !== 'undefined') {
    localStorage.setItem('i18nextLng', language);
    // Update document direction based on language
    document.documentElement.dir = language === 'he' ? 'rtl' : 'ltr';
    document.documentElement.lang = language;
  }
};

// Set initial document direction
if (typeof window !== 'undefined') {
  document.documentElement.dir = defaultLanguage === 'he' ? 'rtl' : 'ltr';
  document.documentElement.lang = defaultLanguage;
}

export default i18n;
