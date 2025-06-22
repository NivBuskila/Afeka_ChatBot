import React from 'react';
import { useTranslation } from 'react-i18next';
import { useThemeClasses } from '../../../hooks/useThemeClasses';
import ThemeButton from '../../ui/ThemeButton';
import ThemeCard from '../../ui/ThemeCard';
import UserSettings from '../../Settings/UserSettings';

interface SettingsModalProps {
  onClose: () => void;
}

const SettingsModal: React.FC<SettingsModalProps> = ({ onClose }) => {
  const { i18n } = useTranslation();
  const { classes } = useThemeClasses();

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <ThemeCard className="w-full max-w-md" shadow="lg" padding="none">
        {/* Header */}
        <div className={`flex items-center justify-between p-6 border-b ${classes.border.primary}`}>
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-xl ${classes.bg.tertiary} flex items-center justify-center`}>
              <svg
                className={`w-5 h-5 ${classes.text.success}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </div>
            <div>
              <h2 className={`text-xl font-semibold ${classes.text.primary}`}>
                {i18n.language === "he" ? "הגדרות" : "Settings"}
              </h2>
              <p className={`text-sm ${classes.text.secondary}`}>
                {i18n.language === "he" ? "התאמה אישית" : "Customize"}
              </p>
            </div>
          </div>
          <ThemeButton
            variant="ghost"
            size="sm"
            onClick={onClose}
            icon={
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            }
          />
        </div>

        {/* Content */}
        <div className="p-6">
          <UserSettings onClose={onClose} />
        </div>
      </ThemeCard>
    </div>
  );
};

export default SettingsModal; 