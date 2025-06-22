import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { supabase } from '../../../config/supabase';

interface UseLoginProps {
  onLoginSuccess: (isAdmin: boolean) => void;
}

export function useLogin({ onLoginSuccess }: UseLoginProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { i18n } = useTranslation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Validate fields
    if (!username.trim() || !password.trim()) {
      setError(i18n.language === 'he' ? 'נא להזין שם משתמש וסיסמה' : 'Please enter both username and password');
      return;
    }
    
    setIsLoading(true);
    
    // Authentication via Supabase
    setTimeout(async () => {
      try {
        const { data, error } = await supabase.auth.signInWithPassword({
          email: username.trim(),
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
        
        // Check if user is admin
        try {
          try {
            const { data: adminData, error: adminError } = await supabase
              .from('admins')
              .select('*')
              .eq('user_id', data.user.id)
              .maybeSingle();
            
            if (!adminError && adminData) {
              onLoginSuccess(true);
              return;
            }
          } catch (dbError) {
            console.error('שגיאת גישה לטבלת מנהלים:', dbError);
          }
          
          try {
            const { data: isAdminResult, error: isAdminError } = await supabase
              .rpc('is_admin', { user_id: data.user.id });
            
            if (isAdminError) {
              console.error('שגיאה בקריאת is_admin RPC:', isAdminError);
            } else if (isAdminResult === true) {
              onLoginSuccess(true);
              return;
            }
          } catch (rpcError) {
            console.error('שגיאה בקריאת RPC:', rpcError);
          }
          
          const isAdminFromMetadata = data.user.user_metadata?.role === 'admin';
          onLoginSuccess(isAdminFromMetadata || false);
          
        } catch (err) {
          console.error('שגיאה בבדיקת מנהל:', err);
          onLoginSuccess(false);
        }
        
      } catch (err) {
        console.error('Authentication error:', err);
        setError('אירעה שגיאה בהתחברות לשרת');
        setIsLoading(false);
      }
    }, 500);
  };

  return {
    username,
    setUsername,
    password,
    setPassword,
    showPassword,
    setShowPassword,
    isLoading,
    error,
    handleSubmit,
  };
} 