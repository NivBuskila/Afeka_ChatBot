import React, { useState, useEffect, useRef } from 'react';
import { Brain, LogIn, Shield, User, Lock, Eye, EyeOff, Mail, ChevronLeft, UserPlus } from 'lucide-react';
import { supabase } from '../../config/supabase';

interface APEXRegistrationProps {
  onRegistrationSuccess: () => void;
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
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // בדיקת תקינות שדות
    if (!email.trim()) {
      setError('נא להזין כתובת אימייל');
      return;
    }
    
    if (!password.trim()) {
      setError('נא להזין סיסמה');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('הסיסמאות אינן תואמות');
      return;
    }
    
    setIsLoading(true);
    console.log("תהליך רישום: התחלת תהליך");
    
    try {
      // רישום המשתמש במערכת האימות של סופאבייס
      console.log("תהליך רישום: רושם משתמש במערכת האימות");
      const { data: authData, error: authError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            role: role // שומרים את התפקיד גם במטא-דאטה של המשתמש
          }
        }
      });
      
      if (authError) {
        console.error('Authentication error:', authError);
        setError('שגיאה ברישום: ' + authError.message);
        setIsLoading(false);
        return;
      }
      
      if (!authData.user) {
        setError('שגיאה ברישום המשתמש');
        setIsLoading(false);
        return;
      }
      
      console.log('תהליך רישום: רישום במערכת האימות הצליח', authData.user);
      
      // רישום מכאן הצליח, עכשיו אנחנו מתחברים כדי להוסיף/לעדכן את הרשומה בטבלת המשתמשים
      console.log("תהליך רישום: מתחבר כמשתמש החדש");
      const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
        email,
        password
      });
      
      if (signInError) {
        console.error('Error signing in as new user:', signInError);
        setError('נרשמת בהצלחה, אך אירעה שגיאה בכניסה למערכת. נסה להתחבר ידנית.');
        setIsLoading(false);
        onRegistrationSuccess();
        return;
      }
      
      console.log("תהליך רישום: התחברות הצליחה", signInData);
      
      // כעת נבדוק את הסשן הנוכחי כדי לוודא שהמשתמש אכן מחובר
      const { data: sessionData } = await supabase.auth.getSession();
      console.log("תהליך רישום: מידע על הסשן הנוכחי", sessionData);
      
      // כעת שהמשתמש מחובר, ננסה להוסיף או לעדכן את הרשומה בטבלת המשתמשים
      console.log("תהליך רישום: מעדכן את טבלת המשתמשים");
      const { data: upsertData, error: upsertError } = await supabase
        .from('users')
        .upsert({
          id: authData.user.id,
          email: email,
          role: role
        }, { onConflict: 'id' });
      
      if (upsertError) {
        console.error('Error upserting user record:', upsertError);
        console.log("תהליך רישום: שגיאה בעדכון טבלת המשתמשים:", upsertError.message);
        // לא נציג שגיאה למשתמש, כי המשתמש נוצר בהצלחה במערכת האימות
      } else {
        console.log('תהליך רישום: עדכון טבלת המשתמשים הצליח:', upsertData);
      }
      
      // בדיקה אם הרשומה נוצרה בהצלחה
      console.log("תהליך רישום: בודק אם הרשומה נוצרה בהצלחה");
      const { data: checkData, error: checkError } = await supabase
        .from('users')
        .select('*')
        .eq('id', authData.user.id)
        .single();
        
      if (checkError) {
        console.error("תהליך רישום: שגיאה בבדיקת הרשומה:", checkError);
      } else {
        console.log("תהליך רישום: הרשומה נוצרה בהצלחה:", checkData);
      }
      
      // מתנתקים מהמשתמש החדש כדי שהוא יוכל להתחבר מחדש דרך מסך הלוגין
      console.log("תהליך רישום: מתנתק מהמשתמש");
      await supabase.auth.signOut();
      
      // הרישום הצליח
      setIsLoading(false);
      console.log("תהליך רישום: הרישום הסתיים בהצלחה");
      onRegistrationSuccess();
      
    } catch (error) {
      console.error('Registration error:', error);
      setError('אירעה שגיאה בתהליך הרישום');
      setIsLoading(false);
    }
  };

  return (
    <div className="relative h-screen bg-black text-white overflow-hidden">
      {/* Registration Content */}
      <div className="flex flex-col items-center justify-center min-h-screen p-4 relative z-10">
        {/* Logo */}
        <div className="mb-8 flex flex-col items-center">
          <div className="relative">
            <div className="absolute inset-0 bg-green-500 rounded-full filter blur-lg opacity-20" />
            <Brain className="w-16 h-16 text-green-400 relative z-10" />
          </div>
          <div className="mt-4 text-3xl font-bold text-green-400">APEX</div>
          <div className="text-sm text-green-400/70 mt-1">רישום למערכת</div>
        </div>
        
        {/* Registration card */}
        <div className="w-full max-w-md bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 overflow-hidden">
          {/* Header */}
          <div className="bg-green-500/5 border-b border-green-500/10 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center">
              <Shield className="w-5 h-5 text-green-400/80 mr-2" />
              <span className="text-green-400/90 font-semibold">הרשמה למערכת</span>
            </div>
            <button 
              onClick={onBackToLogin}
              className="text-green-400/80 hover:text-green-400 transition-colors flex items-center"
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              <span>חזרה להתחברות</span>
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
              <label className="block text-sm text-green-400/80 mb-1">כתובת מייל</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-green-500/50" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-black/50 border border-green-500/30 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-green-500/50 focus:border-green-500/50"
                  placeholder="הזן כתובת אימייל"
                  dir="rtl"
                />
              </div>
            </div>
            
            {/* Password field */}
            <div className="space-y-2">
              <label className="block text-sm text-green-400/80 mb-1">סיסמה</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-green-500/50" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-10 py-2 bg-black/50 border border-green-500/30 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-green-500/50 focus:border-green-500/50"
                  placeholder="הזן סיסמה"
                  dir="rtl"
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
              <label className="block text-sm text-green-400/80 mb-1">אימות סיסמה</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-green-500/50" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-black/50 border border-green-500/30 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-green-500/50 focus:border-green-500/50"
                  placeholder="הזן שוב את הסיסמה"
                  dir="rtl"
                />
              </div>
            </div>
            
            {/* Role selection */}
            <div className="space-y-2">
              <label className="block text-sm text-green-400/80 mb-1">תפקיד</label>
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
                  משתמש רגיל
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
                  מנהל מערכת
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
                  <UserPlus className="w-5 h-5 ml-2" />
                  <span>הרשם למערכת</span>
                </>
              )}
            </button>
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

export default APEXRegistration; 