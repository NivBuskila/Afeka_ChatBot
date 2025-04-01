import React, { useState, useEffect, useRef } from 'react';
import { Brain, LogIn, Shield, User, Lock, Eye, EyeOff, Mail, ChevronLeft, UserPlus, Globe } from 'lucide-react';
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
  
  // Matrix Rain effect (זהה לזה שבלוגין)
  const MatrixRain = () => {
    const canvas = useRef<HTMLCanvasElement>(null);
    
    useEffect(() => {
      let canvasElement = canvas.current;
      
      // נחכה טיפה אחרי הרנדור כדי לוודא שה-canvas קיים
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
      }, 100); // קצת השהייה לאפשר לרנדר להשלים
      
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // בדיקת תקינות שדות
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
    
    setTimeout(async () => {
      try {
        // שימוש בפונקציה המורחבת עם הפרדה בין משתמשים ומנהלים
        const result = await userService.signUp(
          email.trim(),
          password,
          role === 'admin'
        );
        
        console.log('Registration successful:', result);
        onRegistrationSuccess(role === 'admin');
      } catch (error) {
        console.error('Registration error:', error);
        setError(i18n.language === 'he' ? 'ההרשמה נכשלה: ' + (error as Error).message : 'Registration failed: ' + (error as Error).message);
        setIsLoading(false);
      }
    }, 500);
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
      <MatrixRain />
      
      {/* Matrix-like background */}
      <div className="absolute inset-0 opacity-20">
        {[...Array(50)].map((_, i) => (
          <div
            key={i}
            className="absolute text-green-500 text-opacity-20 animate-matrix"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              fontSize: `${Math.random() * 10 + 10}px`
            }}
          >
            01
          </div>
        ))}
      </div>
      
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