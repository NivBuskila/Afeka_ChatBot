import React from 'react';
import { useTranslation } from 'react-i18next';

interface LoadingScreenProps {
  message?: string;
  subMessage?: string;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ 
  message,
  subMessage 
}) => {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-black relative overflow-hidden flex items-center justify-center">
      {/* Ambient light effects */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-green-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div 
          className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-green-400/5 rounded-full blur-2xl animate-pulse" 
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
          <h1 className="text-4xl font-bold text-green-400 mb-2 tracking-wider">
            APEX
          </h1>
          <div className="w-24 h-1 bg-gradient-to-r from-green-500 to-green-300 mx-auto rounded-full"></div>
        </div>

        {/* Loading Animation */}
        <div className="mb-6">
          <div className="relative w-16 h-16 mx-auto">
            <div className="absolute inset-0 border-4 border-green-500/20 rounded-full"></div>
            <div className="absolute inset-0 border-4 border-transparent border-t-green-400 rounded-full animate-spin"></div>
            <div 
              className="absolute inset-2 border-2 border-transparent border-t-green-300 rounded-full animate-spin" 
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
        <h2 className="text-xl font-semibold text-green-400 mb-3">
          {message || t('loading') || 'Loading...'}
        </h2>
        
        <p className="text-green-400/70 text-sm mb-6">
          {subMessage || t('loadingPermissions') || 'Please wait...'}
        </p>

        {/* Bouncing dots */}
        <div className="flex justify-center space-x-1">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-2 h-2 bg-green-400 rounded-full"
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