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
    <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-4">
      <h3 className="text-green-400/80 mb-2">{title}</h3>
      <p className="text-2xl font-bold text-green-400">{value}</p>
      <p className="text-sm text-green-400/60">{change} {t('analytics.week.change')}</p>
    </div>
  );
};

export default AnalyticsCard; 