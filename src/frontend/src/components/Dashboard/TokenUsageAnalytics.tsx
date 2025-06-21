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
  Download,
  Server
} from 'lucide-react';

interface TokenUsageAnalyticsProps {
  language: string;
}

interface KeyStatus {
  id: number;
  status: 'available' | 'blocked' | 'cooldown' | 'error';
  is_current: boolean;
  tokens_today: number;
  requests_today: number;
  tokens_current_minute: number;
  requests_current_minute: number;
  next_reset: string;
  last_used?: string;
  first_used_today?: string;
}

interface KeyManagementStatus {
  keys_status: KeyStatus[];
  current_key_index: number;
  health_status: string;
  total_keys: number;
  healthy_keys: number;
  available_keys: number;
  blocked_keys: number;
  cooldown_keys: number;
  current_key_usage: {
    current_key_index: number;
    tokens_today: number;
    tokens_current_minute: number;
    requests_today: number;
    requests_current_minute: number;
    status: string;
    key_name: string;
  };
}

// Memoized component to prevent unnecessary re-renders
export const TokenUsageAnalytics: React.FC<TokenUsageAnalyticsProps> = React.memo(({ language }) => {
  const { t } = useTranslation();
  const [keyData, setKeyData] = useState<KeyStatus[]>([]);
  const [managementStatus, setManagementStatus] = useState<KeyManagementStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [keyChangeAlert, setKeyChangeAlert] = useState<{show: boolean, oldKey: number, newKey: number} | null>(null);
  const [previousCurrentKey, setPreviousCurrentKey] = useState<number | null>(null);
  const [refreshInterval, setRefreshInterval] = useState<number>(30000);
  const [isVisible, setIsVisible] = useState<boolean>(true);

  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsVisible(!document.hidden);
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  const fetchData = useCallback(async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setIsLoading(true);
      } else {
        setIsUpdating(true);
      }
      
      setError(null);
      
      const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
      
      const response = await fetch(`${BACKEND_URL}/api/keys/`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'ok' && data.key_management) {
        const keyManagement = data.key_management;
        
        const prevCurrentKey = managementStatus?.current_key_index;
        
        setManagementStatus(keyManagement);
        
        const transformedKeys: KeyStatus[] = keyManagement.keys_status.map((keyStatus: any) => {
          return {
            id: keyStatus.id + 1,
            status: keyStatus.status,
            is_current: keyStatus.is_current,
            tokens_today: keyStatus.tokens_today || 0,
            requests_today: keyStatus.requests_today || 0,
            tokens_current_minute: keyStatus.tokens_current_minute || 0,
            requests_current_minute: keyStatus.requests_current_minute || 0,
            next_reset: new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString(),
            last_used: keyStatus.last_used,
            first_used_today: keyStatus.first_used_today
          };
        });
        
        setKeyData(transformedKeys);
        
        if (prevCurrentKey !== undefined && prevCurrentKey !== keyManagement.current_key_index) {
          // Key switched
          setKeyChangeAlert({
            show: true,
            oldKey: prevCurrentKey,
            newKey: keyManagement.current_key_index
          });
          
          setTimeout(() => {
            setKeyChangeAlert(null);
          }, 8000);
        }
        
        setPreviousCurrentKey(keyManagement.current_key_index);
      } else {
        throw new Error('Invalid response format from key status API');
      }
      
      setLastUpdate(new Date());
    } catch (error) {
      console.error('❌ [DASHBOARD-ERROR] Failed to fetch token usage data:', error);
      setError('Failed to load token usage data. Please check if the AI service is running.');
    } finally {
      if (isInitialLoad) {
        setIsLoading(false);
      } else {
        setIsUpdating(false);
      }
    }
  }, []);

  useEffect(() => {
    fetchData(true); // Initial load with loading state
    
    const interval = setInterval(() => {
      // Only refresh if page is visible and user is actively viewing this component
      if (!document.hidden && !isUpdating && !isLoading) {
        fetchData(false); // Auto-refresh without loading state
      }
    }, 30000); // Changed from 5000 to 30000 (30 seconds)

    return () => clearInterval(interval);
  }, [fetchData]);

  const handleRefresh = () => {
    fetchData(true); // Manual refresh with loading indicator
  };

  const handleExportCSV = () => {
    if (!managementStatus) return;

    const csvData = keyData.map(key => ({
      'Key ID': `Key #${key.id}`,
      'Status': key.status,
      'Is Current': key.is_current ? 'Yes' : 'No',
      'Tokens Today': key.tokens_today || 'N/A',
      'Tokens/Min': key.tokens_current_minute || 'N/A',
      'Requests/Min': key.requests_current_minute || 'N/A',
      'Next Reset': new Date(key.next_reset).toLocaleTimeString()
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
      case 'current':
        return <Activity className="w-4 h-4 text-blue-500" />;
      case 'available':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'blocked':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'current':
        return 'text-blue-500 bg-blue-100 dark:bg-blue-900/20';
      case 'available':
        return 'text-green-500 bg-green-100 dark:bg-green-900/20';
      case 'blocked':
        return 'text-red-500 bg-red-100 dark:bg-red-900/20';
      default:
        return 'text-yellow-500 bg-yellow-100 dark:bg-yellow-900/20';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'current':
        return language === 'he' ? 'נוכחי' : 'Current';
      case 'available':
        return language === 'he' ? 'זמין' : 'Available';
      case 'blocked':
        return language === 'he' ? 'חסום' : 'Blocked';
      default:
        return status;
    }
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

  if (!managementStatus) {
    return (
      <div className="p-6">
        <div className="text-center text-gray-500 dark:text-green-400/50">
          {language === 'he' ? 'אין נתונים זמינים' : 'No data available'}
        </div>
      </div>
    );
  }

  const totalKeys = managementStatus.total_keys;
  const availableKeys = managementStatus.available_keys;
  const blockedKeys = totalKeys - availableKeys;
  
  // 🆕 השתמש בנתונים החדשים מהבקאנד במקום לחפש ב-keyData
  const currentKey = managementStatus.current_key_usage ? {
    id: managementStatus.current_key_usage.current_key_index + 1,
    tokens_today: managementStatus.current_key_usage.tokens_today,
    tokens_current_minute: managementStatus.current_key_usage.tokens_current_minute,
    requests_today: managementStatus.current_key_usage.requests_today,
    requests_current_minute: managementStatus.current_key_usage.requests_current_minute,
    status: managementStatus.current_key_usage.status,
    key_name: managementStatus.current_key_usage.key_name
  } : keyData.find(k => k.is_current);

  const totalTokensToday = keyData.reduce((sum, key) => sum + (key.tokens_today || 0), 0);
  const totalRequestsToday = keyData.reduce((sum, key) => sum + (key.requests_today || 0), 0);
  
  const activeKeysToday = keyData.filter(k => (k.tokens_today || 0) > 0 || (k.requests_today || 0) > 0).length;
  const totalCurrentMinuteTokens = keyData.reduce((sum, key) => sum + (key.tokens_current_minute || 0), 0);
  const totalCurrentMinuteRequests = keyData.reduce((sum, key) => sum + (key.requests_current_minute || 0), 0);

  return (
    <div className="p-6 space-y-6">
      {keyChangeAlert?.show && (
        <div className="bg-blue-100 dark:bg-blue-900/20 border border-blue-300 dark:border-blue-500/30 rounded-lg p-4 animate-pulse">
          <div className="flex items-center">
            <Activity className="w-5 h-5 text-blue-500 mr-2 animate-spin" />
            <span className="text-blue-700 dark:text-blue-400 font-medium">
              {language === 'he' 
                ? `מפתח הוחלף אוטומטית: מפתח #${keyChangeAlert.oldKey + 1} → מפתח #${keyChangeAlert.newKey + 1}`
                : `API Key switched automatically: Key #${keyChangeAlert.oldKey + 1} → Key #${keyChangeAlert.newKey + 1}`
              }
            </span>
          </div>
        </div>
      )}

      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">
            {language === 'he' ? 'ניתוח שימוש ב-API' : 'Token Usage'}
          </h2>
          <p className="text-sm text-gray-600 dark:text-green-400/70 mt-1">
            {language === 'he' ? 'עדכון אחרון:' : 'Last updated:'} {lastUpdate.toLocaleTimeString()}
            <span className={`ml-2 text-xs px-2 py-1 rounded transition-all duration-300 ${
              isUpdating 
                ? 'bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' 
                : 'bg-green-100 dark:bg-green-900/20 text-green-600 dark:text-green-400'
            }`}>
              {isUpdating 
                ? (language === 'he' ? 'מעדכן...' : 'Updating...') 
                : (language === 'he' ? 'עדכון אוטומטי' : 'Auto-refresh')
              }
            </span>
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
            disabled={isLoading || isUpdating}
            className="flex items-center gap-2 px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg border border-green-500/30 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading || isUpdating ? 'animate-spin' : ''}`} />
            {language === 'he' ? 'רענן' : 'Refresh'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-green-400/70">
                {language === 'he' ? 'סך כל מפתחות' : 'Total API Keys'}
              </p>
              <p className="text-2xl font-semibold mt-1 text-gray-800 dark:text-green-400">
                {totalKeys}
              </p>
            </div>
            <Server className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-green-400/70">
                {language === 'he' ? 'מפתחות פעילים' : 'Active Keys'}
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
                {language === 'he' ? 'מפתחות לא זמינים' : 'Unavailable Keys'}
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
                {language === 'he' ? 'שימוש היומי' : 'Daily Usage'}
              </p>
              <p className="text-2xl font-semibold mt-1 text-gray-800 dark:text-green-400">
                {totalTokensToday.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 dark:text-green-400/50 mt-1">
                {language === 'he' ? `מ-${activeKeysToday} מפתחות` : `From ${activeKeysToday} keys`}
              </p>
            </div>
            <Coins className="w-8 h-8 text-purple-500" />
          </div>
        </div>

        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-green-400/70">
                {language === 'he' ? 'בקשות יומיות' : 'Daily Requests'}
              </p>
              <p className="text-2xl font-semibold mt-1 text-gray-800 dark:text-green-400">
                {totalRequestsToday.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 dark:text-green-400/50 mt-1">
                {language === 'he' ? `מ-${activeKeysToday} מפתחות` : `From ${activeKeysToday} keys`}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-orange-500" />
          </div>
        </div>
      </div>

      {currentKey && (
        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-6 shadow-lg">
          <h3 className="text-lg font-semibold text-green-600 dark:text-green-400 mb-4">
            {language === 'he' ? 'המפתח הפעיל כרגע' : 'Currently Active API Key'}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="w-5 h-5 text-blue-500" />
                <span className="font-medium text-blue-700 dark:text-blue-400">
                  {language === 'he' ? `מפתח פעיל #${currentKey.id}` : `Active Key #${currentKey.id}`}
                  {currentKey.key_name && (
                    <span className="text-xs text-blue-500 dark:text-blue-300 block mt-1">
                      {currentKey.key_name.replace('GEMINI_API_KEY_', 'AI Key ')}
                    </span>
                  )}
                </span>
              </div>
              <p className="text-2xl font-bold text-blue-700 dark:text-blue-400">
                {currentKey.tokens_today?.toLocaleString() || 'N/A'}
              </p>
              <p className="text-sm text-blue-600 dark:text-blue-400/70">
                {language === 'he' ? 'טוקנים שנוצלו היום' : 'Tokens used today'}
              </p>
            </div>
            
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-5 h-5 text-green-500" />
                <span className="font-medium text-green-700 dark:text-green-400">
                  {language === 'he' ? 'דקה נוכחית' : 'Current Minute'}
                </span>
              </div>
              <p className="text-2xl font-bold text-green-700 dark:text-green-400">
                {currentKey.tokens_current_minute || 0}
              </p>
              <p className="text-sm text-green-600 dark:text-green-400/70">
                {language === 'he' ? 'טוקנים בדקה זו' : 'Tokens this minute'}
              </p>
            </div>
            
            <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="w-5 h-5 text-orange-500" />
                <span className="font-medium text-orange-700 dark:text-orange-400">
                  {language === 'he' ? 'בקשות היום' : 'Requests Today'}
                </span>
              </div>
              <p className="text-2xl font-bold text-orange-700 dark:text-orange-400">
                {currentKey.requests_today?.toLocaleString() || 0}
              </p>
              <p className="text-sm text-orange-600 dark:text-orange-400/70">
                {language === 'he' ? 'סך הבקשות היום' : 'Total requests today'}
              </p>
            </div>
            
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5 text-purple-500" />
                <span className="font-medium text-purple-700 dark:text-purple-400">
                  {language === 'he' ? 'בקשות/דקה' : 'Requests/Min'}
                </span>
              </div>
              <p className="text-2xl font-bold text-purple-700 dark:text-purple-400">
                {currentKey.requests_current_minute || 0}
              </p>
              <p className="text-sm text-purple-600 dark:text-purple-400/70">
                {language === 'he' ? 'בקשות בדקה זו' : 'Requests this minute'}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 shadow-lg">
        <div className="border-b border-gray-300 dark:border-green-500/20 py-3 px-6">
          <h3 className="text-lg font-semibold text-green-600 dark:text-green-400">
            {language === 'he' ? 'סטטוס מפתחות המערכת' : 'System Keys Status'}
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
                  {language === 'he' ? 'בקשות היום' : 'Requests Today'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-green-400/70 uppercase tracking-wider">
                  {language === 'he' ? 'טוקנים/דקה' : 'Tokens/Min'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-green-400/70 uppercase tracking-wider">
                  {language === 'he' ? 'בקשות/דקה' : 'Requests/Min'}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-green-500/20">
              {keyData.map((key) => (
                <tr key={key.id} className="hover:bg-gray-50 dark:hover:bg-green-500/5">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm font-medium text-gray-900 dark:text-green-400">
                      Key #{key.id}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(key.status)}
                      <span className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(key.status)}`}>
                        {getStatusText(key.status)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-green-400">
                    {key.tokens_today?.toLocaleString() || (language === 'he' ? 'לא זמין' : 'N/A')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-green-400">
                    {key.requests_today?.toLocaleString() || (language === 'he' ? 'לא זמין' : 'N/A')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-green-400">
                    {key.tokens_current_minute ?? (language === 'he' ? 'לא זמין' : 'N/A')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-green-400">
                    {key.requests_current_minute ?? (language === 'he' ? 'לא זמין' : 'N/A')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
});

export default TokenUsageAnalytics;
