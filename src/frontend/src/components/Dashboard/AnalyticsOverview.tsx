import React from 'react';
import { useTranslation } from 'react-i18next';
import { BarChart3, Users, FileText, Clock, UserCog } from 'lucide-react';
import type { Document } from '../../config/supabase';

interface AnalyticsOverviewProps {
  analytics: {
    totalDocuments: number;
    totalUsers: number;
    totalAdmins: number;
    recentDocuments: Document[];
    recentUsers: any[];
    recentAdmins: any[];
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
      title: t('analytics.totalAdmins'),
      value: analytics.totalAdmins,
      icon: <UserCog className="w-6 h-6" />,
      color: 'text-purple-500'
    },
    {
      title: t('analytics.activeDocuments'),
      value: analytics.recentDocuments.length,
      icon: <Clock className="w-6 h-6" />,
      color: 'text-yellow-500'
    }
  ];

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-green-400 mb-6">{t('analytics.overview')}</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* User metrics */}
        <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-6">
          <h3 className="text-lg font-semibold text-green-400 mb-4">{t('analytics.users')}</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-400/70">{t('analytics.totalUsers')}</p>
                <p className="text-2xl font-semibold mt-1 text-green-400">{analytics.totalUsers}</p>
              </div>
              <div className="text-green-500 bg-opacity-10 p-3 rounded-full">
                <Users className="w-6 h-6" />
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-400/70">{t('analytics.totalAdmins')}</p>
                <p className="text-2xl font-semibold mt-1 text-green-400">{analytics.totalAdmins}</p>
              </div>
              <div className="text-purple-500 bg-opacity-10 p-3 rounded-full">
                <UserCog className="w-6 h-6" />
              </div>
            </div>
          </div>
        </div>
        
        {/* Document metrics */}
        <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-6">
          <h3 className="text-lg font-semibold text-green-400 mb-4">{t('analytics.documents')}</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-400/70">{t('analytics.totalDocuments')}</p>
                <p className="text-2xl font-semibold mt-1 text-green-400">{analytics.totalDocuments}</p>
              </div>
              <div className="text-blue-500 bg-opacity-10 p-3 rounded-full">
                <FileText className="w-6 h-6" />
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-400/70">{t('analytics.activeDocuments')}</p>
                <p className="text-2xl font-semibold mt-1 text-green-400">{analytics.recentDocuments.length}</p>
              </div>
              <div className="text-yellow-500 bg-opacity-10 p-3 rounded-full">
                <Clock className="w-6 h-6" />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Recent users */}
        <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20">
          <div className="border-b border-green-500/20 py-3 px-6">
            <h3 className="text-lg font-semibold text-green-400">{t('analytics.activeUsers')}</h3>
          </div>
          <div className="p-6 space-y-4">
            {analytics.recentUsers.map((user) => (
              <div key={user.id} className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-green-400">{user.email}</p>
                  <p className="text-sm text-green-400/50">
                    {new Date(user.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span className="text-sm text-green-400/70">
                  user
                </span>
              </div>
            ))}
          </div>
        </div>
        
        {/* Recent admins */}
        <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20">
          <div className="border-b border-green-500/20 py-3 px-6">
            <h3 className="text-lg font-semibold text-green-400">{t('Active Admins')}</h3>
          </div>
          <div className="p-6 space-y-4">
            {analytics.recentAdmins.map((admin) => (
              <div key={admin.id} className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-green-400">{admin.email}</p>
                  <p className="text-sm text-green-400/50">
                    {new Date(admin.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span className="text-sm text-green-400/70">
                  admin {admin.department ? `(${admin.department})` : ''}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}; 