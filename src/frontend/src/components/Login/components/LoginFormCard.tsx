import React from 'react';
import { LogIn, Shield, User, Lock, Eye, EyeOff, Globe } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../../../contexts/ThemeContext';
import APEXLogo from './APEXLogo';

interface LoginFormCardProps {
  username: string;
  setUsername: (value: string) => void;
  password: string;
  setPassword: (value: string) => void;
  showPassword: boolean;
  setShowPassword: (value: boolean) => void;
  isLoading: boolean;
  error: string;
  onSubmit: (e: React.FormEvent) => void;
  onForgotPassword: () => void;
  onRegisterClick: () => void;
  onToggleLanguage: () => void;
  currentLanguage: string;
}

const LoginFormCard: React.FC<LoginFormCardProps> = ({
  username,
  setUsername,
  password,
  setPassword,
  showPassword,
  setShowPassword,
  isLoading,
  error,
  onSubmit,
  onForgotPassword,
  onRegisterClick,
  onToggleLanguage,
  currentLanguage,
}) => {
  const { t, i18n } = useTranslation();
  const { theme } = useTheme();

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 relative z-10">
      {/* Logo */}
      <APEXLogo 
        subtitle={i18n.language === 'he' ? 'פורטל כניסה' : 'Authentication Portal'}
        size="lg"
      />
      
      {/* Login card */}
      <div className={`w-full max-w-md rounded-lg border overflow-hidden shadow-xl ${
        theme === 'dark' 
          ? 'bg-black/30 backdrop-blur-lg border-green-500/20' 
          : 'bg-white/95 backdrop-blur-lg border-gray-200 shadow-lg'
      }`}>
        {/* Header */}
        <div className={`px-6 py-4 flex items-center border-b ${
          theme === 'dark' 
            ? 'bg-green-500/5 border-green-500/10' 
            : 'bg-green-50 border-gray-200'
        }`}>
          <Shield className={`w-5 h-5 mr-2 ${
            theme === 'dark' ? 'text-green-400/80' : 'text-green-600'
          }`} />
          <span className={`font-semibold ${
            theme === 'dark' ? 'text-green-400/90' : 'text-green-700'
          }`}>
            {i18n.language === 'he' ? 'כניסה מאובטחת' : 'Secure Login'}
          </span>
        </div>
        
        {/* Form */}
        <form onSubmit={onSubmit} className="p-6 space-y-5">
          {error && (
            <div className={`border px-4 py-3 rounded-md text-sm ${
              theme === 'dark' 
                ? 'bg-red-500/10 border-red-500/30 text-red-400' 
                : 'bg-red-50 border-red-300 text-red-700'
            }`}>
              {error}
            </div>
          )}
          
          {/* Username field */}
          <div className="space-y-2">
            <label className={`block text-sm mb-1 ${
              theme === 'dark' ? 'text-green-400/80' : 'text-gray-700 font-medium'
            }`}>
              {i18n.language === 'he' ? 'שם משתמש' : 'Username'}
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className={`h-5 w-5 ${
                  theme === 'dark' ? 'text-green-500/50' : 'text-gray-400'
                }`} />
              </div>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className={`w-full pl-10 pr-4 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-offset-0 transition-colors ${
                  theme === 'dark' 
                    ? 'bg-black/50 border-green-500/30 text-white focus:ring-green-500/50 focus:border-green-500/50' 
                    : 'bg-white border-gray-300 text-gray-900 focus:ring-green-500 focus:border-green-500'
                }`}
                placeholder={i18n.language === 'he' ? 'הכנס שם משתמש' : 'Enter your username'}
              />
            </div>
          </div>
          
          {/* Password field */}
          <div className="space-y-2">
            <label className={`block text-sm mb-1 ${
              theme === 'dark' ? 'text-green-400/80' : 'text-gray-700 font-medium'
            }`}>
              {i18n.language === 'he' ? 'סיסמה' : 'Password'}
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className={`h-5 w-5 ${
                  theme === 'dark' ? 'text-green-500/50' : 'text-gray-400'
                }`} />
              </div>
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={`w-full pl-10 pr-10 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-offset-0 transition-colors ${
                  theme === 'dark' 
                    ? 'bg-black/50 border-green-500/30 text-white focus:ring-green-500/50 focus:border-green-500/50' 
                    : 'bg-white border-gray-300 text-gray-900 focus:ring-green-500 focus:border-green-500'
                }`}
                placeholder={i18n.language === 'he' ? 'הכנס סיסמה' : 'Enter your password'}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                {showPassword ? (
                  <EyeOff className={`h-5 w-5 ${
                    theme === 'dark' ? 'text-green-500/50' : 'text-gray-400'
                  }`} />
                ) : (
                  <Eye className={`h-5 w-5 ${
                    theme === 'dark' ? 'text-green-500/50' : 'text-gray-400'
                  }`} />
                )}
              </button>
            </div>
          </div>
          
          {/* Submit button */}
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full font-medium py-3 px-4 rounded-md border transition-colors flex items-center justify-center space-x-2 ${
              theme === 'dark' 
                ? 'bg-green-500/20 hover:bg-green-500/30 text-green-400 border-green-500/30' 
                : 'bg-green-600 hover:bg-green-700 text-white border-green-600 shadow-md hover:shadow-lg'
            }`}
          >
            {isLoading ? (
              <div className="flex space-x-1">
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
              <>
                <LogIn className="w-5 h-5" />
                <span>{i18n.language === 'he' ? 'כניסה למערכת' : 'Login to APEX'}</span>
              </>
            )}
          </button>
          
          {/* Recovery links */}
          <div className="text-center mt-4">
            <div className="flex flex-col space-y-2">
              <button 
                type="button" 
                onClick={onForgotPassword} 
                className={`text-sm transition-colors ${
                  theme === 'dark' 
                    ? 'text-green-400/60 hover:text-green-400/80' 
                    : 'text-green-600 hover:text-green-700'
                }`}
              >
                {i18n.language === 'he' ? 'שכחתי סיסמה' : 'Forgot Password'}
              </button>
              <button 
                type="button"
                onClick={onRegisterClick}
                className={`text-sm transition-colors font-medium ${
                  theme === 'dark' 
                    ? 'text-green-400/70 hover:text-green-400' 
                    : 'text-green-600 hover:text-green-700'
                }`}
              >
                {i18n.language === 'he' ? 'אין לך חשבון? הירשם עכשיו' : "Don't have an account? Register now"}
              </button>
            </div>
          </div>
        </form>
        
        {/* System info footer */}
        <div className={`px-6 py-3 text-xs flex justify-between items-center ${
          theme === 'dark' 
            ? 'bg-black/40 text-green-400/50' 
            : 'bg-gray-50 text-gray-500'
        }`}>
          <span>APEX v1.0.0</span>
          <button 
            onClick={onToggleLanguage} 
            className={`flex items-center transition-colors ${
              theme === 'dark' 
                ? 'text-green-400/70 hover:text-green-400' 
                : 'text-gray-600 hover:text-gray-700'
            }`}
          >
            <Globe className="w-4 h-4 mr-1" />
            <span>{currentLanguage === 'he' ? 'English' : 'עברית'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginFormCard; 