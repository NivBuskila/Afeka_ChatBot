import React, { useState } from 'react';
import { Mail, Lock, AlertCircle, Loader2, X } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { userService } from '../../services/userService';
import { supabase } from '../../config/supabase';

interface UserSettingsProps {
  onClose: () => void;
}

const UserSettings: React.FC<UserSettingsProps> = ({ onClose }) => {
  const { t } = useTranslation();
  const [newEmail, setNewEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleUpdateEmail = async () => {
    try {
      setIsLoading(true);
      setError(null);
      await userService.updateEmail(newEmail);
      setSuccessMessage(t('settings.emailUpdateSuccess'));
      setNewEmail('');
    } catch (err) {
      setError(t('settings.emailUpdateError'));
      console.error('Error updating email:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const user = await supabase.auth.getUser();
      if (user.data.user?.email) {
        await userService.resetPassword(user.data.user.email);
        setSuccessMessage(t('settings.passwordResetEmailSent'));
      }
    } catch (err) {
      setError(t('settings.passwordResetError'));
      console.error('Error resetting password:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      setIsLoading(true);
      setError(null);
      await userService.signInWithGoogle();
    } catch (err) {
      setError(t('settings.googleSignInError'));
      console.error('Error signing in with Google:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl p-6 w-full max-w-md relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
        >
          <X className="w-5 h-5" />
        </button>

        <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
          {t('settings.userSettings')}
        </h2>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-200 text-red-700 rounded-lg flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        )}

        {/* Success Message */}
        {successMessage && (
          <div className="mb-4 p-3 bg-green-100 border border-green-200 text-green-700 rounded-lg flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Email Update Section */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-white">
            {t('settings.changeEmail')}
          </h3>
          <div className="flex gap-2">
            <div className="flex-1">
              <input
                type="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                placeholder={t('settings.newEmailPlaceholder')}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              />
            </div>
            <button
              onClick={handleUpdateEmail}
              disabled={isLoading || !newEmail}
              className="px-4 py-2 bg-green-500 hover:bg-green-600 disabled:bg-green-300 text-white rounded-lg flex items-center gap-2"
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Mail className="w-5 h-5" />}
              {t('settings.update')}
            </button>
          </div>
        </div>

        {/* Password Reset Section */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-white">
            {t('settings.resetPassword')}
          </h3>
          <button
            onClick={handleResetPassword}
            disabled={isLoading}
            className="w-full px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white rounded-lg flex items-center justify-center gap-2"
          >
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Lock className="w-5 h-5" />}
            {t('settings.sendResetLink')}
          </button>
        </div>

        {/* Google Sign-In Section */}
        <div>
          <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-white">
            {t('settings.connectGoogle')}
          </h3>
          <button
            onClick={handleGoogleSignIn}
            disabled={isLoading}
            className="w-full px-4 py-2 bg-white hover:bg-gray-50 disabled:bg-gray-100 text-gray-900 border border-gray-300 rounded-lg flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <img src="/google-icon.svg" alt="Google" className="w-5 h-5" />
            )}
            {t('settings.signInWithGoogle')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserSettings; 