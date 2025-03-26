import React from 'react';
import { useTranslation } from 'react-i18next';
import { BarChart3, Users, FileText, Clock } from 'lucide-react';
import type { Document } from '../../config/supabase';

interface AnalyticsOverviewProps {
  analytics: {
    totalDocuments: number;
    totalUsers: number;
    recentDocuments: Document[];
    recentUsers: any[];
  };
}

export const AnalyticsOverview: React.FC<AnalyticsOverviewProps> = ({ analytics }) => {
  const { t } = useTranslation();

  const stats = [
    {
      title: t('analytics.totalDocuments'),
      value: analytics.totalDocuments,
      icon: <FileText className="w-6 h-6" />,
      color: 'text-blue-500'
    },
    {
      title: t('analytics.totalUsers'),
      value: analytics.totalUsers,
      icon: <Users className="w-6 h-6" />,
      color: 'text-green-500'
    },
    {
      title: t('analytics.activeDocuments'),
      value: analytics.recentDocuments.length,
      icon: <Clock className="w-6 h-6" />,
      color: 'text-yellow-500'
    },
    {
      title: t('analytics.activeUsers'),
      value: analytics.recentUsers.length,
      icon: <BarChart3 className="w-6 h-6" />,
      color: 'text-purple-500'
    }
  ];

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-green-400 mb-6">{t('analytics.overview')}</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* User metrics */}
        <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-6">
          <h3 className="text-lg font-semibold text-green-400 mb-4">{t('analytics.users')}</h3>
          {stats.map((stat, index) => (
            <div
              key={index}
              className="flex items-center justify-between"
            >
              <div>
                <p className="text-sm text-green-400/70">{stat.title}</p>
                <p className="text-2xl font-semibold mt-1 text-green-400">{stat.value}</p>
              </div>
              <div className={`${stat.color} bg-opacity-10 p-3 rounded-full`}>
                {stat.icon}
              </div>
            </div>
          ))}
        </div>
        
        {/* Document metrics */}
        <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-6">
          <h3 className="text-lg font-semibold text-green-400 mb-4">{t('analytics.documents')}</h3>
          {stats.map((stat, index) => (
            <div
              key={index}
              className="flex items-center justify-between"
            >
              <div>
                <p className="text-sm text-green-400/70">{stat.title}</p>
                <p className="text-2xl font-semibold mt-1 text-green-400">{stat.value}</p>
              </div>
              <div className={`${stat.color} bg-opacity-10 p-3 rounded-full`}>
                {stat.icon}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Recent users */}
        <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20">
          <div className="border-b border-green-500/20 py-3 px-6">
            <h3 className="text-lg font-semibold text-green-400">{t('analytics.activeUsers')}</h3>
          </div>
          <div className="space-y-4">
            {analytics.recentUsers.map((user) => (
              <div key={user.id} className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-green-400">{user.email}</p>
                  <p className="text-sm text-green-400/50">
                    {new Date(user.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span className="text-sm text-green-400/70">
                  {user.role}
                </span>
              </div>
            ))}
          </div>
        </div>
        
        {/* Recent documents */}
        <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20">
          <div className="border-b border-green-500/20 py-3 px-6">
            <h3 className="text-lg font-semibold text-green-400">{t('analytics.activeDocuments')}</h3>
          </div>
          <div className="space-y-4">
            {analytics.recentDocuments.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-green-400">{doc.name}</p>
                  <p className="text-sm text-green-400/50">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span className="text-sm text-green-400/70">
                  {(doc.size / 1024 / 1024).toFixed(2)} MB
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}; 