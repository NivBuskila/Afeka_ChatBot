import React from 'react';
import { useTranslation } from 'react-i18next';
import { BarChart3, Users, FileText, Clock, UserCog } from 'lucide-react';
import type { Document } from '../../config/supabase';

// Create basic Spinner component if not in project
const Spinner: React.FC<{ size?: string }> = ({ size = "md" }) => {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8",
  };

  return (
    <div className={`animate-spin rounded-full border-t-2 border-b-2 border-green-500 ${sizeClasses[size as keyof typeof sizeClasses]}`}></div>
  );
};

// Create StatBox component
interface StatBoxProps {
  title: string;
  value: string;
  icon: React.ReactNode;
}

const StatBox: React.FC<StatBoxProps> = ({ title, value, icon }) => {
  return (
    <div className="bg-gray-800 p-4 rounded-lg flex items-center">
      <div className="mr-4">{icon}</div>
      <div>
        <p className="text-sm text-gray-400">{title}</p>
        <p className="text-xl font-bold">{value}</p>
      </div>
    </div>
  );
};

// Helper function for date formatting
const formatDate = (dateString?: string) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString();
};

interface AnalyticsOverviewProps {
  analytics: {
    totalDocuments: number;
    totalUsers: number;
    totalAdmins: number;
    recentDocuments: Document[];
    recentUsers: any[];
    recentAdmins: any[];
  };
  isLoading: boolean;
}

export const AnalyticsOverview: React.FC<AnalyticsOverviewProps> = ({ analytics, isLoading }) => {
  const { t } = useTranslation();
  
  console.log("Analytics data in AnalyticsOverview:", analytics);

  // Check for empty or non-existent data
  const hasData = analytics && !isLoading;
  const hasUsers = hasData && Array.isArray(analytics.recentUsers) && analytics.recentUsers.length > 0;
  const hasAdmins = hasData && Array.isArray(analytics.recentAdmins) && analytics.recentAdmins.length > 0;
  const hasDocuments = hasData && Array.isArray(analytics.recentDocuments) && analytics.recentDocuments.length > 0;

  // General counters - if no data, show at least 0
  const totalDocuments = hasData ? analytics.totalDocuments || 0 : 0;
  const totalUsers = hasData ? analytics.totalUsers || 0 : 0;
  const totalAdmins = hasData ? analytics.totalAdmins || 0 : 0;

  // Take only 5 users/admins for display
  const recentUsers = hasUsers ? analytics.recentUsers.slice(0, 5) : [];
  const recentAdmins = hasAdmins ? analytics.recentAdmins.slice(0, 5) : [];
  const recentDocuments = hasDocuments ? analytics.recentDocuments.slice(0, 5) : [];

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex justify-center items-center h-40">
          <Spinner size="lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* User metrics */}
        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-6 shadow-lg">
          <h3 className="text-lg font-semibold text-green-600 dark:text-green-400 mb-4">{t('analytics.users')}</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-green-400/70">{t('analytics.totalUsers')}</p>
                <p className="text-2xl font-semibold mt-1 text-gray-800 dark:text-green-400">{totalUsers}</p>
              </div>
              <div className="text-green-600 dark:text-green-500 bg-opacity-10 p-3 rounded-full">
                <Users className="w-6 h-6" />
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-green-400/70">{t('analytics.totalAdmins')}</p>
                <p className="text-2xl font-semibold mt-1 text-gray-800 dark:text-green-400">{totalAdmins}</p>
              </div>
              <div className="text-purple-600 dark:text-purple-500 bg-opacity-10 p-3 rounded-full">
                <UserCog className="w-6 h-6" />
              </div>
            </div>
          </div>
        </div>
        
        {/* Document metrics */}
        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-6 shadow-lg">
          <h3 className="text-lg font-semibold text-green-600 dark:text-green-400 mb-4">{t('analytics.documents')}</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-green-400/70">{t('analytics.totalDocuments')}</p>
                <p className="text-2xl font-semibold mt-1 text-gray-800 dark:text-green-400">{totalDocuments}</p>
              </div>
              <div className="text-blue-600 dark:text-blue-500 bg-opacity-10 p-3 rounded-full">
                <FileText className="w-6 h-6" />
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-green-400/70">{t('analytics.activeDocuments')}</p>
                <p className="text-2xl font-semibold mt-1 text-gray-800 dark:text-green-400">{recentDocuments.length}</p>
              </div>
              <div className="text-yellow-600 dark:text-yellow-500 bg-opacity-10 p-3 rounded-full">
                <Clock className="w-6 h-6" />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Recent users */}
        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 shadow-lg">
          <div className="border-b border-gray-300 dark:border-green-500/20 py-3 px-6">
            <h3 className="text-lg font-semibold text-green-600 dark:text-green-400">{t('analytics.activeUsers')}</h3>
          </div>
          <div className="p-6 space-y-4">
            {hasUsers ? (
              recentUsers.map((user, index) => (
                <div key={user.id || index} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-800 dark:text-green-400">{user.email || user.name || t('general.noName')}</p>
                    <p className="text-sm text-gray-600 dark:text-green-400/50">
                      {user.created_at ? new Date(user.created_at).toLocaleDateString() : ''}
                    </p>
                  </div>
                  <span className="text-sm text-gray-600 dark:text-green-400/70">
                    user
                  </span>
                </div>
              ))
            ) : (
              <p className="text-gray-600 dark:text-green-400/70">{t('analytics.noUsers')}</p>
            )}
          </div>
        </div>
        
        {/* Recent admins */}
        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 shadow-lg">
          <div className="border-b border-gray-300 dark:border-green-500/20 py-3 px-6">
            <h3 className="text-lg font-semibold text-green-600 dark:text-green-400">{t('analytics.activeAdmins')}</h3>
          </div>
          <div className="p-6 space-y-4">
            {hasAdmins ? (
              recentAdmins.map((admin, index) => (
                <div key={admin.id || index} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-800 dark:text-green-400">{admin.email || admin.name || t('general.noName')}</p>
                    <p className="text-sm text-gray-600 dark:text-green-400/50">
                      {admin.created_at ? new Date(admin.created_at).toLocaleDateString() : ''}
                    </p>
                  </div>
                  <span className="text-sm text-gray-600 dark:text-green-400/70">
                    admin {admin.department ? `(${admin.department})` : ''}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-gray-600 dark:text-green-400/70">{t('analytics.noAdmins')}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}; 