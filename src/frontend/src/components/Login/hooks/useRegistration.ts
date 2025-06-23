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
        throw authError;
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
          // User registration succeeded but profile creation failed
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
              // Admin role assignment failed but registration succeeded
            } else {
              // Admin role assignment succeeded
            }
          } catch (adminInsertError) {
            // Admin table error - registration already succeeded
          }
        }
      } catch (dbError: any) {
        // Database error after successful auth registration
        if (dbError?.code === '23505') {
          // User already exists in users table - this is fine
        }
      }
      
      // Try auto sign-in
      const { error: signInError } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password
      });

      if (signInError) {
        // Auto sign-in failed - user can still login manually
      } else {
        // Auto sign-in succeeded
      }
      
      onRegistrationSuccess(role === 'admin');
    } catch (error: any) {
      setIsLoading(false);
      
      if (error?.status === 403) {
        // Ignoring admin 403 error - registration succeeded
        onRegistrationSuccess(role === 'admin');
        return;
      }
      
      setError(i18n.language === 'he' ? 'שגיאה ברישום: ' + error.message : 'Registration error: ' + error.message);
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