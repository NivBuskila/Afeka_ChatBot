import React, { forwardRef } from 'react';
import { ChevronDown } from 'lucide-react';
import { useThemeClasses } from '../../hooks/useThemeClasses';

interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

interface ThemeSelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'children'> {
  variant?: 'default' | 'success' | 'error' | 'warning';
  selectSize?: 'sm' | 'md' | 'lg';
  label?: string;
  error?: string;
  helper?: string;
  options: SelectOption[];
  placeholder?: string;
}

const ThemeSelect = forwardRef<HTMLSelectElement, ThemeSelectProps>(({
  variant = 'default',
  selectSize = 'md',
  label,
  error,
  helper,
  options,
  placeholder,
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
  
  const selectClasses = combine(
    'w-full border rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 appearance-none pr-10',
    variantClasses[variant],
    sizeClasses[selectSize],
    props.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
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
        <select
          ref={ref}
          className={selectClasses}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((option) => (
            <option
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </select>
        
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
          <ChevronDown className={`w-4 h-4 ${classes.text.tertiary}`} />
        </div>
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

ThemeSelect.displayName = 'ThemeSelect';

export default ThemeSelect; 