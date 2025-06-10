import React, { useState } from 'react';
import { AlertCircle, Check, Sun, Moon, Globe } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { userService } from '../../services/userService';
import { supabase } from '../../config/supabase';
import { changeLanguage } from '../../i18n/config';
import { useTheme } from '../../contexts/ThemeContext';

interface UserSettingsProps {
  onClose: () => void;
}

const UserSettings: React.FC<UserSettingsProps> = ({ onClose }) => {
  const { t, i18n } = useTranslation();
  const { theme, setTheme } = useTheme();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  const handleLanguageChange = (lang: 'he' | 'en') => {
    changeLanguage(lang);
  };

  const handleThemeChange = (newTheme: 'dark' | 'light') => {
    console.log('handleThemeChange called with:', newTheme, 'current theme:', theme);
    setTheme(newTheme);
  };

  console.log('UserSettings rendered with theme:', theme);

  return (
    <div className="space-y-8">
      {/* Error Message */}
      {error && (
        <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mr-2" />
            <p className="text-red-700 dark:text-red-300">{error}</p>
          </div>
        </div>
      )}

      {/* Success Message */}
      {successMessage && (
        <div className="p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border-l-4 border-green-500">
          <div className="flex items-center">
            <Check className="w-5 h-5 text-green-600 dark:text-green-400 mr-2" />
            <p className="text-green-700 dark:text-green-300">{successMessage}</p>
          </div>
        </div>
      )}

      {/* Theme Section */}
      <div className="space-y-4">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-green-50 dark:bg-green-900/20 flex items-center justify-center">
            {theme === 'dark' ? (
              <Moon className="w-4 h-4 text-green-600 dark:text-green-400" />
            ) : (
              <Sun className="w-4 h-4 text-green-600 dark:text-green-400" />
            )}
          </div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            {i18n.language === 'he' ? 'ערכת נושא' : 'Theme'}
          </h3>
        </div>

        <div className="relative">
          <div className="flex p-1 bg-slate-100 dark:bg-gray-800 rounded-xl">
            <button
              onClick={() => handleThemeChange('light')}
              className={`flex-1 flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                theme === 'light'
                  ? 'bg-white dark:bg-gray-700 text-green-600 dark:text-green-400 shadow-sm border border-green-200 dark:border-green-800'
                  : 'text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-gray-200'
              }`}
            >
              <Sun className="w-4 h-4 mr-2" />
              {i18n.language === 'he' ? 'בהיר' : 'Light'}
            </button>
            <button
              onClick={() => handleThemeChange('dark')}
              className={`flex-1 flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                theme === 'dark'
                  ? 'bg-white dark:bg-gray-700 text-green-600 dark:text-green-400 shadow-sm border border-green-200 dark:border-green-800'
                  : 'text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-gray-200'
              }`}
            >
              <Moon className="w-4 h-4 mr-2" />
              {i18n.language === 'he' ? 'כהה' : 'Dark'}
            </button>
          </div>
        </div>
      </div>

      {/* Language Section */}
      <div className="space-y-4">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-green-50 dark:bg-green-900/20 flex items-center justify-center">
            <Globe className="w-4 h-4 text-green-600 dark:text-green-400" />
          </div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            {i18n.language === 'he' ? 'שפה' : 'Language'}
          </h3>
        </div>

        <div className="relative">
          <div className="flex p-1 bg-slate-100 dark:bg-gray-800 rounded-xl">
            <button
              onClick={() => handleLanguageChange('he')}
              className={`flex-1 flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                i18n.language === 'he'
                  ? 'bg-white dark:bg-gray-700 text-green-600 dark:text-green-400 shadow-sm border border-green-200 dark:border-green-800'
                  : 'text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-gray-200'
              }`}
            >
              עברית
            </button>
            <button
              onClick={() => handleLanguageChange('en')}
              className={`flex-1 flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                i18n.language === 'en'
                  ? 'bg-white dark:bg-gray-700 text-green-600 dark:text-green-400 shadow-sm border border-green-200 dark:border-green-800'
                  : 'text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-gray-200'
              }`}
            >
              English
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserSettings; 