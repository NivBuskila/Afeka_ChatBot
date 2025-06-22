import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';

// Custom hooks
import { useLoginAuth } from './hooks/useLoginAuth';
import { usePasswordReset } from './hooks/usePasswordReset';
import { useLanguageToggle } from './hooks/useLanguageToggle';

// Components
import LoginFormCard from './components/LoginFormCard';
import ForgotPasswordModal from './components/ForgotPasswordModal';
import LoginBackgroundEffects from './components/LoginBackgroundEffects';

interface APEXStaticLoginProps {
  onLoginSuccess: (isAdmin: boolean) => void;
  onRegisterClick: () => void;
}

const APEXStaticLogin: React.FC<APEXStaticLoginProps> = ({ 
  onLoginSuccess, 
  onRegisterClick 
}) => {
  const { theme } = useTheme();
  
  // Custom hooks
  const loginAuth = useLoginAuth({ onLoginSuccess });
  const passwordReset = usePasswordReset();
  const languageToggle = useLanguageToggle();

  // Sync password reset error with login auth error
  const combinedError = loginAuth.error || passwordReset.error;

  return (
    <div className={`relative min-h-screen overflow-auto ${
      theme === 'dark' 
        ? 'bg-black text-white' 
        : 'bg-gradient-to-br from-gray-50 to-gray-100 text-gray-900'
    }`}>
      {/* Background Effects */}
      <LoginBackgroundEffects />
      
      {/* Login Content */}
      <LoginFormCard
        username={loginAuth.username}
        setUsername={loginAuth.setUsername}
        password={loginAuth.password}
        setPassword={loginAuth.setPassword}
        showPassword={loginAuth.showPassword}
        setShowPassword={loginAuth.setShowPassword}
        isLoading={loginAuth.isLoading}
        error={combinedError}
        onSubmit={loginAuth.handleSubmit}
        onForgotPassword={passwordReset.openForgotModal}
        onRegisterClick={onRegisterClick}
        onToggleLanguage={languageToggle.toggleLanguage}
        currentLanguage={languageToggle.currentLanguage}
      />

      {/* Password Reset Modal */}
      <ForgotPasswordModal
        isVisible={passwordReset.showForgotModal}
        forgotEmail={passwordReset.forgotEmail}
        setForgotEmail={passwordReset.setForgotEmail}
        resetEmailSent={passwordReset.resetEmailSent}
        resetEmailLoading={passwordReset.resetEmailLoading}
        error={passwordReset.error}
        onSubmit={passwordReset.handleForgotPassword}
        onClose={passwordReset.closeForgotModal}
      />
    </div>
  );
};

export default APEXStaticLogin; 