import { supabase } from '../config/supabase';

/**
 * Cache service for managing system data
 * Allows clearing specific data after update/delete operations
 */
export const cacheService = {
  /**
   * Clear documents cache in Supabase
   */
  async invalidateDocumentsCache(): Promise<void> {
    try {
      // Clear table cache
      await supabase.removeAllChannels();
      
      // Create timestamp for cleanup
      const timestamp = new Date().toISOString();
      localStorage.setItem('documents_cache_invalidated', timestamp);
    } catch (error) {
      // Silent fail
    }
  },
  
  /**
   * Clear cache for requested entity
   * @param entityType Entity type (documents, users, etc.)
   */
  async invalidateCache(entityType: string): Promise<void> {
    try {
      // Clear table cache
      await supabase.removeAllChannels();
      
      // Create timestamp for cleanup
      const timestamp = new Date().toISOString();
      localStorage.setItem(`${entityType}_cache_invalidated`, timestamp);
    } catch (error) {
      // Silent fail
    }
  },
  
  /**
   * Check if cache was cleared recently
   * @param entityType Entity type
   * @param maxAgeMs Maximum cache age in milliseconds
   */
  isCacheStale(entityType: string, maxAgeMs: number = 60000): boolean {
    const lastInvalidated = localStorage.getItem(`${entityType}_cache_invalidated`);
    if (!lastInvalidated) return true;
    
    const lastInvalidatedTime = new Date(lastInvalidated).getTime();
    const now = Date.now();
    
    return (now - lastInvalidatedTime) > maxAgeMs;
  }
}; 