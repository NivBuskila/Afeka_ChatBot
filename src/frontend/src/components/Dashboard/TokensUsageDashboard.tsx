import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Coins, 
  Activity, 
  Clock, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  RefreshCw,
  TrendingUp,
  BarChart3,
  Download
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { tokenService, TokenUsageData, TokenUsageReport } from '../../services/tokenService';

interface TokenUsageAnalyticsProps {
  language: string;
}

interface KeyStatusData {
  id: number;
  status: 'available' | 'blocked' | 'cooldown' | 'error';
  tokens_today: number;
  tokens_current_minute: number;
  requests_current_minute: number;
  next_reset: string;
  tokens_per_day_usage?: number;
  requests_per_minute_usage?: number;
}

export const TokenUsageAnalytics: React.FC<TokenUsageAnalyticsProps> = ({ language }) => {
  const { t } = useTranslation();
  const [usageData, setUsageData] = useState<TokenUsageData | null>(null);
  const [usageReport, setUsageReport] = useState<TokenUsageReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [timelineData, setTimelineData] = useState<any[]>([]);

  // Auto-refresh every 60 seconds (reduced from 30)
  useEffect(() => {
    const interval = setInterval(() => {
      // Only refresh if page is visible and not already loading
      if (!document.hidden && !isLoading) {
        fetchData();
      }
    }, 60000); // Changed from 30000 to 60000 (60 seconds)

    return () => clearInterval(interval);
  }, []);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const [metricsResponse, reportResponse] = await Promise.all([
        tokenService.getTokenUsageData(),
        tokenService.getUsageReport()
      ]);

      setUsageData(metricsResponse);
      setUsageReport(reportResponse);
      setLastUpdate(new Date());
      
      // Generate mock timeline data for the last 24 hours
      generateTimelineData();
    } catch (error) {
      console.error('Failed to fetch token usage data:', error);
      setError('Failed to load token usage data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const generateTimelineData = () => {
    const data = [];
    const now = new Date();
    
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000);
      data.push({
        time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        requests: Math.floor(Math.random() * 50) + 10,
        tokens: Math.floor(Math.random() * 5000) + 1000
      });
    }
    
    setTimelineData(data);
  };

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleRefresh = () => {
    fetchData();
  };

  const handleExportCSV = () => {
    if (!usageData || !usageReport) return;

    const csvData = Object.entries(usageData.keys).map(([keyHash, key], index) => ({
      'Key ID': `Key #${index + 1}`,
      'Status': key.status,
      'Tokens Today': key.tokens_used_today,
      'Tokens/Min': key.tokens_used_this_minute,
      'Requests/Min': key.requests_this_minute,
      'Tokens Remaining': usageData.limits.max_tokens_per_day - key.tokens_used_today,
      'Daily Usage %': Math.round((key.tokens_used_today / usageData.limits.max_tokens_per_day) * 100)
    }));

    const csv = [
      Object.keys(csvData[0]).join(','),
      ...csvData.map(row => Object.values(row).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `token-usage-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
      case 'available':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'cooldown':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'blocked':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Activity className="w-4 h-4 text-blue-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'available':
        return 'text-green-500 bg-green-100 dark:bg-green-900/20';
      case 'cooldown':
        return 'text-yellow-500 bg-yellow-100 dark:bg-yellow-900/20';
      case 'error':
      case 'blocked':
        return 'text-red-500 bg-red-100 dark:bg-red-900/20';
      default:
        return 'text-blue-500 bg-blue-100 dark:bg-blue-900/20';
    }
  };

  const formatUsagePercentage = (used: number, limit: number): string => {
    if (limit === 0) return '0%';
    return `${Math.round((used / limit) * 100)}%`;
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex justify-center items-center h-40">
          <RefreshCw className="w-8 h-8 animate-spin text-green-400" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-100 dark:bg-red-900/20 border border-red-300 dark:border-red-500/30 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
            <span className="text-red-700 dark:text-red-400">{error}</span>
          </div>
          <button 
            onClick={handleRefresh}
            className="mt-3 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
          >
            {language === 'he' ? 'נסה שוב' : 'Try Again'}
          </button>
        </div>
      </div>
    );
  }

  if (!usageData || !usageReport) {
    return (
      <div className="p-6">
        <div className="text-center text-gray-500 dark:text-green-400/50">
          {t('analytics.no.data')}
        </div>
      </div>
    );
  }

  const summary = usageReport.summary;
  const keyData = Object.entries(usageData.keys).map(([keyHash, key], index) => ({
    id: index + 1,
    name: `Key #${index + 1}`,
    status: key.status as 'available' | 'blocked' | 'cooldown' | 'error',
    tokens_today: key.tokens_used_today,
    tokens_limit: usageData.limits.max_tokens_per_day,
    tokens_current_minute: key.tokens_used_this_minute,
    requests_current_minute: key.requests_this_minute,
    usage_percentage: (key.tokens_used_today / usageData.limits.max_tokens_per_day) * 100,
    next_reset: key.cooldown_until || new Date().toISOString()
  }));

  const availableKeys = keyData.filter(k => k.status === 'available').length;
  const blockedKeys = keyData.filter(k => k.status === 'blocked' || k.status === 'error').length;
  const totalRequestsToday = Object.values(usageData.keys).reduce((sum, key) => sum + key.requests_today, 0);

  // Chart colors
  const COLORS = ['#10B981', '#F59E0B', '#EF4444', '#6B7280'];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">
            {language === 'he' ? 'ניתוח שימוש ב-API' : 'Token Usage Analytics'}
          </h2>
          <p className="text-sm text-gray-600 dark:text-green-400/70 mt-1">
            {language === 'he' ? 'עדכון אחרון:' : 'Last updated:'} {lastUpdate.toLocaleTimeString()}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg border border-blue-500/30 transition-colors"
          >
            <Download className="w-4 h-4" />
            {language === 'he' ? 'ייצא CSV' : 'Export CSV'}
          </button>
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg border border-green-500/30 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            {language === 'he' ? 'רענן' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-green-400/70">
                {language === 'he' ? 'סך כל מפתחות' : 'Total API Keys'}
              </p>
              <p className="text-2xl font-semibold mt-1 text-gray-800 dark:text-green-400">
                {summary.total_keys}
              </p>
            </div>
            <Coins className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-green-400/70">
                {language === 'he' ? 'מפתחות זמינים' : 'Available Keys'}
              </p>
              <p className="text-2xl font-semibold mt-1 text-gray-800 dark:text-green-400">
                {availableKeys}
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-green-400/70">
                {language === 'he' ? 'מפתחות חסומים' : 'Blocked Keys'}
              </p>
              <p className="text-2xl font-semibold mt-1 text-gray-800 dark:text-green-400">
                {blockedKeys}
              </p>
            </div>
            <XCircle className="w-8 h-8 text-red-500" />
          </div>
        </div>

        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-green-400/70">
                {language === 'he' ? 'בקשות היום' : 'Total Requests Today'}
              </p>
              <p className="text-2xl font-semibold mt-1 text-gray-800 dark:text-green-400">
                {totalRequestsToday.toLocaleString()}
              </p>
            </div>
            <Activity className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Usage by Key Bar Chart */}
        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-6 shadow-lg">
          <h3 className="text-lg font-semibold text-green-600 dark:text-green-400 mb-4">
            {language === 'he' ? 'שימוש לפי מפתח' : 'Usage by Key'}
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={keyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis 
                dataKey="name" 
                stroke="#6B7280"
                tick={{ fill: '#6B7280', fontSize: 12 }}
              />
              <YAxis 
                stroke="#6B7280"
                tick={{ fill: '#6B7280', fontSize: 12 }}
                tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F3F4F6'
                }}
                formatter={(value: any) => [value.toLocaleString(), 'Tokens Used']}
              />
              <Bar 
                dataKey="tokens_today" 
                fill="#10B981"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Requests Timeline */}
        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-6 shadow-lg">
          <h3 className="text-lg font-semibold text-green-600 dark:text-green-400 mb-4">
            {language === 'he' ? 'בקשות לאורך זמן' : 'Requests Timeline (24h)'}
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis 
                dataKey="time" 
                stroke="#6B7280"
                tick={{ fill: '#6B7280', fontSize: 12 }}
                interval={5}
              />
              <YAxis 
                stroke="#6B7280"
                tick={{ fill: '#6B7280', fontSize: 12 }}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F3F4F6'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="requests" 
                stroke="#3B82F6" 
                strokeWidth={2}
                dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, fill: '#3B82F6' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Key Status Table */}
      <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 shadow-lg">
        <div className="border-b border-gray-300 dark:border-green-500/20 py-3 px-6">
          <h3 className="text-lg font-semibold text-green-600 dark:text-green-400">
            {language === 'he' ? 'מצב מפתחות מפורט' : 'Key Status Details'}
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-black/20">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-green-400/70 uppercase tracking-wider">
                  {language === 'he' ? 'מפתח' : 'Key ID'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-green-400/70 uppercase tracking-wider">
                  {language === 'he' ? 'סטטוס' : 'Status'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-green-400/70 uppercase tracking-wider">
                  {language === 'he' ? 'טוקנים היום' : 'Tokens Today'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-green-400/70 uppercase tracking-wider">
                  {language === 'he' ? 'טוקנים/דקה' : 'Tokens/Min'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-green-400/70 uppercase tracking-wider">
                  {language === 'he' ? 'בקשות/דקה' : 'Requests/Min'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-green-400/70 uppercase tracking-wider">
                  {language === 'he' ? 'איפוס הבא' : 'Next Reset'}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-green-500/20">
              {keyData.map((key) => (
                <tr key={key.id} className="hover:bg-gray-50 dark:hover:bg-green-500/5">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm font-medium text-gray-900 dark:text-green-400">
                      {key.name}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(key.status)}
                      <span className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(key.status)}`}>
                        {key.status}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 dark:text-green-400">
                      {key.tokens_today.toLocaleString()}
                      <div className="text-xs text-gray-500 dark:text-green-400/50">
                        {formatUsagePercentage(key.tokens_today, key.tokens_limit)} of daily limit
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-green-400">
                    {key.tokens_current_minute}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-green-400">
                    {key.requests_current_minute}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-green-400/70">
                    {new Date(key.next_reset).toLocaleTimeString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default TokenUsageAnalytics; 