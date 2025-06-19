import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { cacheService } from '../../../src/services/cacheService'

// Mock Supabase
vi.mock('../../../src/config/supabase', () => ({
  supabase: {
    removeAllChannels: vi.fn(),
  },
}))

// Get reference to mocked Supabase after mock is set up
const { supabase: mockSupabase } = await import('../../../src/config/supabase')

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key]
    }),
    clear: vi.fn(() => {
      store = {}
    }),
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

// Mock console methods - will be set up in beforeEach
let consoleLogSpy: ReturnType<typeof vi.spyOn>
let consoleErrorSpy: ReturnType<typeof vi.spyOn>

describe('🗂️ CacheService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.clear()
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2024-01-01T10:00:00Z'))
    
    // Set up console spies fresh for each test
    consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.useRealTimers()
    consoleLogSpy?.mockRestore()
    consoleErrorSpy?.mockRestore()
    vi.restoreAllMocks()
  })

  describe('📄 Documents Cache Invalidation', () => {
    it('should invalidate documents cache successfully', async () => {
      mockSupabase.removeAllChannels.mockResolvedValue(undefined)

      await cacheService.invalidateDocumentsCache()

      expect(mockSupabase.removeAllChannels).toHaveBeenCalled()
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'documents_cache_invalidated',
        '2024-01-01T10:00:00.000Z'
      )
      expect(consoleLogSpy).toHaveBeenCalledWith(
        'Documents cache invalidated at',
        '2024-01-01T10:00:00.000Z'
      )
    })

    it('should handle errors when invalidating documents cache', async () => {
      const error = new Error('Supabase connection failed')
      mockSupabase.removeAllChannels.mockRejectedValue(error)

      await cacheService.invalidateDocumentsCache()

      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Failed to invalidate documents cache:',
        error
      )
      expect(localStorageMock.setItem).not.toHaveBeenCalled()
    })

    it('should continue execution even if removeAllChannels fails', async () => {
      mockSupabase.removeAllChannels.mockRejectedValue(new Error('Connection error'))

      // Should not throw
      await expect(cacheService.invalidateDocumentsCache()).resolves.toBeUndefined()
    })
  })

  describe('🔄 Generic Cache Invalidation', () => {
    it('should invalidate cache for specific entity type', async () => {
      mockSupabase.removeAllChannels.mockResolvedValue(undefined)

      await cacheService.invalidateCache('users')

      expect(mockSupabase.removeAllChannels).toHaveBeenCalled()
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'users_cache_invalidated',
        '2024-01-01T10:00:00.000Z'
      )
      expect(consoleLogSpy).toHaveBeenCalledWith(
        'users cache invalidated at',
        '2024-01-01T10:00:00.000Z'
      )
    })

    it('should handle different entity types', async () => {
      mockSupabase.removeAllChannels.mockResolvedValue(undefined)

      await cacheService.invalidateCache('analytics')

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'analytics_cache_invalidated',
        '2024-01-01T10:00:00.000Z'
      )
      expect(consoleLogSpy).toHaveBeenCalledWith(
        'analytics cache invalidated at',
        '2024-01-01T10:00:00.000Z'
      )
    })

    it('should handle empty entity type', async () => {
      mockSupabase.removeAllChannels.mockResolvedValue(undefined)

      await cacheService.invalidateCache('')

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        '_cache_invalidated',
        '2024-01-01T10:00:00.000Z'
      )
    })

    it('should handle special characters in entity type', async () => {
      mockSupabase.removeAllChannels.mockResolvedValue(undefined)

      await cacheService.invalidateCache('chat-sessions')

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'chat-sessions_cache_invalidated',
        '2024-01-01T10:00:00.000Z'
      )
    })

    it('should handle errors when invalidating generic cache', async () => {
      const error = new Error('Cache invalidation failed')
      mockSupabase.removeAllChannels.mockRejectedValue(error)

      await cacheService.invalidateCache('documents')

      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Failed to invalidate documents cache:',
        error
      )
    })
  })

  describe('🕒 Cache Staleness Checking', () => {
    it('should return true when no cache timestamp exists', () => {
      localStorageMock.getItem.mockReturnValue(null)

      const isStale = cacheService.isCacheStale('documents')

      expect(isStale).toBe(true)
      expect(localStorageMock.getItem).toHaveBeenCalledWith('documents_cache_invalidated')
    })

    it('should return false when cache is fresh (within default time)', () => {
      // Set cache timestamp to 30 seconds ago
      const thirtySecondsAgo = new Date('2024-01-01T09:59:30Z').toISOString()
      localStorageMock.getItem.mockReturnValue(thirtySecondsAgo)

      const isStale = cacheService.isCacheStale('documents')

      expect(isStale).toBe(false)
    })

    it('should return true when cache exceeds default max age (60 seconds)', () => {
      // Set cache timestamp to 2 minutes ago
      const twoMinutesAgo = new Date('2024-01-01T09:58:00Z').toISOString()
      localStorageMock.getItem.mockReturnValue(twoMinutesAgo)

      const isStale = cacheService.isCacheStale('documents')

      expect(isStale).toBe(true)
    })

    it('should use custom max age parameter', () => {
      // Set cache timestamp to 5 seconds ago
      const fiveSecondsAgo = new Date('2024-01-01T09:59:55Z').toISOString()
      localStorageMock.getItem.mockReturnValue(fiveSecondsAgo)

      // With 10 second max age - should be fresh
      const isStaleWith10s = cacheService.isCacheStale('documents', 10000)
      expect(isStaleWith10s).toBe(false)

      // With 3 second max age - should be stale
      const isStaleWith3s = cacheService.isCacheStale('documents', 3000)
      expect(isStaleWith3s).toBe(true)
    })

    it('should handle different entity types for staleness check', () => {
      const now = new Date('2024-01-01T10:00:00Z').toISOString()
      
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'users_cache_invalidated') return now
        if (key === 'documents_cache_invalidated') return null
        return null
      })

      expect(cacheService.isCacheStale('users')).toBe(false)
      expect(cacheService.isCacheStale('documents')).toBe(true)
    })

    it('should handle invalid timestamp gracefully', () => {
      localStorageMock.getItem.mockReturnValue('invalid-date')

      // Invalid date results in NaN which makes the comparison always true
      const isStale = cacheService.isCacheStale('documents')

      expect(isStale).toBe(false) // NaN comparisons in JS return false
    })

    it('should handle edge case of exactly max age', () => {
      // Set cache timestamp to exactly 60 seconds ago
      const exactlyMaxAge = new Date('2024-01-01T09:59:00Z').toISOString()
      localStorageMock.getItem.mockReturnValue(exactlyMaxAge)

      const isStale = cacheService.isCacheStale('documents', 60000)

      expect(isStale).toBe(false) // Exactly at max age should still be fresh
    })

    it('should handle very large max age values', () => {
      const oneHourAgo = new Date('2024-01-01T09:00:00Z').toISOString()
      localStorageMock.getItem.mockReturnValue(oneHourAgo)

      // 24 hour max age
      const isStale = cacheService.isCacheStale('documents', 24 * 60 * 60 * 1000)

      expect(isStale).toBe(false)
    })

    it('should handle zero max age', () => {
      const now = new Date('2024-01-01T10:00:00Z').toISOString()
      localStorageMock.getItem.mockReturnValue(now)

      const isStale = cacheService.isCacheStale('documents', 0)

      expect(isStale).toBe(false) // Same timestamp means 0 difference, not > 0
    })
  })

  describe('🔧 Integration Scenarios', () => {
    it('should complete full cache lifecycle', async () => {
      // Initial state - cache is stale
      expect(cacheService.isCacheStale('test-entity')).toBe(true)

      // Invalidate cache
      mockSupabase.removeAllChannels.mockResolvedValue(undefined)
      await cacheService.invalidateCache('test-entity')

      // Cache should now be fresh
      expect(cacheService.isCacheStale('test-entity')).toBe(false)

      // Move time forward beyond max age
      vi.setSystemTime(new Date('2024-01-01T10:02:00Z')) // 2 minutes later

      // Cache should be stale again
      expect(cacheService.isCacheStale('test-entity')).toBe(true)
    })

    it('should handle multiple entity types independently', async () => {
      mockSupabase.removeAllChannels.mockResolvedValue(undefined)

      // Invalidate different entities at different times
      await cacheService.invalidateCache('users')
      
      vi.setSystemTime(new Date('2024-01-01T10:00:30Z')) // 30 seconds later
      await cacheService.invalidateCache('documents')

      vi.setSystemTime(new Date('2024-01-01T10:01:00Z')) // 1 minute from start

      // Users cache should be stale (1 minute old), documents should be fresh (30 seconds old)
      expect(cacheService.isCacheStale('users', 50000)).toBe(true) // 50 second max age
      expect(cacheService.isCacheStale('documents', 50000)).toBe(false) // 50 second max age
    })

    it('should maintain consistency between generic and specific invalidation', async () => {
      mockSupabase.removeAllChannels.mockResolvedValue(undefined)

      // Both should call the same underlying mechanism
      await cacheService.invalidateDocumentsCache()
      const documentsTimestamp = localStorageMock.setItem.mock.calls[0][1]

      localStorageMock.setItem.mockClear()
      
      await cacheService.invalidateCache('documents')
      const genericTimestamp = localStorageMock.setItem.mock.calls[0][1]

      // Both should set timestamps (though they might be slightly different due to execution time)
      expect(documentsTimestamp).toBeTruthy()
      expect(genericTimestamp).toBeTruthy()
    })
  })
}) 