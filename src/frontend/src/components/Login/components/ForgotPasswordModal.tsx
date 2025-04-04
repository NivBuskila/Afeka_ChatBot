import React, { useState } from 'react';
import { X, Mail, RefreshCw } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface ForgotPasswordModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (email: string) => Promise<any>;
  error: string | null;
  isLoading: boolean;
}

const ForgotPasswordModal: React.FC<ForgotPasswordModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  error,
  isLoading
}) => {
  const [email, setEmail] = useState('');
  const [success, setSuccess] = useState(false);
  const { t, i18n } = useTranslation();
  
  const isRTL = i18n.language === 'he';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;
    
    try {
      await onSubmit(email);
      setSuccess(true);
    } catch (error) {
      console.error('Error resetting password:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div 
        className="w-full max-w-md bg-black/70 border border-green-500/30 rounded-lg shadow-lg overflow-hidden"
        dir={isRTL ? 'rtl' : 'ltr'}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-green-500/20 bg-green-500/5">
          <h3 className="text-lg font-medium text-green-400">
            {isRTL ? 'איפוס סיסמה' : 'Reset Password'}
          </h3>
          <button
            onClick={onClose}
            className="p-1 rounded-full text-green-400/60 hover:text-green-400 hover:bg-green-500/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* Content */}
        <div className="p-6">
          {success ? (
            <div className="text-center">
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <RefreshCw className="w-8 h-8 text-green-400" />
              </div>
              <h4 className="text-lg font-medium text-green-400 mb-2">
                {isRTL ? 'בקשתך נשלחה בהצלחה' : 'Request Sent Successfully'}
              </h4>
              <p className="text-green-400/70 mb-4">
                {isRTL 
                  ? 'בדוק את תיבת הדואר האלקטרוני שלך להוראות איפוס הסיסמה' 
                  : 'Check your email for password reset instructions'}
              </p>
              <button
                onClick={onClose}
                className="px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-md border border-green-500/30 transition-colors"
              >
                {isRTL ? 'סגור' : 'Close'}
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              {error && (
                <div className="mb-4 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-md text-sm">
                  {error}
                </div>
              )}
              
              <p className="text-green-400/70 mb-4">
                {isRTL 
                  ? 'הזן את כתובת האימייל שלך ואנו נשלח לך קישור לאיפוס הסיסמה' 
                  : 'Enter your email address and we will send you a password reset link'}
              </p>
              
              <div className="mb-4">
                <label htmlFor="reset-email" className="block text-sm text-green-400/80 mb-1">
                  {isRTL ? 'כתובת אימייל' : 'Email Address'}
                </label>
                <div className="relative">
                  <div className={`absolute inset-y-0 ${isRTL ? 'right-0 pr-3' : 'left-0 pl-3'} flex items-center pointer-events-none`}>
                    <Mail className="h-5 w-5 text-green-500/50" />
                  </div>
                  <input
                    id="reset-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className={`w-full ${isRTL ? 'pr-10 pl-4' : 'pl-10 pr-4'} py-2 bg-black/50 border border-green-500/30 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-green-500/50 focus:border-green-500/50`}
                    placeholder={isRTL ? 'הזן את כתובת האימייל שלך' : 'Enter your email address'}
                    dir={isRTL ? 'rtl' : 'ltr'}
                  />
                </div>
              </div>
              
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 text-green-400/60 hover:text-green-400/80 transition-colors mr-2"
                >
                  {isRTL ? 'ביטול' : 'Cancel'}
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-md border border-green-500/30 transition-colors flex items-center"
                >
                  {isLoading ? (
                    <div className="flex space-x-1">
                      {[...Array(3)].map((_, i) => (
                        <div
                          key={i}
                          className="w-1 h-1 bg-green-400 rounded-full animate-bounce"
                          style={{ animationDelay: `${i * 0.2}s` }}
                        />
                      ))}
                    </div>
                  ) : (
                    <>{isRTL ? 'שלח קישור איפוס' : 'Send Reset Link'}</>
                  )}
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