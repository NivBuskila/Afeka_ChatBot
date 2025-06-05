import { supabase } from '../config/supabase';

/**
 * שירות מטמון לניהול נתונים במערכת
 * מאפשר ניקוי נתונים ספציפיים במערכת לאחר פעולות עדכון/מחיקה
 */
export const cacheService = {
  /**
   * נקה את המטמון של המסמכים בסופאבייס
   */
  async invalidateDocumentsCache(): Promise<void> {
    try {
      // Clear table cache
      await supabase.removeAllChannels();
      
      // Create timestamp for cleanup
      const timestamp = new Date().toISOString();
      localStorage.setItem('documents_cache_invalidated', timestamp);
      
      console.log('Documents cache invalidated at', timestamp);
    } catch (error) {
      console.error('Failed to invalidate documents cache:', error);
    }
  },
  
  /**
   * נקה את המטמון של הישות המבוקשת
   * @param entityType סוג הישות (documents, users, וכו')
   */
  async invalidateCache(entityType: string): Promise<void> {
    try {
      // Clear table cache
      await supabase.removeAllChannels();
      
      // Create timestamp for cleanup
      const timestamp = new Date().toISOString();
      localStorage.setItem(`${entityType}_cache_invalidated`, timestamp);
      
      console.log(`${entityType} cache invalidated at`, timestamp);
    } catch (error) {
      console.error(`Failed to invalidate ${entityType} cache:`, error);
    }
  },
  
  /**
   * בדוק אם המטמון נוקה לאחרונה
   * @param entityType סוג הישות
   * @param maxAgeMs גיל מקסימלי של המטמון במילישניות
   */
  isCacheStale(entityType: string, maxAgeMs: number = 60000): boolean {
    const lastInvalidated = localStorage.getItem(`${entityType}_cache_invalidated`);
    if (!lastInvalidated) return true;
    
    const lastInvalidatedTime = new Date(lastInvalidated).getTime();
    const now = Date.now();
    
    return (now - lastInvalidatedTime) > maxAgeMs;
  }
}; 