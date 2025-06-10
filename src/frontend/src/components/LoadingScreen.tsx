import React from 'react';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../contexts/ThemeContext';

interface LoadingScreenProps {
  message?: string;
  subMessage?: string;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ 
  message,
  subMessage 
}) => {
  const { t } = useTranslation();
  const { theme } = useTheme();

  return (
    <div className={`min-h-screen relative overflow-hidden flex items-center justify-center ${
      theme === 'dark' 
        ? 'bg-black text-white' 
        : 'bg-gradient-to-br from-gray-50 to-gray-100 text-gray-900'
    }`}>
      {/* Ambient light effects */}
      <div className="absolute inset-0">
        <div className={`absolute top-1/4 left-1/4 w-96 h-96 rounded-full blur-3xl animate-pulse ${
          theme === 'dark' ? 'bg-green-500/10' : 'bg-green-200/30'
        }`}></div>
        <div 
          className={`absolute bottom-1/4 right-1/4 w-64 h-64 rounded-full blur-2xl animate-pulse ${
            theme === 'dark' ? 'bg-green-400/5' : 'bg-green-300/20'
          }`}
          style={{ 
            animationDelay: '1s',
            animationDuration: '2s',
            animationIterationCount: 'infinite'
          }}
        ></div>
      </div>

      {/* Main content */}
      <div className="relative z-10 text-center max-w-md mx-auto px-6">
        {/* APEX Logo/Brand */}
        <div className="mb-8">
          <h1 className={`text-4xl font-bold mb-2 tracking-wider ${
            theme === 'dark' ? 'text-green-400' : 'text-green-600'
          }`}>
            APEX
          </h1>
          <div className={`w-24 h-1 mx-auto rounded-full ${
            theme === 'dark' 
              ? 'bg-gradient-to-r from-green-500 to-green-300'
              : 'bg-gradient-to-r from-green-600 to-green-400'
          }`}></div>
        </div>

        {/* Loading Animation */}
        <div className="mb-6">
          <div className="relative w-16 h-16 mx-auto">
            <div className={`absolute inset-0 border-4 rounded-full ${
              theme === 'dark' ? 'border-green-500/20' : 'border-green-300/40'
            }`}></div>
            <div className={`absolute inset-0 border-4 border-transparent rounded-full animate-spin ${
              theme === 'dark' ? 'border-t-green-400' : 'border-t-green-600'
            }`}></div>
            <div 
              className={`absolute inset-2 border-2 border-transparent rounded-full animate-spin ${
                theme === 'dark' ? 'border-t-green-300' : 'border-t-green-500'
              }`}
              style={{ 
                animationDirection: 'reverse', 
                animationDuration: '1.5s',
                animationIterationCount: 'infinite',
                animationTimingFunction: 'linear'
              }}
            ></div>
          </div>
        </div>

        {/* Loading Text */}
        <h2 className={`text-xl font-semibold mb-3 ${
          theme === 'dark' ? 'text-green-400' : 'text-green-700'
        }`}>
          {message || t('loading') || 'Loading...'}
        </h2>
        
        <p className={`text-sm mb-6 ${
          theme === 'dark' ? 'text-green-400/70' : 'text-green-600/80'
        }`}>
          {subMessage || t('loadingPermissions') || 'Please wait...'}
        </p>

        {/* Bouncing dots */}
        <div className="flex justify-center space-x-1">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className={`w-2 h-2 rounded-full ${
                theme === 'dark' ? 'bg-green-400' : 'bg-green-600'
              }`}
              style={{ 
                animationName: 'bounce',
                animationDuration: '1s',
                animationIterationCount: 'infinite',
                animationDelay: `${i * 0.2}s`
              }}
            ></div>
          ))}
        </div>
      </div>

      {/* Custom keyframe styles */}
      <style>{`
        @keyframes float {
          from { transform: translateY(0px) rotate(0deg); opacity: 0.3; }
          to { transform: translateY(-20px) rotate(180deg); opacity: 0.1; }
        }
      `}</style>
    </div>
  );
};

export default LoadingScreen; 