import React, { useState, useEffect } from 'react';
import { Shield, Globe } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useLanguage } from '../../contexts/LanguageContext';
import APEXLogo from './components/APEXLogo';
import LoginForm from './components/LoginForm';
import ForgotPasswordModal from './components/ForgotPasswordModal';
import '../../styles/animations.css';

interface APEXStaticLoginProps {
  onLoginSuccess: (isAdmin: boolean) => void;
  onRegisterClick: () => void;
}

const APEXStaticLogin: React.FC<APEXStaticLoginProps> = ({ onLoginSuccess, onRegisterClick }) => {
  const [showForgotModal, setShowForgotModal] = useState(false);
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { login, resetPassword, isLoading, error, clearError } = useAuth();
  const { language, toggleLanguage } = useLanguage();

  // Debug log to verify language context is working
  useEffect(() => {
    console.log('Current language from context:', language);
  }, [language]);

  // Apply RTL/LTR to the login form container
  useEffect(() => {
    // This ensures the document direction matches the current language
    document.documentElement.dir = i18n.language === 'he' ? 'rtl' : 'ltr';
    document.documentElement.lang = i18n.language;
    console.log('Language changed in i18n to:', i18n.language);
  }, [i18n.language]);

  const handleLogin = async (email: string, password: string) => {
    const result = await login(email, password);
    if (result.user && !result.error) {
      onLoginSuccess(result.isAdmin);
    }
  };

  const handleForgotPassword = async (email: string) => {
    return await resetPassword(email);
  };

  // Background ambient effect component
  const AmbientBackground = () => (
    <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
      <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-green-500 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob" />
      <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-green-700 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob animation-delay-2000" />
    </div>
  );

  const handleToggleLanguage = () => {
    console.log('Toggle language button clicked');
    console.log('Before toggle, language is:', language);
    toggleLanguage();
    console.log('After toggle, language should change to:', language === 'en' ? 'he' : 'en');
  };

  const isRTL = i18n.language === 'he';

  return (
    <div className="relative h-screen bg-black text-white overflow-hidden" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Login Content */}
      <div className="flex flex-col items-center justify-center min-h-screen p-4 relative z-10">
        {/* Logo */}
        <APEXLogo 
          subtitle={isRTL ? 'פורטל כניסה' : 'Authentication Portal'} 
          size="md"
        />
        
        {/* Login card */}
        <div className="w-full max-w-md bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-8">
          <div className="flex items-center justify-center mb-4">
            <Shield className="w-6 h-6 text-green-400/80 mr-2" />
            <h2 className="text-2xl font-bold text-green-400">
              {isRTL ? 'כניסה למערכת' : 'Login'}
            </h2>
          </div>
          
          {/* Form */}
          <LoginForm
            onSubmit={handleLogin}
            error={error}
            isLoading={isLoading}
          />
          
          {/* Recovery link */}
          <div className="text-center mt-4" dir={isRTL ? 'rtl' : 'ltr'}>
            <div className="flex flex-col space-y-2">
              <button 
                type="button" 
                onClick={() => setShowForgotModal(true)} 
                className="text-green-400/60 hover:text-green-400/80 text-sm transition-colors"
              >
                {isRTL ? 'שכחתי סיסמה' : 'Forgot Password'}
              </button>
              <button 
                type="button"
                onClick={onRegisterClick}
                className="text-green-400/70 hover:text-green-400 text-sm transition-colors font-medium"
              >
                {isRTL ? 'אין לך חשבון? הירשם עכשיו' : "Don't have an account? Register now"}
              </button>
            </div>
          </div>
          
          {/* System info footer */}
          <div className="mt-6 pt-4 border-t border-green-500/10 text-xs text-green-400/50 flex justify-between items-center" dir={isRTL ? 'rtl' : 'ltr'}>
            <span>APEX v1.0.0</span>
            <button 
              onClick={handleToggleLanguage} 
              className="flex items-center text-green-400/70 hover:text-green-400 transition-colors"
            >
              <Globe className={`w-4 h-4 ${isRTL ? 'ml-1' : 'mr-1'}`} />
              <span>{isRTL ? 'English' : 'עברית'}</span>
            </button>
          </div>
        </div>
      </div>
      
      {/* Forgot password modal */}
      <ForgotPasswordModal
        isOpen={showForgotModal}
        onClose={() => {
          setShowForgotModal(false);
          clearError();
        }}
        onSubmit={handleForgotPassword}
        error={error}
        isLoading={isLoading}
      />
      
      {/* Background effects */}
      <AmbientBackground />
    </div>
  );
};

export default APEXStaticLogin; 