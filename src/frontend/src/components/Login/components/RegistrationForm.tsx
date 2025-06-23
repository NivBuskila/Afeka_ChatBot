import React from 'react';
import { useTranslation } from 'react-i18next';
import { Mail, Lock, Eye, EyeOff, User, Shield, UserPlus } from 'lucide-react';

interface RegistrationFormProps {
  email: string;
  setEmail: (value: string) => void;
  password: string;
  setPassword: (value: string) => void;
  confirmPassword: string;
  setConfirmPassword: (value: string) => void;
  role: 'user' | 'admin';
  setRole: (role: 'user' | 'admin') => void;
  showPassword: boolean;
  setShowPassword: (show: boolean) => void;
  acceptTerms: boolean;
  setAcceptTerms: (accept: boolean) => void;
  isLoading: boolean;
  error: string;
  onSubmit: (e: React.FormEvent) => void;
  onOpenTerms: () => void;
  theme: 'light' | 'dark';
}

const RegistrationForm: React.FC<RegistrationFormProps> = ({
  email,
  setEmail,
  password,
  setPassword,
  confirmPassword,
  setConfirmPassword,
  role,
  setRole,
  showPassword,
  setShowPassword,
  acceptTerms,
  setAcceptTerms,
  isLoading,
  error,
  onSubmit,
  onOpenTerms,
  theme,
}) => {
  const { i18n } = useTranslation();

  return (
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
      
      {/* Email field */}
      <div className="space-y-2">
        <label className={`block text-sm mb-1 ${
          theme === 'dark' ? 'text-green-400/80' : 'text-gray-700 font-medium'
        }`}>
          {i18n.language === 'he' ? 'כתובת אימייל' : 'Email Address'}
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Mail className={`h-5 w-5 ${
              theme === 'dark' ? 'text-green-500/50' : 'text-gray-400'
            }`} />
          </div>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={`w-full pl-10 pr-4 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-offset-0 transition-colors ${
              theme === 'dark' 
                ? 'bg-black/50 border-green-500/30 text-white focus:ring-green-500/50 focus:border-green-500/50' 
                : 'bg-white border-gray-300 text-gray-900 focus:ring-green-500 focus:border-green-500'
            }`}
            placeholder={i18n.language === 'he' ? 'הכנס כתובת אימייל' : 'Enter email address'}
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
            placeholder={i18n.language === 'he' ? 'הכנס סיסמה' : 'Enter password'}
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
      
      {/* Confirm Password field */}
      <div className="space-y-2">
        <label className={`block text-sm mb-1 ${
          theme === 'dark' ? 'text-green-400/80' : 'text-gray-700 font-medium'
        }`}>
          {i18n.language === 'he' ? 'אישור סיסמה' : 'Confirm Password'}
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Lock className={`h-5 w-5 ${
              theme === 'dark' ? 'text-green-500/50' : 'text-gray-400'
            }`} />
          </div>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className={`w-full pl-10 pr-4 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-offset-0 transition-colors ${
              theme === 'dark' 
                ? 'bg-black/50 border-green-500/30 text-white focus:ring-green-500/50 focus:border-green-500/50' 
                : 'bg-white border-gray-300 text-gray-900 focus:ring-green-500 focus:border-green-500'
            }`}
            placeholder={i18n.language === 'he' ? 'אשר את הסיסמה' : 'Confirm your password'}
          />
        </div>
      </div>
      
      {/* Role selection */}
      <div className="space-y-2">
        <label className={`block text-sm mb-3 ${
          theme === 'dark' ? 'text-green-400/80' : 'text-gray-700 font-medium'
        }`}>
          {i18n.language === 'he' ? 'תפקיד' : 'Role'}
        </label>
        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => setRole('user')}
            className={`flex items-center justify-center px-4 py-3 rounded-md border font-medium transition-colors ${
              role === 'user'
                ? theme === 'dark'
                  ? 'bg-green-500/20 text-green-400 border-green-500/30'
                  : 'bg-green-100 text-green-700 border-green-300'
                : theme === 'dark'
                  ? 'bg-black/30 text-green-400/70 border-green-500/20 hover:bg-green-500/10'
                  : 'bg-gray-50 text-gray-600 border-gray-300 hover:bg-gray-100'
            }`}
          >
            <User className="w-4 h-4 mr-2" />
            {i18n.language === 'he' ? 'משתמש רגיל' : 'Regular User'}
          </button>
          <button
            type="button"
            onClick={() => setRole('admin')}
            className={`flex items-center justify-center px-4 py-3 rounded-md border font-medium transition-colors ${
              role === 'admin'
                ? theme === 'dark'
                  ? 'bg-green-500/20 text-green-400 border-green-500/30'
                  : 'bg-green-100 text-green-700 border-green-300'
                : theme === 'dark'
                  ? 'bg-black/30 text-green-400/70 border-green-500/20 hover:bg-green-500/10'
                  : 'bg-gray-50 text-gray-600 border-gray-300 hover:bg-gray-100'
            }`}
          >
            <Shield className="w-4 h-4 mr-2" />
            {i18n.language === 'he' ? 'מנהל מערכת' : 'System Admin'}
          </button>
        </div>
      </div>
      
      {/* Terms & Conditions checkbox */}
      <div className="flex items-start space-x-3">
        <input
          type="checkbox"
          id="terms"
          checked={acceptTerms}
          onChange={(e) => setAcceptTerms(e.target.checked)}
          className="mt-1 h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
        />
        <label htmlFor="terms" className={`text-sm ${
          theme === 'dark' ? 'text-green-400/80' : 'text-gray-700'
        }`}>
          {i18n.language === 'he' ? (
            <>
              אני מסכים ל
              <button
                type="button"
                onClick={onOpenTerms}
                className={`ml-1 underline ${
                  theme === 'dark' ? 'text-green-400 hover:text-green-300' : 'text-green-600 hover:text-green-700'
                }`}
              >
                תנאי השימוש
              </button>
            </>
          ) : (
            <>
              I accept the{' '}
              <button
                type="button"
                onClick={onOpenTerms}
                className={`underline ${
                  theme === 'dark' ? 'text-green-400 hover:text-green-300' : 'text-green-600 hover:text-green-700'
                }`}
              >
                terms and conditions
              </button>
            </>
          )}
        </label>
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
            <UserPlus className="w-5 h-5 ml-2" />
            <span>{i18n.language === 'he' ? 'הרשם למערכת' : 'Register'}</span>
          </>
        )}
      </button>
    </form>
  );
};

export default RegistrationForm; 