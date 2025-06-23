import React from 'react';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../../../contexts/ThemeContext';

interface ForgotPasswordModalProps {
  isVisible: boolean;
  forgotEmail: string;
  setForgotEmail: (value: string) => void;
  resetEmailSent: boolean;
  resetEmailLoading: boolean;
  error: string;
  onSubmit: (e: React.FormEvent) => void;
  onClose: () => void;
}

const ForgotPasswordModal: React.FC<ForgotPasswordModalProps> = ({
  isVisible,
  forgotEmail,
  setForgotEmail,
  resetEmailSent,
  resetEmailLoading,
  error,
  onSubmit,
  onClose,
}) => {
  const { i18n } = useTranslation();
  const { theme } = useTheme();

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className={`w-full max-w-md rounded-lg border shadow-lg overflow-hidden ${
        theme === 'dark' 
          ? 'bg-gray-900 border-green-500/20' 
          : 'bg-white border-gray-200'
      }`}>
        <div className={`px-6 py-4 flex justify-between items-center border-b ${
          theme === 'dark' 
            ? 'bg-green-500/5 border-green-500/10' 
            : 'bg-green-50 border-gray-200'
        }`}>
          <span className={`font-semibold ${
            theme === 'dark' ? 'text-green-400/90' : 'text-green-700'
          }`}>
            {i18n.language === 'he' ? 'איפוס סיסמה' : 'Reset Password'}
          </span>
          <button 
            type="button" 
            onClick={onClose}
            className={`${
              theme === 'dark' ? 'text-green-400/60 hover:text-green-400' : 'text-gray-600 hover:text-gray-700'
            }`}
          >
            ✕
          </button>
        </div>
        
        <div className="p-6">
          {resetEmailSent ? (
            <div className={`text-center ${
              theme === 'dark' ? 'text-green-400' : 'text-green-600'
            }`}>
              <p className="text-lg font-semibold mb-2">
                {i18n.language === 'he' ? 'נשלח!' : 'Email Sent!'}
              </p>
              <p className="text-sm opacity-80">
                {i18n.language === 'he' 
                  ? 'קישור לאיפוס הסיסמה נשלח לכתובת האימייל שלך' 
                  : 'A password reset link has been sent to your email address'}
              </p>
              <button 
                onClick={onClose}
                className={`mt-4 px-4 py-2 rounded-md border transition-colors ${
                  theme === 'dark' 
                    ? 'bg-green-500/20 hover:bg-green-500/30 text-green-400 border-green-500/30' 
                    : 'bg-green-600 hover:bg-green-700 text-white border-green-600'
                }`}
              >
                {i18n.language === 'he' ? 'סגור' : 'Close'}
              </button>
            </div>
          ) : (
            <form onSubmit={onSubmit} className="space-y-4">
              <p className={`text-sm ${
                theme === 'dark' ? 'text-green-400/70' : 'text-gray-600'
              }`}>
                {i18n.language === 'he' 
                  ? 'הכנס את כתובת האימייל שלך כדי לקבל קישור לאיפוס הסיסמה' 
                  : 'Enter your email address to receive a password reset link'}
              </p>
              
              {error && (
                <div className={`border px-4 py-3 rounded-md text-sm ${
                  theme === 'dark' 
                    ? 'bg-red-500/10 border-red-500/30 text-red-400' 
                    : 'bg-red-50 border-red-300 text-red-700'
                }`}>
                  {error}
                </div>
              )}
              
              <div>
                <label className={`block text-sm mb-1 ${
                  theme === 'dark' ? 'text-green-400/80' : 'text-gray-700 font-medium'
                }`}>
                  {i18n.language === 'he' ? 'כתובת אימייל' : 'Email Address'}
                </label>
                <input
                  type="email"
                  value={forgotEmail}
                  onChange={(e) => setForgotEmail(e.target.value)}
                  required
                  className={`w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-offset-0 transition-colors ${
                    theme === 'dark' 
                      ? 'bg-black/50 border-green-500/30 text-white focus:ring-green-500/50 focus:border-green-500/50' 
                      : 'bg-white border-gray-300 text-gray-900 focus:ring-green-500 focus:border-green-500'
                  }`}
                  placeholder={i18n.language === 'he' ? 'הכנס כתובת אימייל' : 'Enter your email address'}
                />
              </div>
              
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={resetEmailLoading}
                  className={`flex-1 font-medium py-2 px-4 rounded-md border transition-colors ${
                    theme === 'dark' 
                      ? 'bg-green-500/20 hover:bg-green-500/30 text-green-400 border-green-500/30' 
                      : 'bg-green-600 hover:bg-green-700 text-white border-green-600'
                  } ${resetEmailLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {resetEmailLoading ? (
                    <div className="flex items-center justify-center space-x-1">
                      {[...Array(3)].map((_, i) => (
                        <div
                          key={i}
                          className={`w-1 h-1 rounded-full animate-bounce ${
                            theme === 'dark' ? 'bg-green-400' : 'bg-white'
                          }`}
                          style={{ animationDelay: `${i * 0.2}s` }}
                        />
                      ))}
                    </div>
                  ) : (
                    i18n.language === 'he' ? 'שלח קישור' : 'Send Link'
                  )}
                </button>
                
                <button
                  type="button"
                  onClick={onClose}
                  className={`px-4 py-2 rounded-md border transition-colors ${
                    theme === 'dark' 
                      ? 'bg-gray-800/50 hover:bg-gray-700/50 text-gray-300 border-gray-600/30' 
                      : 'bg-gray-200 hover:bg-gray-300 text-gray-700 border-gray-300'
                  }`}
                >
                  {i18n.language === 'he' ? 'ביטול' : 'Cancel'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordModal; 