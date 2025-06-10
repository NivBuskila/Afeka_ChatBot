import React, { useState, useEffect, useRef } from 'react';
import { Brain, LogIn, Shield, User, Lock, Eye, EyeOff, Globe } from 'lucide-react';
import './APEXStaticLogin.css';
import { supabase } from '../../config/supabase';
import { useTranslation } from 'react-i18next';
import { changeLanguage } from '../../i18n/config';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../../contexts/ThemeContext';

interface APEXStaticLoginProps {
  onLoginSuccess: (isAdmin: boolean) => void;
  onRegisterClick: () => void;
}

const APEXStaticLogin: React.FC<APEXStaticLoginProps> = ({ onLoginSuccess, onRegisterClick }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [forgotEmail, setForgotEmail] = useState('');
  const [showForgotModal, setShowForgotModal] = useState(false);
  const [resetEmailSent, setResetEmailSent] = useState(false);
  const [resetEmailLoading, setResetEmailLoading] = useState(false);
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { theme } = useTheme();
  
  // Minimal Matrix effect
  const MatrixRain = () => {
    const canvas = useRef<HTMLCanvasElement>(null);
    
    useEffect(() => {
      let canvasElement = canvas.current;
      
      // Wait a bit after render to ensure canvas exists
      const initTimer = setTimeout(() => {
        canvasElement = canvas.current;
        if (!canvasElement) {
          console.warn('Canvas element not available');
          return;
        }
        
        const ctx = canvasElement.getContext('2d');
        if (!ctx) {
          console.warn('Canvas context not available');
          return;
        }
        
        const updateCanvasSize = () => {
          if (!canvasElement) return;
          canvasElement.width = window.innerWidth;
          canvasElement.height = window.innerHeight;
        };
        
        updateCanvasSize();
        window.addEventListener('resize', updateCanvasSize);
        
        const binary = '01';
        const fontSize = 14;
        
        let columns: number[] = [];
        
        const initColumns = () => {
          if (!canvasElement) return;
          const columnsCount = Math.floor(canvasElement.width / fontSize);
          columns = Array(columnsCount).fill(1);
        };
        
        initColumns();
        
        const draw = () => {
          if (!canvasElement || !ctx || columns.length === 0) return;
          
          ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
          ctx.fillRect(0, 0, canvasElement.width, canvasElement.height);
          ctx.fillStyle = '#0f0';
          ctx.font = `${fontSize}px monospace`;
          
          for (let i = 0; i < columns.length; i++) {
            const text = binary.charAt(Math.floor(Math.random() * binary.length));
            ctx.fillText(text, i * fontSize, columns[i] * fontSize);
            columns[i]++;
            if (columns[i] * fontSize > canvasElement.height && Math.random() > 0.975) {
              columns[i] = 0;
            }
          }
        };
        
        const interval = setInterval(draw, 33);
        
        return () => {
          clearInterval(interval);
          window.removeEventListener('resize', updateCanvasSize);
        };
      }, 100); // Small delay to allow render to complete
      
      return () => {
        clearTimeout(initTimer);
      };
    }, []);

    return (
      <canvas
        ref={canvas}
        className="absolute inset-0 opacity-5"
        style={{ zIndex: 0 }}
      />
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Validate fields
    if (!username.trim() || !password.trim()) {
      setError(i18n.language === 'he' ? 'נא להזין שם משתמש וסיסמה' : 'Please enter both username and password');
      return;
    }
    
    // Show loading state
    setIsLoading(true);
    
    // Authentication via Supabase
    setTimeout(async () => {
      try {
        // Login to Supabase with email and password
        const { data, error } = await supabase.auth.signInWithPassword({
          email: username.trim(), // Use username field as email
          password: password,
        });
        
        if (error) {
          setError(i18n.language === 'he' ? 'התחברות נכשלה: ' + error.message : 'Login failed: ' + error.message);
          setIsLoading(false);
          return;
        }
        
        if (!data.user) {
          setError(i18n.language === 'he' ? 'לא ניתן לאמת את פרטי המשתמש' : 'Could not authenticate user');
          setIsLoading(false);
          return;
        }
        
        console.log('התחברות הצליחה, מידע משתמש:', data.user);
        
        // Due to RLS issues, check if user is admin
        try {
          console.log('בודק אם המשתמש הוא מנהל...');
          
          // First try direct access to admins table
          try {
            const { data: adminData, error: adminError } = await supabase
              .from('admins')
              .select('*')
              .eq('user_id', data.user.id)
              .maybeSingle();
            
            if (!adminError && adminData) {
              console.log('מצאתי מנהל בטבלת המנהלים:', adminData);
              onLoginSuccess(true);
              return;
            } else if (adminError) {
              console.error('שגיאה בבדיקת טבלת מנהלים:', adminError);
            }
          } catch (dbError) {
            console.error('שגיאת גישה לטבלת מנהלים:', dbError);
          }
          
          // If direct access failed, try using RPC
          try {
            // Use a single explicit parameter to avoid ambiguity
            const { data: isAdminResult, error: isAdminError } = await supabase
              .rpc('is_admin', { user_id: data.user.id });
            
            if (isAdminError) {
              console.error('שגיאה בקריאת is_admin RPC:', isAdminError);
            } else if (isAdminResult === true) {
              console.log('המשתמש הוא מנהל לפי is_admin RPC');
              onLoginSuccess(true);
              return;
            }
          } catch (rpcError) {
            console.error('שגיאה בקריאת RPC:', rpcError);
          }
          
          // If we got here, try reading from user metadata
          const isAdminFromMetadata = data.user.user_metadata?.role === 'admin';
          console.log('בדיקת מנהל ממטא-דאטה:', isAdminFromMetadata);
          
          // Final decision on role
          onLoginSuccess(isAdminFromMetadata || false);
          
        } catch (err) {
          console.error('שגיאה בבדיקת מנהל:', err);
          // In case of error, login as regular user
          onLoginSuccess(false);
        }
        
      } catch (err) {
        console.error('Authentication error:', err);
        setError('אירעה שגיאה בהתחברות לשרת');
        setIsLoading(false);
      }
    }, 500);
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!forgotEmail.trim()) {
      setError(i18n.language === 'he' ? 'נא להזין כתובת אימייל' : 'Please enter your email address');
      return;
    }
    
    setResetEmailLoading(true);
    
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(forgotEmail, {
        redirectTo: `${window.location.origin}/reset-password`,
      });
      
      if (error) {
        setError(i18n.language === 'he' ? 'שגיאה בשליחת קישור איפוס: ' + error.message : 'Error sending reset link: ' + error.message);
        setResetEmailLoading(false);
        return;
      }
      
      setResetEmailSent(true);
      setResetEmailLoading(false);
    } catch (err) {
      console.error('Error sending password reset email:', err);
      setError(i18n.language === 'he' ? 'אירעה שגיאה בשליחת דוא"ל לאיפוס סיסמה' : 'Error sending password reset email');
      setResetEmailLoading(false);
    }
  };

  const closeForgotModal = () => {
    setShowForgotModal(false);
    setForgotEmail('');
    setResetEmailSent(false);
    setError('');
  };

  const toggleLanguage = () => {
    const newLang = i18n.language === 'he' ? 'en' : 'he';
    changeLanguage(newLang);
  };

  return (
    <div className={`relative min-h-screen overflow-auto ${
      theme === 'dark' 
        ? 'bg-black text-white' 
        : 'bg-gradient-to-br from-gray-50 to-gray-100 text-gray-900'
    }`}>
      {theme === 'dark' && <MatrixRain />}
      
      {/* Login Content */}
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
            {i18n.language === 'he' ? 'פורטל כניסה' : 'Authentication Portal'}
          </div>
        </div>
        
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
                  onClick={() => setShowForgotModal(true)} 
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
      
      {/* Light mode background effects */}
      {theme === 'light' && (
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
          <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-green-200 rounded-full mix-blend-multiply filter blur-[128px] opacity-20 animate-blob" />
          <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-green-300 rounded-full mix-blend-multiply filter blur-[128px] opacity-15 animate-blob animation-delay-2000" />
        </div>
      )}

      {/* Dark mode background effects */}
      {theme === 'dark' && (
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
          <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-green-500 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob" />
          <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-green-700 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob animation-delay-2000" />
        </div>
      )}

      {/* Password Reset Modal */}
      {showForgotModal && (
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
                onClick={closeForgotModal}
                className={`${
                  theme === 'dark' ? 'text-green-400/60 hover:text-green-400' : 'text-gray-600 hover:text-gray-700'
                }`}
              >
                ✕
              </button>
            </div>
            
            <div className="p-6">
              {resetEmailSent ? (
                <div className="text-center py-4">
                  <div className={`border px-4 py-3 rounded-md text-sm mb-4 ${
                    theme === 'dark' 
                      ? 'bg-green-500/10 border-green-500/30 text-green-400' 
                      : 'bg-green-50 border-green-300 text-green-700'
                  }`}>
                    {i18n.language === 'he' 
                      ? 'קישור לאיפוס סיסמה נשלח לאימייל שלך' 
                      : 'Password reset link has been sent to your email'}
                  </div>
                  <button
                    type="button"
                    onClick={closeForgotModal}
                    className={`font-medium py-2 px-4 rounded-md border transition-colors ${
                      theme === 'dark' 
                        ? 'bg-green-500/20 hover:bg-green-500/30 text-green-400 border-green-500/30' 
                        : 'bg-green-600 hover:bg-green-700 text-white border-green-600'
                    }`}
                  >
                    {i18n.language === 'he' ? 'סגור' : 'Close'}
                  </button>
                </div>
              ) : (
                <form onSubmit={handleForgotPassword}>
                  <p className={`mb-4 ${
                    theme === 'dark' ? 'text-gray-400' : 'text-gray-600'
                  }`}>
                    {i18n.language === 'he' 
                      ? 'הזן את כתובת האימייל שלך ואנו נשלח לך קישור לאיפוס הסיסמה' 
                      : 'Enter your email address and we will send you a password reset link'}
                  </p>
                  
                  {error && (
                    <div className={`border px-4 py-3 rounded-md text-sm mb-4 ${
                      theme === 'dark' 
                        ? 'bg-red-500/10 border-red-500/30 text-red-400' 
                        : 'bg-red-50 border-red-300 text-red-700'
                    }`}>
                      {error}
                    </div>
                  )}
                  
                  <div className="space-y-4">
                    <div>
                      <label className={`block text-sm mb-1 ${
                        theme === 'dark' ? 'text-green-400/80' : 'text-gray-700 font-medium'
                      }`}>
                        {i18n.language === 'he' ? 'אימייל' : 'Email'}
                      </label>
                      <input
                        type="email"
                        value={forgotEmail}
                        onChange={(e) => setForgotEmail(e.target.value)}
                        className={`w-full px-4 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-offset-0 transition-colors ${
                          theme === 'dark' 
                            ? 'bg-black/50 border-green-500/30 text-white focus:ring-green-500/50 focus:border-green-500/50' 
                            : 'bg-white border-gray-300 text-gray-900 focus:ring-green-500 focus:border-green-500'
                        }`}
                        placeholder={i18n.language === 'he' ? 'הכנס את האימייל שלך' : 'Enter your email'}
                        required
                      />
                    </div>
                    
                    <div className="flex space-x-3">
                      <button
                        type="button"
                        onClick={closeForgotModal}
                        className={`flex-1 py-2 px-4 rounded-md border font-medium transition-colors ${
                          theme === 'dark' 
                            ? 'bg-gray-700 hover:bg-gray-600 text-gray-300 border-gray-600' 
                            : 'bg-gray-100 hover:bg-gray-200 text-gray-700 border-gray-300'
                        }`}
                      >
                        {i18n.language === 'he' ? 'ביטול' : 'Cancel'}
                      </button>
                      <button
                        type="submit"
                        disabled={resetEmailLoading}
                        className={`flex-1 py-2 px-4 rounded-md border font-medium transition-colors ${
                          theme === 'dark' 
                            ? 'bg-green-500/20 hover:bg-green-500/30 text-green-400 border-green-500/30' 
                            : 'bg-green-600 hover:bg-green-700 text-white border-green-600'
                        }`}
                      >
                        {resetEmailLoading ? (
                          <div className="flex space-x-1 justify-center">
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
                          i18n.language === 'he' ? 'שלח קישור איפוס' : 'Send Reset Link'
                        )}
                      </button>
                    </div>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default APEXStaticLogin; 