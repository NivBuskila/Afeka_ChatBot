import React, { useState, useEffect, useRef } from 'react';
import { Brain, LogIn, Shield, User, Lock, Eye, EyeOff } from 'lucide-react';
import './APEXStaticLogin.css';
import { supabase } from '../../config/supabase';
import { useTranslation } from 'react-i18next';

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
  const { t, i18n } = useTranslation();
  
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
    
    // אימות דרך Supabase
    setTimeout(async () => {
      try {
        // התחברות לסופאבייס עם האימייל והסיסמה שהמשתמש הזין
        const { data, error } = await supabase.auth.signInWithPassword({
          email: username.trim(), // משתמשים בשדה username כדוא"ל
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
        
        // מאחר ויש בעיות RLS, נבדוק את רולי המשתמש מהמטא-דאטה של המשתמש
        const userRole = data.user.user_metadata?.role || 'user';
        const isAdmin = userRole === 'admin';
        
        try {
          // ננסה לקבל מידע מטבלת users, אבל אם יש שגיאה נמשיך עם המטא-דאטה
          const { data: userData, error: userError } = await supabase
            .from('users')
            .select('role')
            .eq('id', data.user.id)
            .single();
          
          if (userError) {
            console.error('Error fetching user role from DB, using metadata instead:', userError);
          } else if (userData) {
            console.log('User role from DB:', userData.role);
            onLoginSuccess(userData.role === 'admin');
            return;
          }
        } catch (dbError) {
          console.error('Database query error:', dbError);
        }
        
        // אם הגענו לכאן, נשתמש במטא-דאטה
        console.log('Using role from user metadata:', userRole);
        onLoginSuccess(isAdmin);
        
      } catch (err) {
        console.error('Authentication error:', err);
        setError('אירעה שגיאה בהתחברות לשרת');
        setIsLoading(false);
      }
    }, 500);
  };

  return (
    <div className="relative h-screen bg-black text-white overflow-hidden">
      {/* Login Content */}
      <div className="flex flex-col items-center justify-center min-h-screen p-4 relative z-10">
        {/* Logo */}
        <div className="mb-8 flex flex-col items-center">
          <div className="relative">
            <div className="absolute inset-0 bg-green-500 rounded-full filter blur-lg opacity-20" />
            <Brain className="w-16 h-16 text-green-400 relative z-10" />
          </div>
          <div className="mt-4 text-3xl font-bold text-green-400">APEX</div>
          <div className="text-sm text-green-400/70 mt-1">{i18n.language === 'he' ? 'פורטל כניסה' : 'Authentication Portal'}</div>
        </div>
        
        {/* Login card */}
        <div className="w-full max-w-md bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 overflow-hidden">
          {/* Header */}
          <div className="bg-green-500/5 border-b border-green-500/10 px-6 py-4 flex items-center">
            <Shield className="w-5 h-5 text-green-400/80 mr-2" />
            <span className="text-green-400/90 font-semibold">{i18n.language === 'he' ? 'כניסה מאובטחת' : 'Secure Login'}</span>
          </div>
          
          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-5">
            {error && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-md text-sm">
                {error}
              </div>
            )}
            
            {/* Username field */}
            <div className="space-y-2">
              <label className="block text-sm text-green-400/80 mb-1">{i18n.language === 'he' ? 'שם משתמש' : 'Username'}</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-green-500/50" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-black/50 border border-green-500/30 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-green-500/50 focus:border-green-500/50"
                  placeholder={i18n.language === 'he' ? 'הכנס שם משתמש' : 'Enter your username'}
                />
              </div>
            </div>
            
            {/* Password field */}
            <div className="space-y-2">
              <label className="block text-sm text-green-400/80 mb-1">{i18n.language === 'he' ? 'סיסמה' : 'Password'}</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-green-500/50" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-10 py-2 bg-black/50 border border-green-500/30 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-green-500/50 focus:border-green-500/50"
                  placeholder={i18n.language === 'he' ? 'הכנס סיסמה' : 'Enter your password'}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-green-500/50" />
                  ) : (
                    <Eye className="h-5 w-5 text-green-500/50" />
                  )}
                </button>
              </div>
            </div>
            
            {/* Submit button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-green-500/20 hover:bg-green-500/30 text-green-400 font-medium py-2 px-4 rounded-md border border-green-500/30 transition-colors flex items-center justify-center space-x-2"
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
                <>
                  <LogIn className="w-5 h-5" />
                  <span>{i18n.language === 'he' ? 'כניסה למערכת' : 'Login to APEX'}</span>
                </>
              )}
            </button>
            
            {/* Recovery link */}
            <div className="text-center mt-4">
              <div className="flex flex-col space-y-2">
                <a href="#" className="text-green-400/60 hover:text-green-400/80 text-sm transition-colors">
                  {i18n.language === 'he' ? 'שכחת פרטי התחברות? פנה למנהל המערכת' : 'Forgot login details? Contact system admin'}
                </a>
                <button 
                  type="button"
                  onClick={onRegisterClick}
                  className="text-green-400/70 hover:text-green-400 text-sm transition-colors font-medium"
                >
                  {i18n.language === 'he' ? 'אין לך חשבון? הירשם עכשיו' : "Don't have an account? Register now"}
                </button>
              </div>
            </div>
          </form>
          
          {/* System info footer */}
          <div className="bg-black/40 px-6 py-3 text-xs text-green-400/50 flex justify-between">
            <span>APEX v3.5.2</span>
          </div>
        </div>
      </div>
      
      {/* Ambient light effects */}
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-green-500 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob" />
        <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-green-700 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob animation-delay-2000" />
      </div>
    </div>
  );
};

export default APEXStaticLogin; 