import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { userService } from "../../services/userService";
import { useTranslation } from "react-i18next";
import { Loader2, Globe, Brain, Shield } from "lucide-react";
import { changeLanguage } from "../../i18n/config";

const ResetPassword: React.FC = () => {
  const { t, i18n } = useTranslation();
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
    <div className="relative h-screen bg-black text-white overflow-hidden">
      {/* Reset Password Content */}
      <div className="flex flex-col items-center justify-center min-h-screen p-4 relative z-10">
        {/* Logo */}
        <div className="mb-8 flex flex-col items-center">
          <div className="relative">
            <div className="absolute inset-0 bg-green-500 rounded-full filter blur-lg opacity-20" />
            <Brain className="w-16 h-16 text-green-400 relative z-10" />
          </div>
          <div className="mt-4 text-3xl font-bold text-green-400">APEX</div>
          <div className="text-sm text-green-400/70 mt-1">
            {i18n.language === "he" ? "פורטל כניסה" : "Authentication Portal"}
          </div>
        </div>

        {/* Reset Password card */}
        <div className="w-full max-w-md bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 overflow-hidden">
          {/* Header */}
          <div className="bg-green-500/5 border-b border-green-500/10 px-6 py-4 flex items-center">
            <Shield className="w-5 h-5 text-green-400/80 mr-2" />
            <span className="text-green-400/90 font-semibold">
              {i18n.language === "he" ? "איפוס סיסמה" : "Reset Password"}
            </span>
          </div>

          {/* Form Content */}
          <div className="p-6">
            {success ? (
              <div className="text-center">
                <p className="text-green-400 mb-4">
                  {i18n.language === "he"
                    ? "הסיסמה עודכנה בהצלחה!"
                    : "Password updated successfully!"}
                </p>
                <p className="text-gray-400">
                  {i18n.language === "he"
                    ? "מעביר אותך לדף ההתחברות..."
                    : "Redirecting to login page..."}
                </p>
              </div>
            ) : (
              <form onSubmit={handleResetPassword} className="space-y-5">
                {error && (
                  <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-md text-sm">
                    {error}
                  </div>
                )}

                <div className="space-y-4">
                  <div>
                    <label
                      htmlFor="newPassword"
                      className="block text-sm text-green-400/80 mb-1"
                    >
                      {i18n.language === "he" ? "סיסמה חדשה" : "New Password"}
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
                    <label
                      htmlFor="confirmPassword"
                      className="block text-sm text-green-400/80 mb-1"
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
                      className="w-full px-4 py-2 bg-black/50 border border-green-500/30 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-green-500/50 focus:border-green-500/50"
                      required
                      minLength={8}
                    />
                  </div>

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
          <div className="bg-black/40 px-6 py-3 text-xs text-green-400/50 flex justify-between items-center">
            <span>APEX v1.0.0</span>
            <button
              onClick={toggleLanguage}
              className="flex items-center text-green-400/70 hover:text-green-400 transition-colors"
            >
              <Globe className="w-4 h-4 mr-1" />
              <span>{i18n.language === "he" ? "English" : "עברית"}</span>
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

export default ResetPassword;
