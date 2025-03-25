import React from 'react';
import { Settings, Monitor, Moon, Sun } from 'lucide-react';

interface SettingsPanelProps {
  onClose: () => void;
  theme: 'dark' | 'light';
  setTheme: React.Dispatch<React.SetStateAction<'dark' | 'light'>>;
  fontSize: number;
  setFontSize: React.Dispatch<React.SetStateAction<number>>;
  animations: string;
  setAnimations: React.Dispatch<React.SetStateAction<string>>;
  contrast: string;
  setContrast: React.Dispatch<React.SetStateAction<string>>;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({
  onClose,
  theme,
  setTheme,
  fontSize,
  setFontSize,
  animations,
  setAnimations,
  contrast,
  setContrast,
}) => {
  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  return (
    <div className="absolute inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center">
      <div className="bg-gray-800 dark:bg-gray-700 text-white p-6 rounded-md w-96 relative">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-300 hover:text-gray-100"
        >
          ✕
        </button>
        <h2 className="text-xl mb-4 flex items-center gap-2">
          <Settings className="w-5 h-5 text-green-400/80" />
          <span>Settings</span>
        </h2>

        {/* Dark/Light Toggle */}
        <div className="mb-4 flex items-center justify-between">
          <span className="flex items-center gap-2">
            {theme === 'dark' ? (
              <Moon className="w-4 h-4 text-green-400" />
            ) : (
              <Sun className="w-4 h-4 text-green-400" />
            )}
            Dark Mode
          </span>
          <label className="inline-flex relative items-center cursor-pointer">
            <input
              type="checkbox"
              className="sr-only peer"
              checked={theme === 'dark'}
              onChange={toggleTheme}
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-green-500 rounded-full peer dark:bg-gray-600 peer-checked:bg-green-500 relative transition-colors">
              <span className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transform transition-transform peer-checked:translate-x-5" />
            </div>
          </label>
        </div>

        {/* Font Size */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm">Font Size</span>
            <span className="text-xs bg-black/30 dark:bg-gray-600 py-1 px-2 rounded border border-green-500/20">
              {fontSize}px
            </span>
          </div>
          <input
            type="range"
            min={10}
            max={20}
            value={fontSize}
            onChange={(e) => setFontSize(parseInt(e.target.value))}
            className="w-full h-2 bg-black/50 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        {/* Animations */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm flex items-center gap-2">
              <Monitor className="w-4 h-4 text-green-400" />
              Interface Animations
            </span>
            <select
              className="bg-black/30 dark:bg-gray-600 border border-green-500/30 text-green-400 rounded p-1 text-sm focus:outline-none focus:ring-1 focus:ring-green-500/50"
              value={animations}
              onChange={(e) => setAnimations(e.target.value)}
            >
              <option>Enabled</option>
              <option>Reduced</option>
              <option>Disabled</option>
            </select>
          </div>
        </div>

        {/* Contrast */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm flex items-center gap-2">
              <Settings className="w-4 h-4 text-green-400" />
              Color Contrast
            </span>
            <select
              className="bg-black/30 dark:bg-gray-600 border border-green-500/30 text-green-400 rounded p-1 text-sm focus:outline-none focus:ring-1 focus:ring-green-500/50"
              value={contrast}
              onChange={(e) => setContrast(e.target.value)}
            >
              <option>Normal</option>
              <option>High</option>
              <option>Maximum</option>
            </select>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="bg-green-500/30 hover:bg-green-500/40 border border-green-500/30 px-4 py-2 rounded text-green-400 font-medium"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;
