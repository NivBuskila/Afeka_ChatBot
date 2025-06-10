import React from 'react';
import { useThemeClasses } from '../../hooks/useThemeClasses';

interface ThemeCardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  shadow?: 'none' | 'sm' | 'md' | 'lg';
  border?: boolean;
  hover?: boolean;
}

const ThemeCard: React.FC<ThemeCardProps> = ({
  children,
  className = '',
  padding = 'md',
  shadow = 'sm',
  border = true,
  hover = false,
}) => {
  const { classes, combine } = useThemeClasses();
  
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };
  
  const shadowClasses = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
  };
  
  const cardClasses = combine(
    classes.bg.card,
    classes.text.primary,
    border ? classes.border.primary : '',
    border ? 'border' : '',
    'rounded-lg',
    shadowClasses[shadow],
    paddingClasses[padding],
    hover ? 'transition-shadow duration-200 hover:shadow-md' : '',
    className
  );
  
  return (
    <div className={cardClasses}>
      {children}
    </div>
  );
};

export default ThemeCard; 