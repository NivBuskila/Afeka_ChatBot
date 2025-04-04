import React, { useState, useEffect } from 'react';
import { User, Lock, Eye, EyeOff, LogIn, Loader2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface LoginFormProps {
  onSubmit: (email: string, password: string) => Promise<void>;
  error: string | null;
  isLoading: boolean;
}

const LoginForm: React.FC<LoginFormProps> = ({ onSubmit, error, isLoading }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const { t, i18n } = useTranslation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) return;
    await onSubmit(email, password);
  };

  // Helper function to determine input icon position based on language
  const getIconPosition = (isRTL: boolean, position: 'start' | 'end') => {
    if (position === 'start') {
      return isRTL ? 'right-0 pr-3' : 'left-0 pl-3';
    } else {
      return isRTL ? 'left-0 pl-3' : 'right-0 pr-3';
    }
  };

  // Helper function to determine input padding based on language
  const getInputPadding = (isRTL: boolean) => {
    return isRTL ? 'pr-10 pl-10' : 'pl-10 pr-10';
  };

  const isRTL = i18n.language === 'he';

  return (
    <form onSubmit={handleSubmit} dir={isRTL ? 'rtl' : 'ltr'}>
      {error && (
        <div className="mb-4 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-md text-sm">
          {error}
        </div>
      )}
      
      <div className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-sm text-green-400/80 mb-1">
            {isRTL ? 'שם משתמש' : 'Username'}
          </label>
          <div className="relative">
            <div className={`absolute inset-y-0 ${getIconPosition(isRTL, 'start')} flex items-center pointer-events-none`}>
              <User className="h-5 w-5 text-green-500/50" />
            </div>
            <input
              id="username"
              type="text"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={isRTL ? 'הכנס שם משתמש' : 'Enter your username'}
              className={`w-full ${getInputPadding(isRTL)} py-2 bg-black/50 border border-green-500/30 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-green-500/50 focus:border-green-500/50`}
              dir={isRTL ? 'rtl' : 'ltr'}
            />
          </div>
        </div>
        
        <div>
          <label htmlFor="password" className="block text-sm text-green-400/80 mb-1">
            {isRTL ? 'סיסמה' : 'Password'}
          </label>
          <div className="relative">
            <div className={`absolute inset-y-0 ${getIconPosition(isRTL, 'start')} flex items-center pointer-events-none`}>
              <Lock className="h-5 w-5 text-green-500/50" />
            </div>
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={isRTL ? 'הכנס סיסמה' : 'Enter your password'}
              className={`w-full ${getInputPadding(isRTL)} py-2 bg-black/50 border border-green-500/30 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-green-500/50 focus:border-green-500/50`}
              dir={isRTL ? 'rtl' : 'ltr'}
            />
            <div 
              className={`absolute inset-y-0 ${getIconPosition(isRTL, 'end')} flex items-center cursor-pointer`}
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? 
                <EyeOff className="h-5 w-5 text-green-500/50" /> : 
                <Eye className="h-5 w-5 text-green-500/50" />
              }
            </div>
          </div>
        </div>
        
        <button 
          type="submit"
          disabled={isLoading}
          className="w-full px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 font-medium rounded-md border border-green-500/30 transition-colors flex items-center justify-center gap-2"
          dir={isRTL ? 'rtl' : 'ltr'}
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              {isRTL ? 'מתחבר...' : 'Logging in...'}
            </>
          ) : (
            <>
              <LogIn className={`w-5 h-5 ${isRTL ? 'ml-1 order-1' : 'mr-1 order-0'}`} />
              {isRTL ? 'כניסה למערכת' : 'Login to APEX'}
            </>
          )}
        </button>
      </div>
    </form>
  );
};

export default LoginForm; 