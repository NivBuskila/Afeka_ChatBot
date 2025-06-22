import React, { useState, useEffect, useCallback, useRef } from "react";
import { useTranslation } from "react-i18next";
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
  Server,
  Timer,
  ArrowRight,
  ArrowLeft,
  Zap,
} from "lucide-react";

interface TokenUsageAnalyticsProps {
  language: string;
}

interface KeyStatus {
  id: number;
  status: 'available' | 'blocked' | 'cooldown' | 'error' | 'current';
  is_current: boolean;
  tokens_today: number;
  requests_today: number;
  tokens_current_minute: number;
  requests_current_minute: number;
  next_reset: string;
  last_used?: string;
  first_used_today?: string;
  key_name?: string;
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
  const [managementStatus, setManagementStatus] =
    useState<KeyManagementStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [keyChangeAlert, setKeyChangeAlert] = useState<{
    show: boolean;
    oldKey: number;
    newKey: number;
  } | null>(null);
  
  // אינדיקטור לcountdown עד הרענון הבא
  const [nextRefreshIn, setNextRefreshIn] = useState<number>(15);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const countdownRef = useRef<NodeJS.Timeout | null>(null);
  const autoRefreshEnabledRef = useRef<boolean>(true);

  // פונקציה לניקוי intervals
  const clearIntervals = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    if (countdownRef.current) {
      clearInterval(countdownRef.current);
      countdownRef.current = null;
    }
  }, []);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden && autoRefreshEnabledRef.current) {
        fetchData(false);
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      clearIntervals();
    };
  }, [clearIntervals]);

  const fetchData = useCallback(async (isInitialLoad = false) => {
    try {
      if (isInitialLoad) {
        setIsLoading(true);
      } else {
        setIsUpdating(true);
      }

      setError(null);

      const BACKEND_URL =
        import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000);
      const response = await fetch(`${BACKEND_URL}/api/keys/`, {
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.status === "ok" && data.key_management) {
        const keyManagement = data.key_management;

        const prevCurrentKey = managementStatus?.current_key_index;

        setManagementStatus(keyManagement);

        const transformedKeys: KeyStatus[] = keyManagement.keys_status.map(
          (keyStatus: any) => {
            return {
              id: keyStatus.id + 1,
              status: keyStatus.status,
              is_current: keyStatus.is_current,
              tokens_today: keyStatus.tokens_today || 0,
              requests_today: keyStatus.requests_today || 0,
              tokens_current_minute: keyStatus.tokens_current_minute || 0,
              requests_current_minute: keyStatus.requests_current_minute || 0,
              next_reset: new Date(
                Date.now() + 8 * 60 * 60 * 1000
              ).toISOString(),
              last_used: keyStatus.last_used,
              first_used_today: keyStatus.first_used_today,
            };
          }
        );

        setKeyData(transformedKeys);

        // 🔧 בדיקה משופרת לחלפת מפתח - רק אם באמת השתנה
        if (
          prevCurrentKey !== undefined &&
          prevCurrentKey !== keyManagement.current_key_index &&
          managementStatus !== null // ודא שזה לא הטעינה הראשונה
        ) {
          // Key switched - אינדיקטור משופר
          setKeyChangeAlert({
            show: true,
            oldKey: prevCurrentKey,
            newKey: keyManagement.current_key_index,
          });

          // סגירה אוטומטית אחרי 6 שניות במקום 8
          setTimeout(() => {
            setKeyChangeAlert(null);
          }, 6000);
        }
      } else {
        throw new Error("Invalid response format from key status API");
      }

      setLastUpdate(new Date());
      // איפוס הcountdown אחרי רענון מוצלח
      setNextRefreshIn(15);
      autoRefreshEnabledRef.current = true;
      
    } catch (error) {
      console.error(
        "❌ [DASHBOARD-ERROR] Failed to fetch token usage data:",
        error
      );
      
      // 🔧 טיפול משופר בשגיאות עם תמיכה בעברית
      if ((error as any)?.name === 'AbortError') {
        setError(
          language === "he" 
            ? "פגת זמן לבקשה אחרי 15 שניות. רענון אוטומטי ממשיך..."
            : "Request timed out after 15 seconds. Auto-refresh continues..."
        );
      } else if ((error as any)?.message && (error as any).message.includes('NetworkError')) {
        setError(
          language === "he"
            ? "בעיית חיבור רשת. מנסה שוב אוטומטית..."
            : "Network connection issue. Retrying automatically..."
        );
      } else if ((error as any)?.message && (error as any).message.includes('fetch')) {
        setError(
          language === "he"
            ? "שגיאת חיבור. רענון אוטומטי פעיל..."
            : "Connection error. Auto-refresh is active..."
        );
      } else {
        setError(
          language === "he"
            ? "כשל בטעינת נתונים. רענון אוטומטי ממשיך..."
            : "Failed to load data. Auto-refresh continues..."
        );
      }
      
      // אל תעצור את הauto-refresh גם במקרה של שגיאות
      autoRefreshEnabledRef.current = true;
      
    } finally {
      if (isInitialLoad) {
        setIsLoading(false);
      } else {
        setIsUpdating(false);
      }
    }
  }, [managementStatus?.current_key_index]);

  // auto-refresh משופר עם countdown
  useEffect(() => {
    fetchData(true); // Initial load

    // Auto-refresh מתקדם יותר
    const startAutoRefresh = () => {
      clearIntervals();
      
      // Main refresh interval
      intervalRef.current = setInterval(() => {
        if (autoRefreshEnabledRef.current && !document.hidden) {
          fetchData(false);
        }
      }, 15000); // כל 15 שניות

      // Countdown timer
      countdownRef.current = setInterval(() => {
        setNextRefreshIn(prev => {
          if (prev <= 1) {
            return 15; // Reset countdown
          }
          return prev - 1;
        });
      }, 1000); // כל שנייה
    };

    startAutoRefresh();

    return () => {
      clearIntervals();
    };
  }, [fetchData, clearIntervals]);

  const handleRefresh = () => {
    // איפוס הcountdown ו-force refresh
    setNextRefreshIn(15);
    fetchData(true);
  };

  const handleExportCSV = () => {
    if (!managementStatus) return;

    const csvData = keyData.map((key) => ({
      "Key ID": `Key #${key.id}`,
      Status: key.status,
      "Is Current": key.is_current ? "Yes" : "No",
      "Tokens Today": key.tokens_today || "N/A",
      "Tokens/Min": key.tokens_current_minute || "N/A",
      "Requests/Min": key.requests_current_minute || "N/A",
      "Next Reset": new Date(key.next_reset).toLocaleTimeString(),
    }));

    const csv = [
      Object.keys(csvData[0]).join(","),
      ...csvData.map((row) => Object.values(row).join(",")),
    ].join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `token-usage-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "current":
        return <Activity className="w-4 h-4 text-blue-500" />;
      case "available":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "blocked":
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "current":
        return "text-blue-500 bg-blue-100 dark:bg-blue-900/20";
      case "available":
        return "text-green-500 bg-green-100 dark:bg-green-900/20";
      case "blocked":
        return "text-red-500 bg-red-100 dark:bg-red-900/20";
      default:
        return "text-yellow-500 bg-yellow-100 dark:bg-yellow-900/20";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "current":
        return language === "he" ? "נוכחי" : "Current";
      case "available":
        return language === "he" ? "זמין" : "Available";
      case "blocked":
        return language === "he" ? "חסום" : "Blocked";
      default:
        return status;
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex flex-col justify-center items-center h-40">
          <RefreshCw className="w-8 h-8 animate-spin text-green-400 mb-4" />
          <p className="text-green-400 text-sm">
            {language === "he" ? "טוען נתוני API..." : "Loading API data..."}
          </p>
          <p className="text-green-400/50 text-xs mt-1">
            {language === "he" ? "זה יכול לקחת כמה שניות..." : "This may take a few seconds..."}
          </p>
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
          <div className="flex items-center justify-between mt-3">
            <button
              onClick={handleRefresh}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              {language === "he" ? "נסה שוב" : "Try Again"}
            </button>
            <div className="flex items-center text-xs text-red-600 dark:text-red-400">
              <Timer className="w-3 h-3 mr-1" />
              {language === "he" 
                ? `רענון אוטומטי בעוד ${nextRefreshIn}ש`
                : `Auto-refresh in ${nextRefreshIn}s`}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!managementStatus) {
    return (
      <div className="p-6">
        <div className="text-center text-gray-500 dark:text-green-400/50">
          {language === "he" ? "אין נתונים זמינים" : "No data available"}
        </div>
      </div>
    );
  }

  const totalKeys = managementStatus.total_keys;
  const availableKeys = managementStatus.available_keys;
  const blockedKeys = totalKeys - availableKeys;

  // השתמש בנתונים החדשים מהבקאנד
  const currentKey = managementStatus.current_key_usage
    ? {
        id: managementStatus.current_key_usage.current_key_index + 1,
        tokens_today: managementStatus.current_key_usage.tokens_today,
        tokens_current_minute:
          managementStatus.current_key_usage.tokens_current_minute,
        requests_today: managementStatus.current_key_usage.requests_today,
        requests_current_minute:
          managementStatus.current_key_usage.requests_current_minute,
        status: managementStatus.current_key_usage.status,
        key_name: managementStatus.current_key_usage.key_name,
      }
    : keyData.find((k) => k.is_current);

  const totalTokensToday = keyData.reduce(
    (sum, key) => sum + (key.tokens_today || 0),
    0
  );
  const totalRequestsToday = keyData.reduce(
    (sum, key) => sum + (key.requests_today || 0),
    0
  );

  const activeKeysToday = keyData.filter(
    (k) => (k.tokens_today || 0) > 0 || (k.requests_today || 0) > 0
  ).length;

  return (
    <div className="p-6 space-y-6">
      {/* 🎨 אינדיקטור משופר לחלפת מפתחות */}
      {keyChangeAlert?.show && (
        <div className="bg-gradient-to-r from-blue-50 to-green-50 dark:from-blue-900/20 dark:to-green-900/20 border border-blue-200 dark:border-blue-500/30 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="flex items-center bg-blue-100 dark:bg-blue-900/30 rounded-full p-2 mr-3">
                <Zap className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-blue-800 dark:text-blue-300 font-medium text-sm">
                  {language === "he" ? "מפתח הוחלף אוטומטית" : "API Key Auto-Switched"}
                </p>
                <div className="flex items-center text-blue-600 dark:text-blue-400 text-xs mt-1">
                  <span className="font-mono bg-blue-100 dark:bg-blue-900/30 px-2 py-1 rounded">
                    Key #{keyChangeAlert.oldKey + 1}
                  </span>
                  {language === "he" ? (
                    <ArrowLeft className="w-3 h-3 mx-2" />
                  ) : (
                    <ArrowRight className="w-3 h-3 mx-2" />
                  )}
                  <span className="font-mono bg-green-100 dark:bg-green-900/30 px-2 py-1 rounded text-green-600 dark:text-green-400">
                    Key #{keyChangeAlert.newKey + 1}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center text-xs text-blue-500 dark:text-blue-400">
              <Activity className="w-3 h-3 mr-1 animate-spin" />
              {language === "he" ? "פעיל" : "Active"}
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">
            {language === "he" ? "ניתוח שימוש ב-API" : "Token Usage"}
          </h2>
          <div className="flex items-center gap-4 mt-1">
            <p className="text-sm text-gray-600 dark:text-green-400/70">
              {language === "he" ? "עדכון אחרון:" : "Last updated:"}{" "}
              {lastUpdate.toLocaleTimeString()}
            </p>
            {/* אינדיקטור חזותי משופר לauto-refresh */}
            <div className="flex items-center gap-2">
              <span
                className={`text-xs px-3 py-1 rounded-full transition-all duration-300 ${
                  isUpdating
                    ? "bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 animate-pulse"
                    : "bg-green-100 dark:bg-green-900/20 text-green-600 dark:text-green-400"
                }`}
              >
                {isUpdating
                  ? language === "he"
                    ? "מעדכן..."
                    : "Updating..."
                  : language === "he"
                  ? "עדכון אוטומטי פעיל"
                  : "Auto-refresh active"}
              </span>
              
              {/* Countdown timer */}
              {!isUpdating && (
                <div className="flex items-center text-xs text-gray-500 dark:text-green-400/50">
                  <Timer className="w-3 h-3 mr-1" />
                  {language === "he" 
                    ? `${nextRefreshIn}ש`
                    : `${nextRefreshIn}s`}
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg border border-blue-500/30 transition-colors"
          >
            <Download className="w-4 h-4" />
            {language === "he" ? "ייצא CSV" : "Export CSV"}
          </button>
          <button
            onClick={handleRefresh}
            disabled={isLoading || isUpdating}
            className="flex items-center gap-2 px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg border border-green-500/30 transition-colors disabled:opacity-50"
          >
            <RefreshCw
              className={`w-4 h-4 ${
                isLoading || isUpdating ? "animate-spin" : ""
              }`}
            />
            {language === "he" ? "רענן" : "Refresh"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-green-400/70">
                {language === "he" ? "סך כל מפתחות" : "Total API Keys"}
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
                {language === "he" ? "מפתחות פעילים" : "Active Keys"}
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
                {language === "he" ? "מפתחות לא זמינים" : "Unavailable Keys"}
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
                {language === "he" ? "שימוש היומי" : "Daily Usage"}
              </p>
              <p className="text-2xl font-semibold mt-1 text-gray-800 dark:text-green-400">
                {totalTokensToday.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 dark:text-green-400/50 mt-1">
                {language === "he"
                  ? `מ-${activeKeysToday} מפתחות`
                  : `From ${activeKeysToday} keys`}
              </p>
            </div>
            <Coins className="w-8 h-8 text-purple-500" />
          </div>
        </div>

        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-green-400/70">
                {language === "he" ? "בקשות יומיות" : "Daily Requests"}
              </p>
              <p className="text-2xl font-semibold mt-1 text-gray-800 dark:text-green-400">
                {totalRequestsToday.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 dark:text-green-400/50 mt-1">
                {language === "he"
                  ? `מ-${activeKeysToday} מפתחות`
                  : `From ${activeKeysToday} keys`}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-orange-500" />
          </div>
        </div>
      </div>

      {currentKey && (
        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-6 shadow-lg">
          <h3 className="text-lg font-semibold text-green-600 dark:text-green-400 mb-4">
            {language === "he"
              ? "המפתח הפעיל כרגע"
              : "Currently Active API Key"}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="w-5 h-5 text-blue-500" />
                <span className="font-medium text-blue-700 dark:text-blue-400">
                  {language === "he"
                    ? `מפתח פעיל #${currentKey.id}`
                    : `Active Key #${currentKey.id}`}
                  {currentKey.key_name && (
                    <span className="text-xs text-blue-500 dark:text-blue-300 block mt-1">
                      {currentKey.key_name.replace(
                        "GEMINI_API_KEY_",
                        "AI Key "
                      )}
                    </span>
                  )}
                </span>
              </div>
              <p className="text-2xl font-bold text-blue-700 dark:text-blue-400">
                {currentKey.tokens_today?.toLocaleString() || "N/A"}
              </p>
              <p className="text-sm text-blue-600 dark:text-blue-400/70">
                {language === "he" ? "טוקנים שנוצלו היום" : "Tokens used today"}
              </p>
            </div>

            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-5 h-5 text-green-500" />
                <span className="font-medium text-green-700 dark:text-green-400">
                  {language === "he" ? "דקה נוכחית" : "Current Minute"}
                </span>
              </div>
              <p className="text-2xl font-bold text-green-700 dark:text-green-400">
                {currentKey.tokens_current_minute || 0}
              </p>
              <p className="text-sm text-green-600 dark:text-green-400/70">
                {language === "he" ? "טוקנים בדקה זו" : "Tokens this minute"}
              </p>
            </div>

            <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="w-5 h-5 text-orange-500" />
                <span className="font-medium text-orange-700 dark:text-orange-400">
                  {language === "he" ? "בקשות היום" : "Requests Today"}
                </span>
              </div>
              <p className="text-2xl font-bold text-orange-700 dark:text-orange-400">
                {currentKey.requests_today?.toLocaleString() || 0}
              </p>
              <p className="text-sm text-orange-600 dark:text-orange-400/70">
                {language === "he" ? "סך הבקשות היום" : "Total requests today"}
              </p>
            </div>

            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5 text-purple-500" />
                <span className="font-medium text-purple-700 dark:text-purple-400">
                  {language === "he" ? "בקשות/דקה" : "Requests/Min"}
                </span>
              </div>
              <p className="text-2xl font-bold text-purple-700 dark:text-purple-400">
                {currentKey.requests_current_minute || 0}
              </p>
              <p className="text-sm text-purple-600 dark:text-purple-400/70">
                {language === "he" ? "בקשות בדקה זו" : "Requests this minute"}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 shadow-lg">
        <div className="border-b border-gray-300 dark:border-green-500/20 py-3 px-6">
          <h3 className="text-lg font-semibold text-green-600 dark:text-green-400">
            {language === "he" ? "סטטוס מפתחות המערכת" : "System Keys Status"}
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-black/20">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-green-400/70 uppercase tracking-wider">
                  {language === "he" ? "מפתח" : "Key ID"}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-green-400/70 uppercase tracking-wider">
                  {language === "he" ? "סטטוס" : "Status"}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-green-400/70 uppercase tracking-wider">
                  {language === "he" ? "טוקנים היום" : "Tokens Today"}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-green-400/70 uppercase tracking-wider">
                  {language === "he" ? "בקשות היום" : "Requests Today"}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-green-400/70 uppercase tracking-wider">
                  {language === "he" ? "טוקנים/דקה" : "Tokens/Min"}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-green-400/70 uppercase tracking-wider">
                  {language === "he" ? "בקשות/דקה" : "Requests/Min"}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-green-500/20">
              {keyData.map((key) => (
                <tr
                  key={key.id}
                  className="hover:bg-gray-50 dark:hover:bg-green-500/5"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm font-medium text-gray-900 dark:text-green-400">
                      Key #{key.id}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(key.status)}
                      <span
                        className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(
                          key.status
                        )}`}
                      >
                        {getStatusText(key.status)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-green-400">
                    {key.tokens_today?.toLocaleString() ||
                      (language === "he" ? "לא זמין" : "N/A")}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-green-400">
                    {key.requests_today?.toLocaleString() ||
                      (language === "he" ? "לא זמין" : "N/A")}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-green-400">
                    {key.tokens_current_minute ??
                      (language === "he" ? "לא זמין" : "N/A")}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-green-400">
                    {key.requests_current_minute ??
                      (language === "he" ? "לא זמין" : "N/A")}
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

TokenUsageAnalytics.displayName = 'TokenUsageAnalytics';

export default TokenUsageAnalytics;
