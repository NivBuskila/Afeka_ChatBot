import React, { createContext, useState, useContext, useEffect } from 'react';
import i18n from 'i18next';

type Language = 'he' | 'en';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  toggleLanguage: () => void;
  isRTL: boolean;
  direction: 'rtl' | 'ltr';
}

const LanguageContext = createContext<LanguageContextType>({
  language: 'en',
  setLanguage: () => {},
  toggleLanguage: () => {},
  isRTL: false,
  direction: 'ltr',
});

export const useLanguage = () => useContext(LanguageContext);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Get saved language or default to English
  const getSavedLanguage = (): Language => {
    const savedLanguage = localStorage.getItem('language');
    return (savedLanguage === 'he' || savedLanguage === 'en') 
      ? savedLanguage as Language
      : 'en';
  };

  const [language, setLanguageState] = useState<Language>(getSavedLanguage());
  
  // Apply language to document and i18n
  useEffect(() => {
    // Apply document direction and language
    document.documentElement.lang = language;
    document.documentElement.dir = language === 'he' ? 'rtl' : 'ltr';
    
    // Change language in i18n
    i18n.changeLanguage(language)
      .catch(err => console.error('Error changing i18n language:', err));
    
    // Save language to localStorage
    localStorage.setItem('language', language);
  }, [language]);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
  };

  const toggleLanguage = () => {
    setLanguageState(prevLang => {
      const newLang = prevLang === 'en' ? 'he' : 'en';
      return newLang;
    });
  };

  // RTL support
  const isRTL = language === 'he';
  const direction: 'rtl' | 'ltr' = isRTL ? 'rtl' : 'ltr';

  const contextValue: LanguageContextType = {
    language,
    setLanguage,
    toggleLanguage,
    isRTL,
    direction
  };

  return (
    <LanguageContext.Provider value={contextValue}>
      {children}
    </LanguageContext.Provider>
  );
};

export default LanguageProvider; 