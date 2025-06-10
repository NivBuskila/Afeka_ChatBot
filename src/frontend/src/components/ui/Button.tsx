import React from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'success';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  icon?: React.ReactNode;
  fullWidth?: boolean;
  children?: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  icon,
  fullWidth = false,
  children,
  className = '',
  disabled,
  ...rest
}) => {
  // Base styles
  const baseClasses = 'flex items-center justify-center font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed';
  
  // Size classes
  const sizeClasses = {
    sm: 'py-1 px-3 text-sm rounded',
    md: 'py-2 px-4 text-base rounded-md',
    lg: 'py-3 px-6 text-lg rounded-lg',
  };
  
  // Variant classes
  const variantClasses = {
    primary: 'bg-green-500 hover:bg-green-600 text-white focus:ring-green-500 border border-transparent',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800 focus:ring-gray-500 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white border border-transparent',
    danger: 'bg-red-500 hover:bg-red-600 text-white focus:ring-red-500 border border-transparent',
    success: 'bg-green-500 hover:bg-green-600 text-white focus:ring-green-500 border border-transparent',
  };
  
  // Loading indicator
  const LoadingIndicator = () => (
    <div className="flex space-x-1 mr-2">
      {[...Array(3)].map((_, i) => (
        <div
          key={i}
          className="w-1 h-1 bg-current rounded-full animate-bounce"
          style={{ animationDelay: `${i * 0.2}s` }}
        />
      ))}
    </div>
  );

  return (
    <button
      className={`
        ${baseClasses}
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${fullWidth ? 'w-full' : ''}
        ${className}
      `}
      disabled={isLoading || disabled}
      {...rest}
    >
      {isLoading ? (
        <LoadingIndicator />
      ) : icon ? (
        <span className={`${children ? 'mr-2' : ''}`}>{icon}</span>
      ) : null}
      {children}
    </button>
  );
};

export default Button; 