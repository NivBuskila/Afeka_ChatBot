import React, { useState } from 'react';
import { Mail, Lock, AlertCircle, Loader2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { userService } from '../../services/userService';
import { supabase } from '../../config/supabase';
import { changeLanguage } from '../../i18n/config';

interface UserSettingsProps {
  onClose: () => void;
}

const UserSettings: React.FC<UserSettingsProps> = ({ onClose }) => {
  const { t, i18n } = useTranslation();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  const handleLanguageChange = (lang: 'he' | 'en') => {
    changeLanguage(lang);
  };

  return (
    <div className="space-y-6">
      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-200 text-red-700 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      )}

      {/* Success Message */}
      {successMessage && (
        <div className="mb-4 p-3 bg-green-100 border border-green-200 text-green-700 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Language Selection */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-white">
          {i18n.language === 'he' ? 'שפה' : 'Language'}
        </h3>
        <div className="flex gap-2">
          <button
            onClick={() => handleLanguageChange('he')}
            className={`flex-1 py-2 px-3 rounded-md ${
              i18n.language === 'he'
                ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 font-medium border border-green-200 dark:border-green-800'
                : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 border border-gray-200 dark:border-gray-700'
            }`}
          >
            {i18n.language === 'he' ? 'עברית' : 'Hebrew'}
          </button>
          <button
            onClick={() => handleLanguageChange('en')}
            className={`flex-1 py-2 px-3 rounded-md ${
              i18n.language === 'en'
                ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 font-medium border border-green-200 dark:border-green-800'
                : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 border border-gray-200 dark:border-gray-700'
            }`}
          >
            {i18n.language === 'he' ? 'אנגלית' : 'English'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserSettings; 