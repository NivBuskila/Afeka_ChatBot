import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { userService } from "../../services/userService";
import { useTranslation } from "react-i18next";
import { Loader2, Globe, Brain, Shield } from "lucide-react";
import { changeLanguage } from "../../i18n/config";
import { useTheme } from '../../contexts/ThemeContext'; 

const ResetPassword: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { theme } = useTheme();
  const navigate = useNavigate();
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      setError(t("resetPassword.passwordsMismatch"));
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      await userService.updatePassword(newPassword);
      setSuccess(true);
      setTimeout(() => navigate("/"), 3000); // Redirect to login after 3 seconds
    } catch (err) {
      setError(t("resetPassword.updateError"));
      console.error("Error updating password:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleLanguage = () => {
    const newLang = i18n.language === "he" ? "en" : "he";
    changeLanguage(newLang);
  };

  return (
    <div className={`relative min-h-screen overflow-auto ${
      theme === 'dark' 
        ? 'bg-black text-white' 
        : 'bg-gradient-to-br from-gray-50 to-gray-100 text-gray-900'
    }`}>
      {/* Reset Password Content */}
      <div className="flex flex-col items-center justify-center min-h-screen p-4 relative z-10">
        {/* Logo */}
        <div className="mb-8 flex flex-col items-center">
          <div className="relative">
            <div className={`absolute inset-0 rounded-full filter blur-lg opacity-20 ${
              theme === 'dark' ? 'bg-green-500' : 'bg-green-600'
            }`} />
            <Brain className={`w-16 h-16 relative z-10 ${
              theme === 'dark' ? 'text-green-400' : 'text-green-600'
            }`} />
          </div>
          <div className={`mt-4 text-3xl font-bold ${
            theme === 'dark' ? 'text-green-400' : 'text-green-600'
          }`}>APEX</div>
          <div className={`text-sm mt-1 ${
            theme === 'dark' ? 'text-green-400/70' : 'text-green-600/80'
          }`}>
            {i18n.language === "he" ? "פורטל כניסה" : "Authentication Portal"}
          </div>
        </div>

        {/* Reset Password card */}
        <div className={`w-full max-w-md rounded-lg border overflow-hidden shadow-xl ${
          theme === 'dark' 
            ? 'bg-black/30 backdrop-blur-lg border-green-500/20' 
            : 'bg-white/95 backdrop-blur-lg border-gray-200 shadow-lg'
        }`}>
          {/* Header */}
          <div className={`px-6 py-4 flex items-center border-b ${
            theme === 'dark' 
              ? 'bg-green-500/5 border-green-500/10' 
              : 'bg-green-50 border-gray-200'
          }`}>
            <Shield className={`w-5 h-5 mr-2 ${
              theme === 'dark' ? 'text-green-400/80' : 'text-green-600'
            }`} />
            <span className={`font-semibold ${
              theme === 'dark' ? 'text-green-400/90' : 'text-green-700'
            }`}>
              {i18n.language === "he" ? "איפוס סיסמה" : "Reset Password"}
            </span>
          </div>

          {/* Form Content */}
          <div className="p-6">
            {success ? (
              <div className="text-center">
                <p className={`mb-4 ${
                  theme === 'dark' ? 'text-green-400' : 'text-green-600'
                }`}>
                  {i18n.language === "he"
                    ? "הסיסמה עודכנה בהצלחה!"
                    : "Password updated successfully!"}
                </p>
                <p className={`${
                  theme === 'dark' ? 'text-gray-400' : 'text-gray-600'
                }`}>
                  {i18n.language === "he"
                    ? "מעביר אותך לדף ההתחברות..."
                    : "Redirecting to login page..."}
                </p>
              </div>
            ) : (
              <form onSubmit={handleResetPassword} className="space-y-5">
                {error && (
                  <div className={`border px-4 py-3 rounded-md text-sm ${
                    theme === 'dark' 
                      ? 'bg-red-500/10 border-red-500/30 text-red-400' 
                      : 'bg-red-50 border-red-300 text-red-700'
                  }`}>
                    {error}
                  </div>
                )}

                <div className="space-y-4">
                  <div>
                    <label
                      htmlFor="newPassword"
                      className={`block text-sm mb-1 ${
                        theme === 'dark' ? 'text-green-400/80' : 'text-gray-700 font-medium'
                      }`}
                    >
                      {i18n.language === "he" ? "סיסמה חדשה" : "New Password"}
                    </label>
                    <input
                      id="newPassword"
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className={`w-full px-4 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-offset-0 transition-colors ${
                        theme === 'dark' 
                          ? 'bg-black/50 border-green-500/30 text-white focus:ring-green-500/50 focus:border-green-500/50' 
                          : 'bg-white border-gray-300 text-gray-900 focus:ring-green-500 focus:border-green-500'
                      }`}
                      required
                      minLength={8}
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="confirmPassword"
                      className={`block text-sm mb-1 ${
                        theme === 'dark' ? 'text-green-400/80' : 'text-gray-700 font-medium'
                      }`}
                    >
                      {i18n.language === "he"
                        ? "אימות סיסמה"
                        : "Confirm Password"}
                    </label>
                    <input
                      id="confirmPassword"
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className={`w-full px-4 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-offset-0 transition-colors ${
                        theme === 'dark' 
                          ? 'bg-black/50 border-green-500/30 text-white focus:ring-green-500/50 focus:border-green-500/50' 
                          : 'bg-white border-gray-300 text-gray-900 focus:ring-green-500 focus:border-green-500'
                      }`}
                      required
                      minLength={8}
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading}
                    className={`w-full font-medium py-3 px-4 rounded-md border transition-colors flex items-center justify-center space-x-2 ${
                      theme === 'dark' 
                        ? 'bg-green-500/20 hover:bg-green-500/30 text-green-400 border-green-500/30' 
                        : 'bg-green-600 hover:bg-green-700 text-white border-green-600 shadow-md hover:shadow-lg'
                    }`}
                  >
                    {isLoading ? (
                      <div className="flex space-x-1">
                        {[...Array(3)].map((_, i) => (
                          <div
                            key={i}
                            className={`w-1 h-1 rounded-full animate-bounce ${
                              theme === 'dark' ? 'bg-green-400' : 'bg-white'
                            }`}
                            style={{ animationDelay: `${i * 0.2}s` }}
                          />
                        ))}
                      </div>
                    ) : (
                      <span>
                        {i18n.language === "he"
                          ? "עדכן סיסמה"
                          : "Update Password"}
                      </span>
                    )}
                  </button>
                </div>
              </form>
            )}
          </div>

          {/* System info footer */}
          <div className={`px-6 py-3 text-xs flex justify-between items-center ${
            theme === 'dark' 
              ? 'bg-black/40 text-green-400/50' 
              : 'bg-gray-50 text-gray-500'
          }`}>
            <span>APEX v1.0.0</span>
            <button
              onClick={toggleLanguage}
              className={`flex items-center transition-colors ${
                theme === 'dark' 
                  ? 'text-green-400/70 hover:text-green-400' 
                  : 'text-gray-600 hover:text-gray-700'
              }`}
            >
              <Globe className="w-4 h-4 mr-1" />
              <span>{i18n.language === "he" ? "English" : "עברית"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Background effects */}
      {theme === 'light' && (
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
          <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-green-200 rounded-full mix-blend-multiply filter blur-[128px] opacity-20 animate-blob" />
          <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-green-300 rounded-full mix-blend-multiply filter blur-[128px] opacity-15 animate-blob animation-delay-2000" />
        </div>
      )}

      {theme === 'dark' && (
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
          <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-green-500 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob" />
          <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-green-700 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob animation-delay-2000" />
        </div>
      )}
    </div>
  );
};

export default ResetPassword;
