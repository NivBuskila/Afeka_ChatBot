import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { supabase } from '../../../config/supabase';

export function usePasswordReset() {
  const [forgotEmail, setForgotEmail] = useState('');
  const [showForgotModal, setShowForgotModal] = useState(false);
  const [resetEmailSent, setResetEmailSent] = useState(false);
  const [resetEmailLoading, setResetEmailLoading] = useState(false);
  const [error, setError] = useState('');
  const { i18n } = useTranslation();

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

  const openForgotModal = () => {
    setShowForgotModal(true);
    setError('');
  };

  return {
    forgotEmail,
    setForgotEmail,
    showForgotModal,
    resetEmailSent,
    resetEmailLoading,
    error,
    setError,
    handleForgotPassword,
    closeForgotModal,
    openForgotModal,
  };
} 