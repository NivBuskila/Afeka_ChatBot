import React from 'react';
import { translations } from '../translations';
import AnalyticsCard from './AnalyticsCard';

type Language = 'he' | 'en';

interface AnalyticsOverviewProps {
  language: Language;
}

const AnalyticsOverview: React.FC<AnalyticsOverviewProps> = ({ language }) => {
  const t = (key: string) => translations[key]?.[language] || key;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-green-400 mb-4">{t('analytics.overview')}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <AnalyticsCard
          title={t('analytics.active.users')}
          value="1,234"
          change="+12%"
          language={language}
        />
        <AnalyticsCard
          title={t('analytics.daily.conversations')}
          value="456"
          change="+8%"
          language={language}
        />
        <AnalyticsCard
          title={t('analytics.active.documents')}
          value="89"
          change="+5%"
          language={language}
        />
        <AnalyticsCard
          title={t('analytics.avg.response')}
          value="1.2s"
          change="-15%"
          language={language}
        />
      </div>
      <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-4">
        <div className="flex items-center justify-center h-[400px] text-green-400/50">
          {t('analytics.overview')}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsOverview; 