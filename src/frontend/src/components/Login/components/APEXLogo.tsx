import React from 'react';
import { Brain } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface APEXLogoProps {
  subtitle?: string;
  size?: 'sm' | 'md' | 'lg';
}

const APEXLogo: React.FC<APEXLogoProps> = ({ 
  subtitle,
  size = 'md'
}) => {
  const { i18n } = useTranslation();
  
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
        <div className="absolute inset-0 bg-green-500 rounded-full filter blur-lg opacity-20" />
        <Brain className={`${classes.icon} text-green-400 relative z-10`} />
      </div>
      <div className={`mt-4 ${classes.title} font-bold text-green-400`}>APEX</div>
      {subtitle && (
        <div className={`${classes.subtitle} text-green-400/70 mt-1`}>{subtitle}</div>
      )}
    </div>
  );
};

export default APEXLogo; 