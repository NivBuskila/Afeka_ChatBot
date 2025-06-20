import { describe, it, expect } from 'vitest'

// פונקציות עזר שיכולות להיות בקומפוננט
const formatNumber = (num: number): string => {
  return num.toLocaleString()
}

const calculateKeyStats = (keys: any[]) => {
  const activeKeys = keys.filter(k => k.status === 'current' || k.status === 'available')
  const blockedKeys = keys.filter(k => k.status === 'blocked')
  const totalTokens = keys.reduce((sum, key) => sum + (key.tokens_today || 0), 0)
  const totalRequests = keys.reduce((sum, key) => sum + (key.requests_today || 0), 0)
  
  return {
    activeCount: activeKeys.length,
    blockedCount: blockedKeys.length,
    totalTokens,
    totalRequests
  }
}

const shouldSwitchKey = (requestsPerMinute: number, limit: number, margin: number = 0.6): boolean => {
  return requestsPerMinute >= (limit * margin)
}

const getKeyDisplayName = (keyId: number, language: 'he' | 'en') => {
  if (language === 'he') {
    return `מפתח פעיל #${keyId}`
  }
  return `Active Key #${keyId}`
}

const getTitleText = (language: 'he' | 'en') => {
  if (language === 'he') {
    return 'ניטור מערכת הבינה המלאכותית'
  }
  return 'AI System Monitor'
}

describe('Dashboard Utility Functions', () => {
  describe('Number Formatting', () => {
    it('should format numbers with commas', () => {
      expect(formatNumber(1234)).toBe('1,234')
      expect(formatNumber(123456)).toBe('123,456')
      expect(formatNumber(1000000)).toBe('1,000,000')
    })

    it('should handle small numbers', () => {
      expect(formatNumber(123)).toBe('123')
      expect(formatNumber(0)).toBe('0')
    })
  })

  describe('Key Statistics Calculation', () => {
    it('should calculate stats correctly', () => {
      const keys = [
        { status: 'current', tokens_today: 1196, requests_today: 15 },
        { status: 'available', tokens_today: 500, requests_today: 8 },
        { status: 'blocked', tokens_today: 0, requests_today: 0 }
      ]

      const stats = calculateKeyStats(keys)
      
      expect(stats.activeCount).toBe(2)
      expect(stats.blockedCount).toBe(1)
      expect(stats.totalTokens).toBe(1696)
      expect(stats.totalRequests).toBe(23)
    })

    it('should handle missing data', () => {
      const keys = [
        { status: 'current' }, // missing tokens_today and requests_today
        { status: 'available', tokens_today: 100, requests_today: 5 }
      ]

      const stats = calculateKeyStats(keys)
      
      expect(stats.totalTokens).toBe(100)
      expect(stats.totalRequests).toBe(5)
    })
  })

  describe('Key Switching Logic', () => {
    it('should switch at 60% threshold', () => {
      expect(shouldSwitchKey(9, 15)).toBe(true)  // 9 >= 9 (15 * 0.6)
      expect(shouldSwitchKey(8, 15)).toBe(false) // 8 < 9
    })

    it('should work with different margins', () => {
      expect(shouldSwitchKey(5, 10, 0.5)).toBe(true)  // 5 >= 5 (10 * 0.5)
      expect(shouldSwitchKey(4, 10, 0.5)).toBe(false) // 4 < 5
    })
  })

  describe('Text Localization', () => {
    it('should return Hebrew text', () => {
      expect(getKeyDisplayName(8, 'he')).toBe('מפתח פעיל #8')
      expect(getTitleText('he')).toBe('ניטור מערכת הבינה המלאכותית')
    })

    it('should return English text', () => {
      expect(getKeyDisplayName(8, 'en')).toBe('Active Key #8')
      expect(getTitleText('en')).toBe('AI System Monitor')
    })
  })

  describe('Data Validation', () => {
    it('should validate API response structure', () => {
      const response = {
        status: 'ok',
        keys: [
          { id: 8, status: 'current', tokens_today: 1196 }
        ],
        key_management: {
          current_key_index: 0,
          total_keys: 7
        }
      }

      expect(response.status).toBe('ok')
      expect(Array.isArray(response.keys)).toBe(true)
      expect(response.key_management).toBeDefined()
      expect(typeof response.keys[0].id).toBe('number')
    })

    it('should handle empty arrays', () => {
      const stats = calculateKeyStats([])
      
      expect(stats.activeCount).toBe(0)
      expect(stats.blockedCount).toBe(0)
      expect(stats.totalTokens).toBe(0)
      expect(stats.totalRequests).toBe(0)
    })
  })
}) 