import React, { forwardRef } from 'react';
import { useThemeClasses } from '../../hooks/useThemeClasses';

interface ThemeInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  variant?: 'default' | 'success' | 'error' | 'warning';
  inputSize?: 'sm' | 'md' | 'lg';
  label?: string;
  error?: string;
  helper?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const ThemeInput = forwardRef<HTMLInputElement, ThemeInputProps>(({
  variant = 'default',
  inputSize = 'md',
  label,
  error,
  helper,
  leftIcon,
  rightIcon,
  className = '',
  ...props
}, ref) => {
  const { classes, combine } = useThemeClasses();
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-3 py-2 text-base',
    lg: 'px-4 py-3 text-lg',
  };
  
  const variantClasses = {
    default: `${classes.bg.input} ${classes.text.primary} ${classes.border.primary} ${classes.border.focus}`,
    success: `${classes.bg.input} ${classes.text.primary} border-green-500 focus:border-green-600`,
    error: `${classes.bg.input} ${classes.text.primary} border-red-500 focus:border-red-600`,
    warning: `${classes.bg.input} ${classes.text.primary} border-yellow-500 focus:border-yellow-600`,
  };
  
  const inputClasses = combine(
    'w-full border rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2',
    variantClasses[variant],
    sizeClasses[inputSize],
    leftIcon ? 'pl-10' : '',
    rightIcon ? 'pr-10' : '',
    props.disabled ? 'opacity-50 cursor-not-allowed' : '',
    className
  );
  
  const labelClasses = combine(
    'block text-sm font-medium mb-1',
    classes.text.primary,
    props.disabled ? 'opacity-50' : ''
  );
  
  return (
    <div className="w-full">
      {label && (
        <label className={labelClasses}>
          {label}
        </label>
      )}
      
      <div className="relative">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2">
            <div className={`${classes.text.tertiary} flex-shrink-0`}>
              {leftIcon}
            </div>
          </div>
        )}
        
        <input
          ref={ref}
          className={inputClasses}
          {...props}
        />
        
        {rightIcon && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <div className={`${classes.text.tertiary} flex-shrink-0`}>
              {rightIcon}
            </div>
          </div>
        )}
      </div>
      
      {error && (
        <p className={`mt-1 text-sm ${classes.text.error}`}>
          {error}
        </p>
      )}
      
      {helper && !error && (
        <p className={`mt-1 text-sm ${classes.text.secondary}`}>
          {helper}
        </p>
      )}
    </div>
  );
});

ThemeInput.displayName = 'ThemeInput';

export default ThemeInput; 