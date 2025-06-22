import React from 'react';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../../contexts/ThemeContext';
import { changeLanguage } from '../../i18n/config';
import { Shield, ChevronLeft, Globe } from 'lucide-react';

// Components
import APEXLogo from './components/APEXLogo';
import RegistrationForm from './components/RegistrationForm';
import BackgroundEffects from './components/BackgroundEffects';

// Hooks
import { useRegistration } from './hooks/useRegistration';

interface APEXRegistrationProps {
  onRegistrationSuccess: (isAdmin: boolean) => void;
  onBackToLogin: () => void;
}

const APEXRegistration: React.FC<APEXRegistrationProps> = ({ 
  onRegistrationSuccess, 
  onBackToLogin 
}) => {
  const { i18n } = useTranslation();
  const { theme } = useTheme();
  
  const registration = useRegistration({ onRegistrationSuccess });

  const toggleLanguage = () => {
    const newLang = i18n.language === 'he' ? 'en' : 'he';
    changeLanguage(newLang);
  };

  return (
    <div className={`relative h-screen overflow-auto ${
      theme === 'dark' 
        ? 'bg-black text-white' 
        : 'bg-gradient-to-br from-gray-50 to-gray-100 text-gray-900'
    }`}>
      
      {/* Registration Content */}
      <div className="flex flex-col items-center justify-center min-h-screen p-4 relative z-10">
        {/* Logo */}
        <APEXLogo 
          subtitle={i18n.language === 'he' ? 'רישום למערכת' : 'Registration Portal'}
          size="lg"
        />
        
        {/* Registration card */}
        <div className={`w-full max-w-md rounded-lg border overflow-hidden shadow-xl ${
          theme === 'dark' 
            ? 'bg-black/30 backdrop-blur-lg border-green-500/20' 
            : 'bg-white/95 backdrop-blur-lg border-gray-200 shadow-lg'
        }`}>
          {/* Header */}
          <div className={`px-6 py-4 flex items-center justify-between border-b ${
            theme === 'dark' 
              ? 'bg-green-500/5 border-green-500/10' 
              : 'bg-green-50 border-gray-200'
          }`}>
            <div className="flex items-center">
              <Shield className={`w-5 h-5 mr-2 ${
                theme === 'dark' ? 'text-green-400/80' : 'text-green-600'
              }`} />
              <span className={`font-semibold ${
                theme === 'dark' ? 'text-green-400/90' : 'text-green-700'
              }`}>
                {i18n.language === 'he' ? 'הרשמה למערכת' : 'System Registration'}
              </span>
            </div>
            <button 
              onClick={onBackToLogin}
              className={`transition-colors flex items-center ${
                theme === 'dark' 
                  ? 'text-green-400/80 hover:text-green-400' 
                  : 'text-green-600 hover:text-green-700'
              }`}
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              <span>{i18n.language === 'he' ? 'חזרה להתחברות' : 'Back to Login'}</span>
            </button>
          </div>
          
          {/* Form */}
          <RegistrationForm
            email={registration.email}
            setEmail={registration.setEmail}
            password={registration.password}
            setPassword={registration.setPassword}
            confirmPassword={registration.confirmPassword}
            setConfirmPassword={registration.setConfirmPassword}
            role={registration.role}
            setRole={registration.setRole}
            showPassword={registration.showPassword}
            setShowPassword={registration.setShowPassword}
            acceptTerms={registration.acceptTerms}
            setAcceptTerms={registration.setAcceptTerms}
            isLoading={registration.isLoading}
            error={registration.error}
            onSubmit={registration.handleSubmit}
            onOpenTerms={registration.openTermsModal}
            theme={theme}
          />
          
          {/* System info footer */}
          <div className={`px-6 py-3 text-xs flex justify-between items-center ${
            theme === 'dark' 
              ? 'bg-black/40 text-green-400/50' 
              : 'bg-gray-50 text-gray-500'
          }`}>
            <span>APEX v1.0.0</span>
            <button 
              onClick={toggleLanguage} 
              className={`flex items-center transition-colors ${
                theme === 'dark' 
                  ? 'text-green-400/70 hover:text-green-400' 
                  : 'text-gray-600 hover:text-gray-700'
              }`}
            >
              <Globe className="w-4 h-4 mr-1" />
              <span>{i18n.language === 'he' ? 'English' : 'עברית'}</span>
            </button>
          </div>
        </div>
      </div>
      
      {/* Background effects */}
      <BackgroundEffects theme={theme} />
    </div>
  );
};

export default APEXRegistration; 