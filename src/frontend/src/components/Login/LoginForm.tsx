import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

interface LoginFormProps {
  onSubmit: (email: string, password: string) => Promise<void>;
  error: string | null;
  loading: boolean;
}

const LoginForm: React.FC<LoginFormProps> = ({ onSubmit, error, loading }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);
  const { t, i18n } = useTranslation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    
    // Basic validation check
    if (!email.trim()) {
      setLocalError(i18n.language === 'he' ? 'נא להזין אימייל' : 'Please enter an email');
      return;
    }
    
    if (!password.trim()) {
      setLocalError(i18n.language === 'he' ? 'נא להזין סיסמה' : 'Please enter a password');
      return;
    }
    
    try {
      console.log('התחלת תהליך התחברות:', email);
      await onSubmit(email, password);
    } catch (err: any) {
      console.error('שגיאת התחברות:', err);
      setLocalError(err.message || 'שגיאה בהתחברות');
    }
  };

  // If there are predefined test users
  const loginAsTestUser = (userType: 'user' | 'admin') => {
    if (userType === 'user') {
      setEmail('omriuser@gmail.com');
      setPassword('Test123!');
    } else {
      setEmail('omriadmin@gmail.com');
      setPassword('Test123!');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {(error || localError) && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">{i18n.language === 'he' ? 'שגיאה:' : 'Error:'}</strong>
          <span className="block sm:inline"> {error || localError}</span>
        </div>
      )}
      
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          {i18n.language === 'he' ? 'אימייל' : 'Email'}
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          placeholder={i18n.language === 'he' ? 'הכנס אימייל' : 'Enter your email'}
          dir={i18n.language === 'he' ? 'rtl' : 'ltr'}
          required
        />
      </div>
      
      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
          {i18n.language === 'he' ? 'סיסמה' : 'Password'} 
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          placeholder={i18n.language === 'he' ? 'הכנס סיסמה' : 'Enter your password'}
          dir={i18n.language === 'he' ? 'rtl' : 'ltr'}
          required
        />
      </div>
      
      <div>
        <button
          type="submit"
          disabled={loading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          {loading ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {i18n.language === 'he' ? 'מתחבר...' : 'Signing in...'}
            </span>
          ) : (
            <span>{i18n.language === 'he' ? 'התחבר' : 'Sign in'}</span>
          )}
        </button>
      </div>
      
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-4 border-t pt-4">
          <p className="text-xs text-gray-500 mb-2">{i18n.language === 'he' ? 'משתמשי טסט (רק בסביבת פיתוח):' : 'Test users (development only):'}</p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => loginAsTestUser('user')}
              className="text-xs px-2 py-1 bg-gray-100 rounded"
            >
              {i18n.language === 'he' ? 'משתמש רגיל' : 'Regular User'}
            </button>
            <button
              type="button"
              onClick={() => loginAsTestUser('admin')}
              className="text-xs px-2 py-1 bg-gray-100 rounded"
            >
              {i18n.language === 'he' ? 'מנהל מערכת' : 'Admin User'}
            </button>
          </div>
        </div>
      )}
    </form>
  );
};

export default LoginForm; 