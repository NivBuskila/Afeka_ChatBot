import React, { forwardRef } from 'react';
import { useThemeClasses } from '../../hooks/useThemeClasses';

interface ThemeTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  variant?: 'default' | 'success' | 'error' | 'warning';
  textareaSize?: 'sm' | 'md' | 'lg';
  label?: string;
  error?: string;
  helper?: string;
  resize?: 'none' | 'vertical' | 'horizontal' | 'both';
}

const ThemeTextarea = forwardRef<HTMLTextAreaElement, ThemeTextareaProps>(({
  variant = 'default',
  textareaSize = 'md',
  label,
  error,
  helper,
  resize = 'vertical',
  className = '',
  rows = 4,
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
  
  const resizeClasses = {
    none: 'resize-none',
    vertical: 'resize-y',
    horizontal: 'resize-x',
    both: 'resize',
  };
  
  const textareaClasses = combine(
    'w-full border rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2',
    variantClasses[variant],
    sizeClasses[textareaSize],
    resizeClasses[resize],
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
      
      <textarea
        ref={ref}
        rows={rows}
        className={textareaClasses}
        {...props}
      />
      
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

ThemeTextarea.displayName = 'ThemeTextarea';

export default ThemeTextarea; 