import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { supabase } from '../../../config/supabase';

interface UseLoginAuthProps {
  onLoginSuccess: (isAdmin: boolean) => void;
}

export function useLoginAuth({ onLoginSuccess }: UseLoginAuthProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { i18n } = useTranslation();

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
        
        // Check if user is admin
        try {
          // First try direct access to admins table
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
            // Silent fail
          }
          
          // If direct access failed, try using RPC
          try {
            const { data: isAdminResult, error: isAdminError } = await supabase
              .rpc('is_admin', { user_id: data.user.id });
            
            if (isAdminError) {
              // Silent fail
            } else if (isAdminResult === true) {
              onLoginSuccess(true);
              return;
            }
          } catch (rpcError) {
            // Silent fail
          }
          
          // If we got here, try reading from user metadata
          const isAdminFromMetadata = data.user.user_metadata?.role === 'admin';
          
          // Final decision on role
          onLoginSuccess(isAdminFromMetadata || false);
          
        } catch (err) {
          // Silent fail
        }
        
      } catch (err) {
        // Silent fail
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
    setError,
    handleSubmit,
  };
} 