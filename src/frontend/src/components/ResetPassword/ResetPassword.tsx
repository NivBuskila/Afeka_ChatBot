import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { userService } from '../../services/userService';
import { useTranslation } from 'react-i18next';
import { Loader2 } from 'lucide-react';

const ResetPassword: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      setError(t('resetPassword.passwordsMismatch'));
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      await userService.updatePassword(newPassword);
      setSuccess(true);
      setTimeout(() => navigate('/'), 3000); // Redirect to login after 3 seconds
    } catch (err) {
      setError(t('resetPassword.updateError'));
      console.error('Error updating password:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-8">
        <h2 className="text-2xl font-bold mb-6 text-center text-green-400">
          {i18n.language === 'he' ? 'איפוס סיסמה' : 'Reset Password'}
        </h2>

        {success ? (
          <div className="text-center">
            <p className="text-green-400 mb-4">
              {i18n.language === 'he' ? 'הסיסמה עודכנה בהצלחה!' : 'Password updated successfully!'}
            </p>
            <p className="text-gray-400">
              {i18n.language === 'he' ? 'מעביר אותך לדף ההתחברות...' : 'Redirecting to login page...'}
            </p>
          </div>
        ) : (
          <form onSubmit={handleResetPassword}>
            {error && (
              <div className="mb-4 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-md text-sm">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label htmlFor="newPassword" className="block text-sm text-green-400/80 mb-1">
                  {i18n.language === 'he' ? 'סיסמה חדשה' : 'New Password'}
                </label>
                <input
                  id="newPassword"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-4 py-2 bg-black/50 border border-green-500/30 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-green-500/50 focus:border-green-500/50"
                  required
                  minLength={8}
                />
              </div>

              <div>
                <label htmlFor="confirmPassword" className="block text-sm text-green-400/80 mb-1">
                  {i18n.language === 'he' ? 'אימות סיסמה' : 'Confirm Password'}
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-4 py-2 bg-black/50 border border-green-500/30 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-green-500/50 focus:border-green-500/50"
                  required
                  minLength={8}
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 font-medium rounded-md border border-green-500/30 transition-colors flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    {i18n.language === 'he' ? 'מעדכן...' : 'Updating...'}
                  </>
                ) : (
                  (i18n.language === 'he' ? 'עדכן סיסמה' : 'Update Password')
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default ResetPassword; 