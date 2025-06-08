import React from 'react';
import { useTranslation } from 'react-i18next';
import { Bell, Search, UserCog } from 'lucide-react';

type Language = 'he' | 'en';

interface TopBarProps {
  language: Language;
}

export const TopBar: React.FC<TopBarProps> = ({ language }) => {
  const { t, i18n } = useTranslation();

  return (
    <div className="bg-gray-100/50 dark:bg-black/50 backdrop-blur-sm border-b border-gray-300/20 dark:border-green-500/20 py-3 px-6 transition-colors duration-300">
      <div className="flex justify-between items-center">
        <div></div>
        
        <div className="flex items-center space-x-4 space-x-reverse">
          <div className="relative">
            <Bell className="w-6 h-6 text-gray-600 dark:text-green-400/70" />
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
              2
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}; 