import React from 'react';
import { Brain } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../../../contexts/ThemeContext';

interface APEXLogoProps {
  subtitle?: string;
  size?: 'sm' | 'md' | 'lg';
}

const APEXLogo: React.FC<APEXLogoProps> = ({ 
  subtitle,
  size = 'md'
}) => {
  const { i18n } = useTranslation();
  const { theme } = useTheme();
  
  const sizeClasses = {
    sm: {
      container: 'mb-4',
      icon: 'w-10 h-10',
      title: 'text-xl',
      subtitle: 'text-xs'
    },
    md: {
      container: 'mb-6',
      icon: 'w-16 h-16',
      title: 'text-3xl',
      subtitle: 'text-sm'
    },
    lg: {
      container: 'mb-8',
      icon: 'w-20 h-20',
      title: 'text-4xl',
      subtitle: 'text-base'
    }
  };
  
  const classes = sizeClasses[size];

  return (
    <div className={`${classes.container} flex flex-col items-center`}>
      <div className="relative">
        <div className={`absolute inset-0 rounded-full filter blur-lg opacity-20 ${
          theme === 'dark' ? 'bg-green-500' : 'bg-green-600'
        }`} />
        <Brain className={`${classes.icon} relative z-10 ${
          theme === 'dark' ? 'text-green-400' : 'text-green-600'
        }`} />
      </div>
      <div className={`mt-4 ${classes.title} font-bold ${
        theme === 'dark' ? 'text-green-400' : 'text-green-600'
      }`}>APEX</div>
      {subtitle && (
        <div className={`${classes.subtitle} mt-1 ${
          theme === 'dark' ? 'text-green-400/70' : 'text-green-600/80'
        }`}>{subtitle}</div>
      )}
    </div>
  );
};

export default APEXLogo; 