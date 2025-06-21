import React from "react";
import { useTranslation } from "react-i18next";
import { Sun, Moon, Globe } from "lucide-react";

type Language = "he" | "en";
type Theme = "light" | "dark";

interface SettingsPageProps {
  language: Language;
  theme: Theme;
  handleLanguageChange: (language: Language) => void;
  handleThemeChange: (theme: Theme) => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({
  language,
  theme,
  handleLanguageChange,
  handleThemeChange,
}) => {
  const { t } = useTranslation();

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-green-600 dark:text-green-400 mb-6">
        {t("admin.sidebar.settings")}
      </h2>
      <div className="bg-gray-100/30 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300/20 dark:border-green-500/20 p-6 space-y-8">
        {/* Theme Section */}
        <div className="space-y-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-green-50 dark:bg-green-900/20 flex items-center justify-center">
              {theme === "dark" ? (
                <Moon className="w-4 h-4 text-green-600 dark:text-green-400" />
              ) : (
                <Sun className="w-4 h-4 text-green-600 dark:text-green-400" />
              )}
            </div>
            <h3 className="text-lg font-semibold text-gray-800 dark:text-green-400">
              {t("settings.theme") || "Theme"}
            </h3>
          </div>

          <div className="relative">
            <div className="flex p-1 bg-gray-200/50 dark:bg-black/50 rounded-xl border border-gray-300/30 dark:border-green-500/30">
              <button
                onClick={() => handleThemeChange("light")}
                className={`flex-1 flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  theme === "light"
                    ? "bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/30"
                    : "text-gray-600 dark:text-green-400/70 hover:text-gray-800 dark:hover:text-green-400 hover:bg-gray-100/20 dark:hover:bg-green-500/10"
                }`}
              >
                <Sun className="w-4 h-4 mr-2" />
                {language === "he" ? "בהיר" : "Light"}
              </button>
              <button
                onClick={() => handleThemeChange("dark")}
                className={`flex-1 flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  theme === "dark"
                    ? "bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/30"
                    : "text-gray-600 dark:text-green-400/70 hover:text-gray-800 dark:hover:text-green-400 hover:bg-gray-100/20 dark:hover:bg-green-500/10"
                }`}
              >
                <Moon className="w-4 h-4 mr-2" />
                {language === "he" ? "כהה" : "Dark"}
              </button>
            </div>
          </div>
        </div>

        {/* Language Section */}
        <div className="space-y-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-green-50 dark:bg-green-900/20 flex items-center justify-center">
              <Globe className="w-4 h-4 text-green-600 dark:text-green-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-800 dark:text-green-400">
              {t("settings.language") || "Language"}
            </h3>
          </div>

          <div className="relative">
            <div className="flex p-1 bg-gray-200/50 dark:bg-black/50 rounded-xl border border-gray-300/30 dark:border-green-500/30">
              <button
                onClick={() => handleLanguageChange("he")}
                className={`flex-1 flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  language === "he"
                    ? "bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/30"
                    : "text-gray-600 dark:text-green-400/70 hover:text-gray-800 dark:hover:text-green-400 hover:bg-gray-100/20 dark:hover:bg-green-500/10"
                }`}
              >
                עברית
              </button>
              <button
                onClick={() => handleLanguageChange("en")}
                className={`flex-1 flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  language === "en"
                    ? "bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/30"
                    : "text-gray-600 dark:text-green-400/70 hover:text-gray-800 dark:hover:text-green-400 hover:bg-gray-100/20 dark:hover:bg-green-500/10"
                }`}
              >
                English
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 