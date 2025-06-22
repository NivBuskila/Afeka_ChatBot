import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { supabase } from '../../../config/supabase';

interface UseRegistrationProps {
  onRegistrationSuccess: (isAdmin: boolean) => void;
}

export function useRegistration({ onRegistrationSuccess }: UseRegistrationProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState<'user' | 'admin'>('user');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
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
      // Create user via Supabase Auth
      const { data: authData, error: authError } = await supabase.auth.signUp({
        email: email.trim(),
        password,
        options: {
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
      
      // Create user in users table
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
        }
        
        // If admin user, add to admins table
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
            }
          } catch (adminInsertError) {
            console.warn('Exception setting admin role:', adminInsertError);
          }
        }
      } catch (dbError) {
        console.warn('Database error:', dbError);
      }
      
      // Automatic login
      try {
        const { error: signInError } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password
        });
        
        if (signInError) {
          console.warn('Auto sign-in error:', signInError);
        }
      } catch (signInError) {
        console.warn('Exception during auto sign-in:', signInError);
      }
      
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

  return {
    email,
    setEmail,
    password,
    setPassword,
    confirmPassword,
    setConfirmPassword,
    role,
    setRole,
    showPassword,
    setShowPassword,
    isLoading,
    error,
    acceptTerms,
    setAcceptTerms,
    handleSubmit,
    openTermsModal,
  };
} 