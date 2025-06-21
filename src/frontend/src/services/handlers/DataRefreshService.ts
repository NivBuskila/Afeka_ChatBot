import { documentService } from '../documentService';
import { analyticsService } from '../analyticsService';
import type { Document } from '../../config/supabase';

export interface DataRefreshCallbacks {
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
  onDocumentsUpdate: (documents: Document[]) => void;
  onAnalyticsUpdate: (analytics: any) => void;
  onInitialLoadingChange: (loading: boolean) => void;
  onRefreshingChange: (refreshing: boolean) => void;
}

export class DataRefreshService {
  constructor(private callbacks: DataRefreshCallbacks) {}

  /**
   * Fetches all initial data (documents + analytics)
   */
  async fetchInitialData(): Promise<void> {
    try {
      this.callbacks.onInitialLoadingChange(true);

      const [docs, analyticsData] = await Promise.all([
        documentService.getAllDocuments(),
        analyticsService.getDashboardAnalytics(),
      ]);

      this.callbacks.onDocumentsUpdate(docs);
      this.callbacks.onAnalyticsUpdate(analyticsData);
    } catch (error) {
      console.error('Error fetching initial data:', error);
      this.callbacks.onError('שגיאה בטעינת הנתונים הראשוניים');
    } finally {
      this.callbacks.onInitialLoadingChange(false);
    }
  }

  /**
   * Fetches only analytics data (for performance)
   */
  async fetchAnalyticsOnly(): Promise<void> {
    try {
      this.callbacks.onRefreshingChange(true);
      const analyticsData = await analyticsService.getDashboardAnalytics();
      this.callbacks.onAnalyticsUpdate(analyticsData);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      this.callbacks.onError('שגיאה בטעינת נתוני האנליטיקה');
    } finally {
      this.callbacks.onRefreshingChange(false);
    }
  }

  /**
   * Manual refresh of all data with user feedback
   */
  async refreshAllData(): Promise<void> {
    try {
      this.callbacks.onRefreshingChange(true);
      
      const [docs, analyticsData] = await Promise.all([
        documentService.getAllDocuments(),
        analyticsService.getDashboardAnalytics(),
      ]);

      this.callbacks.onDocumentsUpdate(docs);
      this.callbacks.onAnalyticsUpdate(analyticsData);
      this.callbacks.onSuccess('הנתונים עודכנו בהצלחה');
    } catch (error) {
      console.error('Error refreshing data:', error);
      this.callbacks.onError('שגיאה ברענון הנתונים');
    } finally {
      this.callbacks.onRefreshingChange(false);
    }
  }

  /**
   * Fetches only documents data
   */
  async fetchDocumentsOnly(): Promise<void> {
    try {
      this.callbacks.onRefreshingChange(true);
      const docs = await documentService.getAllDocuments();
      this.callbacks.onDocumentsUpdate(docs);
    } catch (error) {
      console.error('Error fetching documents:', error);
      this.callbacks.onError('שגיאה בטעינת המסמכים');
    } finally {
      this.callbacks.onRefreshingChange(false);
    }
  }

  /**
   * Invalidates cache and forces fresh data fetch
   */
  async invalidateAndRefresh(): Promise<void> {
    try {
      // Clear any cached data
      localStorage.removeItem('documents_cache');
      localStorage.removeItem('analytics_cache');
      
      // Trigger storage event to notify other components
      window.dispatchEvent(new StorageEvent('storage', {
        key: 'documents_cache_invalidated',
        newValue: Date.now().toString()
      }));

      await this.refreshAllData();
    } catch (error) {
      console.error('Error invalidating cache:', error);
      this.callbacks.onError('שגיאה בעדכון המטמון');
    }
  }

  /**
   * Sets up data refresh listeners for real-time updates
   */
  setupDataListeners(): () => void {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'documents_cache_invalidated') {
        this.fetchInitialData();
      }
    };

    window.addEventListener('storage', handleStorageChange);

    // Return cleanup function
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }

  /**
   * Checks if data is stale and needs refresh
   */
  isDataStale(lastFetch: Date | null, maxAgeMinutes: number = 5): boolean {
    if (!lastFetch) return true;
    
    const now = new Date();
    const diffMinutes = (now.getTime() - lastFetch.getTime()) / (1000 * 60);
    
    return diffMinutes > maxAgeMinutes;
  }

  /**
   * Smart refresh that only fetches if data is stale
   */
  async smartRefresh(lastFetch: Date | null): Promise<void> {
    if (this.isDataStale(lastFetch)) {
      await this.fetchAnalyticsOnly();
    }
  }
} 