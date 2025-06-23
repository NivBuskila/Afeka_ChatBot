import { useTranslation } from 'react-i18next';
import { changeLanguage } from '../../../i18n/config';

export function useLanguageToggle() {
  const { i18n } = useTranslation();

  const toggleLanguage = () => {
    const newLang = i18n.language === 'he' ? 'en' : 'he';
    changeLanguage(newLang);
  };

  return {
    currentLanguage: i18n.language,
    toggleLanguage,
  };
} 