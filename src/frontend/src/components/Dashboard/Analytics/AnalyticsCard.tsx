import React from 'react';
import { translations } from '../translations';

type Language = 'he' | 'en';

interface AnalyticsCardProps {
  title: string;
  value: string;
  change: string;
  language: Language;
}

const AnalyticsCard: React.FC<AnalyticsCardProps> = ({ title, value, change, language }) => {
  const t = (key: string) => translations[key]?.[language] || key;

  return (
    <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-4 shadow-lg">
      <h3 className="text-gray-700 dark:text-green-400/80 mb-2">{title}</h3>
      <p className="text-2xl font-bold text-gray-800 dark:text-green-400">{value}</p>
      <p className="text-sm text-gray-600 dark:text-green-400/60">{change} {t('analytics.week.change')}</p>
    </div>
  );
};

export default AnalyticsCard; 