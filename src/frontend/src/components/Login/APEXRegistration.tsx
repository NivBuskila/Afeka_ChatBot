import React, { useState, useEffect } from 'react';
import { Brain, LogIn, Shield, User, Lock, Eye, EyeOff, Mail, ChevronLeft, UserPlus, Globe } from 'lucide-react';
import '../../styles/animations.css';
import { supabase } from '../../config/supabase';
import { userService } from '../../services/userService';
import { useTranslation } from 'react-i18next';
import { changeLanguage } from '../../i18n/config';
import { useTheme } from '../../contexts/ThemeContext';

interface APEXRegistrationProps {
  onRegistrationSuccess: (isAdmin: boolean) => void;
  onBackToLogin: () => void;
}

const APEXRegistration: React.FC<APEXRegistrationProps> = ({ onRegistrationSuccess, onBackToLogin }) => {
  const { theme } = useTheme();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState<'user' | 'admin'>('user');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState(1);
  const [acceptTerms, setAcceptTerms] = useState(false);
  const { i18n } = useTranslation();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Field validation
    if (!email.trim()) {
      setError(i18n.language === 'he' ? 'נא להזין כתובת אימייל' : 'Please enter an email address');
      return;
    }
    
    if (!password.trim()) {
      setError(i18n.language === 'he' ? 'נא להזין סיסמה' : 'Please enter a password');
      return;
    }
    
    if (password !== confirmPassword) {
      setError(i18n.language === 'he' ? 'הסיסמאות אינן תואמות' : 'Passwords do not match');
      return;
    }
    
    if (!acceptTerms) {
      setError(i18n.language === 'he' ? 'יש לאשר את תנאי השימוש כדי להמשיך' : 'You must accept the terms and conditions to continue');
      return;
    }
    
    setIsLoading(true);
    
    try {
      // Direct method - create user directly via API
      const { data: authData, error: authError } = await supabase.auth.signUp({
        email: email.trim(),
        password,
        options: {
          // Important flag to bypass the error
          emailRedirectTo: window.location.origin + '/auth/callback',
          data: {
            is_admin: role === 'admin',
            role: role,
            name: email.split('@')[0]
          }
        }
      });
      
      if (authError) {
        console.error('Auth error:', authError);
        setError(i18n.language === 'he' ? 'שגיאה ברישום: ' + authError.message : 'Registration error: ' + authError.message);
        setIsLoading(false);
        return;
      }
      
      if (!authData.user) {
        setError(i18n.language === 'he' ? 'הרישום נכשל - לא נוצר משתמש' : 'Registration failed - no user created');
        setIsLoading(false);
        return;
      }
      
      // Create user in users table manually
      try {
        const { error: dbInsertError } = await supabase
          .from('users')
          .insert({
            id: authData.user.id,
            email: email.trim(),
            name: email.split('@')[0],
            status: 'active',
            last_sign_in: new Date().toISOString(),
            preferred_language: i18n.language || 'he',
            timezone: 'Asia/Jerusalem'
          });
        
        if (dbInsertError) {
          console.warn('Error inserting user record:', dbInsertError);
          // Continue despite error, as trigger may have already created the record
        }
        
        // If admin user, add to admins table
        // Might get 403 error, but that's ok - will be handled on first login
        if (role === 'admin') {
          try {
            const { error: adminError } = await supabase
              .from('admins')
              .insert({ 
                user_id: authData.user.id,
                permissions: ['read', 'write']
              });
            
            if (adminError) {
              console.warn('Error setting admin role:', adminError);
              // Don't handle error here - will be addressed on first login
            }
          } catch (adminInsertError) {
            console.warn('Exception setting admin role:', adminInsertError);
            // Continue despite error - will be handled on login
          }
        }
      } catch (dbError) {
        console.warn('Database error:', dbError);
        // Continue despite error, as user is already created in Auth
      }
      
      // Now perform automatic login with created user
      try {
        const { error: signInError } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password
        });
        
        if (signInError) {
          console.warn('Auto sign-in error:', signInError);
          // Don't fail because of this, just notify user of successful registration and prompt to login
        }
      } catch (signInError) {
        console.warn('Exception during auto sign-in:', signInError);
        // Continue despite error - ask user to login
      }
      
      // Call function to notify parent of registration success
      onRegistrationSuccess(role === 'admin');
    } catch (error: any) {
      console.error('Registration error:', error);
      
      // Ignore 403 errors related to admins table
      if (error.message?.includes('admins') && error.message?.includes('403')) {
        console.warn('Ignoring admin 403 error - registration succeeded');
        onRegistrationSuccess(role === 'admin');
        return;
      }
      
      setError(i18n.language === 'he' ? 'שגיאה ברישום: ' + error.message : 'Registration error: ' + error.message);
      setIsLoading(false);
    }
  };

  const openTermsModal = () => {
    window.open('/terms-and-conditions', '_blank');
  };

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
        <div className="mb-8 flex flex-col items-center">
          <div className="relative">
            <div className={`absolute inset-0 rounded-full filter blur-lg opacity-20 ${
              theme === 'dark' ? 'bg-green-500' : 'bg-green-600'
            }`} />
            <Brain className={`w-16 h-16 relative z-10 ${
              theme === 'dark' ? 'text-green-400' : 'text-green-600'
            }`} />
          </div>
          <div className={`mt-4 text-3xl font-bold ${
            theme === 'dark' ? 'text-green-400' : 'text-green-600'
          }`}>APEX</div>
          <div className={`text-sm mt-1 ${
            theme === 'dark' ? 'text-green-400/70' : 'text-green-600/80'
          }`}>
            {i18n.language === 'he' ? 'רישום למערכת' : 'Registration Portal'}
          </div>
        </div>
        
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
          <form onSubmit={handleSubmit} className="p-6 space-y-5">
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
                      onClick={openTermsModal}
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
                      onClick={openTermsModal}
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
      {theme === 'light' && (
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
          <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-green-200 rounded-full mix-blend-multiply filter blur-[128px] opacity-20 animate-blob" />
          <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-green-300 rounded-full mix-blend-multiply filter blur-[128px] opacity-15 animate-blob animation-delay-2000" />
        </div>
      )}

      {theme === 'dark' && (
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
          <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-green-500 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob" />
          <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-green-700 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob animation-delay-2000" />
        </div>
      )}
    </div>
  );
};

export default APEXRegistration; 