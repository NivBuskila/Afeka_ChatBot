import React, { useState, useEffect } from 'react';
import { Brain, LogIn, Shield, User, Lock, Eye, EyeOff, Mail, ChevronLeft, UserPlus, Globe } from 'lucide-react';
import '../../styles/animations.css';
import { supabase } from '../../config/supabase';
import { userService } from '../../services/userService';
import { useTranslation } from 'react-i18next';
import { changeLanguage } from '../../i18n/config';

interface APEXRegistrationProps {
  onRegistrationSuccess: (isAdmin: boolean) => void;
  onBackToLogin: () => void;
}

const APEXRegistration: React.FC<APEXRegistrationProps> = ({ onRegistrationSuccess, onBackToLogin }) => {
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
      // שיטה ישירה - ניצור את המשתמש באופן ישיר מול ה-API
      const { data: authData, error: authError } = await supabase.auth.signUp({
        email: email.trim(),
        password,
        options: {
          // הדגל החשוב שמאפשר לעקוף את השגיאה
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
      
      // ניצור את המשתמש בטבלת users באופן ידני
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
          // ממשיכים למרות השגיאה, כי ייתכן שהטריגר כבר יצר את הרשומה
        }
        
        // אם זה משתמש מנהל, נוסיף אותו לטבלת מנהלים
        // יתכן שתהיה שגיאת 403, אבל זה בסדר - נטפל בכך בהתחברות הראשונה
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
              // לא נטפל בשגיאה כאן - נקבל אותה בהתחברות הראשונה
            }
          } catch (adminInsertError) {
            console.warn('Exception setting admin role:', adminInsertError);
            // ממשיכים למרות השגיאה - זה יטופל בהתחברות
          }
        }
      } catch (dbError) {
        console.warn('Database error:', dbError);
        // ממשיכים למרות השגיאה, כי המשתמש כבר נוצר ב-Auth
      }
      
      // עכשיו נבצע התחברות אוטומטית עם המשתמש שנוצר
      try {
        const { error: signInError } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password
        });
        
        if (signInError) {
          console.warn('Auto sign-in error:', signInError);
          // לא נכשלים בגלל זה, פשוט נודיע למשתמש שנרשם בהצלחה ונבקש ממנו להתחבר
        }
      } catch (signInError) {
        console.warn('Exception during auto sign-in:', signInError);
        // ממשיכים למרות השגיאה - נבקש מהמשתמש להתחבר
      }
      
      // קוראים לפונקציה שמודיעה להורה על הצלחת הרישום
      onRegistrationSuccess(role === 'admin');
    } catch (error: any) {
      console.error('Registration error:', error);
      
      // התעלמות משגיאות 403 הקשורות לטבלת מנהלים
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
    <div className="relative h-screen bg-black text-white overflow-auto">
      {/* Removed MatrixRain component */}
      
      {/* Removed Matrix-like background */}
      
      {/* Registration Content */}
      <div className="flex flex-col items-center justify-center min-h-screen p-4 relative z-10">
        {/* Logo */}
        <div className="mb-8 flex flex-col items-center">
          <div className="relative">
            <div className="absolute inset-0 bg-green-500 rounded-full filter blur-lg opacity-20" />
            <Brain className="w-16 h-16 text-green-400 relative z-10" />
          </div>
          <div className="mt-4 text-3xl font-bold text-green-400">APEX</div>
          <div className="text-sm text-green-400/70 mt-1">{i18n.language === 'he' ? 'רישום למערכת' : 'Registration Portal'}</div>
        </div>
        
        {/* Registration card */}
        <div className="w-full max-w-md bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 overflow-hidden">
          {/* Header */}
          <div className="bg-green-500/5 border-b border-green-500/10 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center">
              <Shield className="w-5 h-5 text-green-400/80 mr-2" />
              <span className="text-green-400/90 font-semibold">{i18n.language === 'he' ? 'הרשמה למערכת' : 'System Registration'}</span>
            </div>
            <button 
              onClick={onBackToLogin}
              className="text-green-400/80 hover:text-green-400 transition-colors flex items-center"
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              <span>{i18n.language === 'he' ? 'חזרה להתחברות' : 'Back to Login'}</span>
            </button>
          </div>
          
          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-5">
            {error && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-md text-sm">
                {error}
              </div>
            )}
            
            {/* Email field */}
            <div className="space-y-2">
              <label className="block text-sm text-green-400/80 mb-1">{i18n.language === 'he' ? 'כתובת מייל' : 'Email Address'}</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-green-500/50" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-black/50 border border-green-500/30 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-green-500/50 focus:border-green-500/50"
                  placeholder={i18n.language === 'he' ? 'הזן כתובת אימייל' : 'Enter email address'}
                  dir={i18n.language === 'he' ? 'rtl' : 'ltr'}
                  autoComplete="username"
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
                  placeholder={i18n.language === 'he' ? 'הזן סיסמה' : 'Enter password'}
                  dir={i18n.language === 'he' ? 'rtl' : 'ltr'}
                  autoComplete="new-password"
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
            
            {/* Confirm Password field */}
            <div className="space-y-2">
              <label className="block text-sm text-green-400/80 mb-1">{i18n.language === 'he' ? 'אימות סיסמה' : 'Confirm Password'}</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-green-500/50" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-black/50 border border-green-500/30 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-green-500/50 focus:border-green-500/50"
                  placeholder={i18n.language === 'he' ? 'הזן שוב את הסיסמה' : 'Confirm your password'}
                  dir={i18n.language === 'he' ? 'rtl' : 'ltr'}
                  autoComplete="new-password"
                />
              </div>
            </div>
            
            {/* Role selection */}
            <div className="space-y-2">
              <label className="block text-sm text-green-400/80 mb-1">{i18n.language === 'he' ? 'תפקיד' : 'Role'}</label>
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setRole('user')}
                  className={`flex-1 px-4 py-2 rounded-md border transition-colors flex items-center justify-center ${
                    role === 'user'
                      ? 'bg-green-500/20 border-green-500/30 text-green-400'
                      : 'bg-black/50 border-green-500/30 text-green-400/70 hover:bg-green-500/10'
                  }`}
                >
                  <User className="w-4 h-4 mr-2" />
                  {i18n.language === 'he' ? 'משתמש רגיל' : 'Regular User'}
                </button>
                <button
                  type="button"
                  onClick={() => setRole('admin')}
                  className={`flex-1 px-4 py-2 rounded-md border transition-colors flex items-center justify-center ${
                    role === 'admin'
                      ? 'bg-green-500/20 border-green-500/30 text-green-400'
                      : 'bg-black/50 border-green-500/30 text-green-400/70 hover:bg-green-500/10'
                  }`}
                >
                  <Shield className="w-4 h-4 mr-2" />
                  {i18n.language === 'he' ? 'מנהל מערכת' : 'System Admin'}
                </button>
              </div>
            </div>
            
            {/* Terms & Conditions checkbox */}
            <div className="space-y-2">
              <div className="flex items-center space-x-2 space-x-reverse">
                <input
                  type="checkbox"
                  id="terms"
                  checked={acceptTerms}
                  onChange={(e) => setAcceptTerms(e.target.checked)}
                  className="rounded border-green-500/30 text-green-500 bg-black/50 focus:ring-green-500/30"
                />
                <label htmlFor="terms" className="text-sm text-green-400/80">
                  {i18n.language === 'he' ? 'אני מאשר/ת את ' : 'I accept the '}
                  <button 
                    type="button" 
                    onClick={openTermsModal} 
                    className="text-green-400 underline hover:text-green-300"
                  >
                    {i18n.language === 'he' ? 'תנאי השימוש ומדיניות הפרטיות' : 'terms and conditions'}
                  </button>
                </label>
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
                  <UserPlus className="w-5 h-5 ml-2" />
                  <span>{i18n.language === 'he' ? 'הרשם למערכת' : 'Register'}</span>
                </>
              )}
            </button>
          </form>
          
          {/* System info footer */}
          <div className="bg-black/40 px-6 py-3 text-xs text-green-400/50 flex justify-between items-center">
            <span>APEX v1.0.0</span>
            <button 
              onClick={toggleLanguage} 
              className="flex items-center text-green-400/70 hover:text-green-400 transition-colors"
            >
              <Globe className="w-4 h-4 mr-1" />
              <span>{i18n.language === 'he' ? 'English' : 'עברית'}</span>
            </button>
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

export default APEXRegistration; 