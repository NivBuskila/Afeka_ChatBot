import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock Supabase
vi.mock('../../../src/config/supabase', () => ({
  supabase: {
    removeAllChannels: vi.fn(),
  },
}));

import { cacheService } from '../../../src/services/cacheService';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

// Mock localStorage globally
vi.stubGlobal('localStorage', localStorageMock);

// Get the mocked Supabase instance
const { supabase: mockSupabase } = await vi.importMock('../../../src/config/supabase');

describe('cacheService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  describe('invalidateDocumentsCache', () => {
    it('should invalidate documents cache successfully', async () => {
      const mockDate = new Date('2024-01-01T12:00:00.000Z');
      vi.setSystemTime(mockDate);

      mockSupabase.removeAllChannels.mockResolvedValue(undefined);

      await cacheService.invalidateDocumentsCache();

      expect(mockSupabase.removeAllChannels).toHaveBeenCalled();
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'documents_cache_invalidated',
        '2024-01-01T12:00:00.000Z'
      );
    });

    it('should handle errors gracefully', async () => {
      const mockDate = new Date('2024-01-01T12:00:00.000Z');
      vi.setSystemTime(mockDate);
      
      mockSupabase.removeAllChannels.mockRejectedValue(
        new Error('Connection failed')
      );

      // Should not throw
      await expect(cacheService.invalidateDocumentsCache()).resolves.toBeUndefined();

      // When Supabase fails, localStorage.setItem is NOT called because it's in the try block
      expect(localStorageMock.setItem).not.toHaveBeenCalled();
      
      vi.useRealTimers();
    });
  });

  describe('invalidateCache', () => {
    it('should invalidate cache for specified entity type', async () => {
      const mockDate = new Date('2024-01-01T12:00:00.000Z');
      vi.setSystemTime(mockDate);

      mockSupabase.removeAllChannels.mockResolvedValue(undefined);

      await cacheService.invalidateCache('users');

      expect(mockSupabase.removeAllChannels).toHaveBeenCalled();
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'users_cache_invalidated',
        '2024-01-01T12:00:00.000Z'
      );
    });

    it('should handle different entity types', async () => {
      const entityTypes = ['documents', 'analytics', 'sessions'];

      for (const entityType of entityTypes) {
        await cacheService.invalidateCache(entityType);

        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          `${entityType}_cache_invalidated`,
          expect.any(String)
        );
      }
    });

    it('should handle Supabase errors gracefully', async () => {
      const mockDate = new Date('2024-01-01T12:00:00.000Z');
      vi.setSystemTime(mockDate);
      
      mockSupabase.removeAllChannels.mockRejectedValue(
        new Error('Network error')
      );

      await expect(cacheService.invalidateCache('test')).resolves.toBeUndefined();

      // When Supabase fails, localStorage.setItem is NOT called because it's in the try block
      expect(localStorageMock.setItem).not.toHaveBeenCalled();
      
      vi.useRealTimers();
    });
  });

  describe('isCacheStale', () => {
    it('should return true when no cache timestamp exists', () => {
      localStorageMock.getItem.mockReturnValue(null);

      const result = cacheService.isCacheStale('documents');

      expect(result).toBe(true);
      expect(localStorageMock.getItem).toHaveBeenCalledWith(
        'documents_cache_invalidated'
      );
    });

    it('should return true when cache is older than max age', () => {
      // Current time: 2024-01-01T12:00:00.000Z
      const currentTime = new Date('2024-01-01T12:00:00.000Z');
      vi.setSystemTime(currentTime);

      // Cache was invalidated 2 minutes ago
      const cacheTime = new Date('2024-01-01T11:58:00.000Z');
      localStorageMock.getItem.mockReturnValue(cacheTime.toISOString());

      // Max age is 1 minute (60000ms)
      const result = cacheService.isCacheStale('documents', 60000);

      expect(result).toBe(true);
    });

    it('should return false when cache is within max age', () => {
      // Current time: 2024-01-01T12:00:00.000Z
      const currentTime = new Date('2024-01-01T12:00:00.000Z');
      vi.setSystemTime(currentTime);

      // Cache was invalidated 30 seconds ago
      const cacheTime = new Date('2024-01-01T11:59:30.000Z');
      localStorageMock.getItem.mockReturnValue(cacheTime.toISOString());

      // Max age is 1 minute (60000ms)
      const result = cacheService.isCacheStale('documents', 60000);

      expect(result).toBe(false);
    });

    it('should use default max age of 60 seconds', () => {
      // Current time: 2024-01-01T12:00:00.000Z
      const currentTime = new Date('2024-01-01T12:00:00.000Z');
      vi.setSystemTime(currentTime);

      // Cache was invalidated 2 minutes ago (beyond default 60 seconds)
      const cacheTime = new Date('2024-01-01T11:58:00.000Z');
      localStorageMock.getItem.mockReturnValue(cacheTime.toISOString());

      const result = cacheService.isCacheStale('documents');

      expect(result).toBe(true);
    });

    it('should handle edge case when cache time equals current time', () => {
      const currentTime = new Date('2024-01-01T12:00:00.000Z');
      vi.setSystemTime(currentTime);

      localStorageMock.getItem.mockReturnValue(currentTime.toISOString());

      const result = cacheService.isCacheStale('documents', 60000);

      expect(result).toBe(false);
    });

    it('should handle different entity types correctly', () => {
      const currentTime = new Date('2024-01-01T12:00:00.000Z');
      vi.setSystemTime(currentTime);

      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'users_cache_invalidated') {
          return new Date('2024-01-01T11:59:30.000Z').toISOString(); // Fresh
        }
        if (key === 'analytics_cache_invalidated') {
          return new Date('2024-01-01T11:58:00.000Z').toISOString(); // Stale
        }
        return null;
      });

      expect(cacheService.isCacheStale('users', 60000)).toBe(false);
      expect(cacheService.isCacheStale('analytics', 60000)).toBe(true);
      expect(cacheService.isCacheStale('nonexistent', 60000)).toBe(true);
    });

    it('should handle invalid date strings gracefully', () => {
      localStorageMock.getItem.mockReturnValue('invalid-date');

      const result = cacheService.isCacheStale('documents');

      // When date parsing fails, new Date('invalid-date').getTime() returns NaN
      // and (now - NaN) > maxAgeMs is always false, so function returns false
      expect(result).toBe(false);
    });
  });

  describe('integration scenarios', () => {
    it('should handle complete cache invalidation and staleness check cycle', async () => {
      const startTime = new Date('2024-01-01T12:00:00.000Z');
      vi.setSystemTime(startTime);

      // Initially cache should be stale
      localStorageMock.getItem.mockReturnValue(null);
      expect(cacheService.isCacheStale('documents')).toBe(true);

      // Invalidate cache
      await cacheService.invalidateCache('documents');

      // Mock that localStorage now has the timestamp
      localStorageMock.getItem.mockReturnValue(startTime.toISOString());

      // Should not be stale immediately after invalidation
      expect(cacheService.isCacheStale('documents', 60000)).toBe(false);

      // Move time forward beyond max age
      const laterTime = new Date('2024-01-01T12:02:00.000Z');
      vi.setSystemTime(laterTime);

      // Should now be stale
      expect(cacheService.isCacheStale('documents', 60000)).toBe(true);
    });

    it('should handle multiple entity types independently', async () => {
      const baseTime = new Date('2024-01-01T12:00:00.000Z');
      vi.setSystemTime(baseTime);

      // Invalidate different entities at different times
      await cacheService.invalidateCache('documents');

      vi.setSystemTime(new Date('2024-01-01T12:01:00.000Z'));
      await cacheService.invalidateCache('users');

      // Mock localStorage to return different timestamps
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'documents_cache_invalidated') {
          return baseTime.toISOString();
        }
        if (key === 'users_cache_invalidated') {
          return new Date('2024-01-01T12:01:00.000Z').toISOString();
        }
        return null;
      });

      // Check staleness at different time
      vi.setSystemTime(new Date('2024-01-01T12:01:30.000Z'));

      expect(cacheService.isCacheStale('documents', 60000)).toBe(true); // 90 seconds old
      expect(cacheService.isCacheStale('users', 60000)).toBe(false); // 30 seconds old
    });
  });
}); 