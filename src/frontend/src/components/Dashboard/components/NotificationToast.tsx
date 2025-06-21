import React from 'react';
import { CheckCircle, AlertCircle } from 'lucide-react';

interface NotificationToastProps {
  message: string;
  type: 'success' | 'error';
  onClose?: () => void;
}

export const NotificationToast: React.FC<NotificationToastProps> = ({ 
  message, 
  type, 
  onClose 
}) => {
  const isSuccess = type === 'success';
  
  return (
    <div 
      className={`fixed top-4 right-4 z-50 ${
        isSuccess 
          ? 'bg-green-50 dark:bg-green-900/20 border-l-4 border-green-500' 
          : 'bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500'
      } p-4 rounded shadow-md max-w-md animate-fadeIn`}
    >
      <div className="flex items-center">
        {isSuccess ? (
          <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 mr-2" />
        ) : (
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mr-2" />
        )}
        <p className={`${
          isSuccess 
            ? 'text-green-700 dark:text-green-300' 
            : 'text-red-700 dark:text-red-300'
        }`}>
          {message}
        </p>
        {onClose && (
          <button
            onClick={onClose}
            className={`ml-auto text-sm ${
              isSuccess 
                ? 'text-green-600 dark:text-green-400 hover:text-green-800 dark:hover:text-green-200' 
                : 'text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200'
            } transition-colors`}
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}; 