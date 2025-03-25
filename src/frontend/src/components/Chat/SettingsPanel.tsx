import React from 'react';
import { Settings, Moon, Sun } from 'lucide-react';

interface SettingsPanelProps {
  onClose: () => void;
  theme: 'dark' | 'light';
  setTheme: React.Dispatch<React.SetStateAction<'dark' | 'light'>>;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({
  onClose,
  theme,
  setTheme,
}) => {
  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  return (
    <div className="absolute inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center">
      <div className="bg-white dark:bg-black text-gray-900 dark:text-white p-5 rounded-2xl w-80 relative shadow-2xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
        >
          ×
        </button>
        <div className="flex items-center gap-2 mb-6">
          <Settings className="w-5 h-5 text-green-500" />
          <h2 className="text-xl font-semibold">Settings</h2>
        </div>

        {/* Dark/Light Toggle */}
        <div className="flex items-center justify-between py-2">
          <div className="flex items-center gap-2">
            {theme === 'dark' ? (
              <Moon className="w-5 h-5 text-green-500" />
            ) : (
              <Sun className="w-5 h-5 text-green-500" />
            )}
            <span className="text-base">Dark Mode</span>
          </div>
          <button
            onClick={toggleTheme}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-300 focus:outline-none ${
              theme === 'dark' ? 'bg-green-500' : 'bg-gray-200 dark:bg-gray-600'
            }`}
          >
            <span
              className={`inline-block h-5 w-5 transform rounded-full bg-white shadow-md transition-transform duration-300 ${
                theme === 'dark' ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Save Button */}
        <div className="mt-6">
          <button
            onClick={onClose}
            className="w-full bg-green-500 hover:bg-green-600 text-white py-2 rounded-lg font-medium transition-colors"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;
