import React, { createContext, useState, useContext, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import i18n from 'i18next';

type Language = 'he' | 'en';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  toggleLanguage: () => void;
}

const LanguageContext = createContext<LanguageContextType>({
  language: 'en',
  setLanguage: () => {},
  toggleLanguage: () => {},
});

export const useLanguage = () => useContext(LanguageContext);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Get saved language or default to English
  const getSavedLanguage = (): Language => {
    // For now, always default to English to fix splash screen issue
    return 'en';
    
    // Original code:
    // const savedLanguage = localStorage.getItem('language');
    // return (savedLanguage === 'he' || savedLanguage === 'en') 
    //   ? savedLanguage as Language
    //   : 'en';
  };

  const [language, setLanguageState] = useState<Language>(getSavedLanguage());
  
  // Apply language to document and i18n
  useEffect(() => {
    console.log('LanguageProvider: Setting language to', language);
    
    // Apply document direction and language
    document.documentElement.lang = language;
    document.documentElement.dir = language === 'he' ? 'rtl' : 'ltr';
    
    // Change language in i18n
    i18n.changeLanguage(language)
      .then(() => console.log('i18n language changed successfully to', language))
      .catch(err => console.error('Error changing i18n language:', err));
    
    // Save language to localStorage
    localStorage.setItem('language', language);
  }, [language]);

  const setLanguage = (lang: Language) => {
    console.log('setLanguage called with:', lang);
    setLanguageState(lang);
  };

  const toggleLanguage = () => {
    console.log('toggleLanguage called, current language:', language);
    setLanguageState(prevLang => {
      const newLang = prevLang === 'en' ? 'he' : 'en';
      console.log('Switching language from', prevLang, 'to', newLang);
      return newLang;
    });
  };

  const contextValue = {
    language,
    setLanguage,
    toggleLanguage
  };

  console.log('LanguageProvider rendering with language:', language);

  return (
    <LanguageContext.Provider value={contextValue}>
      {children}
    </LanguageContext.Provider>
  );
};

export default LanguageProvider; 