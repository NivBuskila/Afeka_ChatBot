import { describe, it, expect } from 'vitest'

describe('Dashboard Logic Tests', () => {
  // טסט פונקציות חישוב טוקנים
  describe('Token Calculations', () => {
    it('should calculate total tokens correctly', () => {
      const keys = [
        { tokens_today: 1196, requests_today: 15 },
        { tokens_today: 500, requests_today: 8 },
        { tokens_today: 15000, requests_today: 200 }
      ]
      
      const totalTokens = keys.reduce((sum, key) => sum + key.tokens_today, 0)
      const totalRequests = keys.reduce((sum, key) => sum + key.requests_today, 0)
      
      expect(totalTokens).toBe(16696)
      expect(totalRequests).toBe(223)
    })

    it('should handle zero values correctly', () => {
      const keys = [
        { tokens_today: 0, requests_today: 0 },
        { tokens_today: 100, requests_today: 5 }
      ]
      
      const totalTokens = keys.reduce((sum, key) => sum + key.tokens_today, 0)
      expect(totalTokens).toBe(100)
    })
  })

  // טסט לוגיקת מעבר מפתחות
  describe('Key Switching Logic', () => {
    it('should switch when reaching threshold', () => {
      const requestsPerMinute = 9
      const limit = 15
      const safetyMargin = 0.6 // 60%
      
      const threshold = limit * safetyMargin // 9
      const shouldSwitch = requestsPerMinute >= threshold
      
      expect(shouldSwitch).toBe(true)
    })

    it('should not switch below threshold', () => {
      const requestsPerMinute = 8
      const limit = 15
      const safetyMargin = 0.6 // 60%
      
      const threshold = limit * safetyMargin // 9
      const shouldSwitch = requestsPerMinute >= threshold
      
      expect(shouldSwitch).toBe(false)
    })

    it('should calculate threshold correctly for different limits', () => {
      const testCases = [
        { limit: 10, margin: 0.5, expected: 5 },
        { limit: 20, margin: 0.8, expected: 16 },
        { limit: 15, margin: 0.6, expected: 9 }
      ]
      
      testCases.forEach(({ limit, margin, expected }) => {
        const threshold = limit * margin
        expect(threshold).toBe(expected)
      })
    })
  })

  // טסט סיווג סטטוס מפתחות
  describe('Key Status Classification', () => {
    it('should count key statuses correctly', () => {
      const keys = [
        { status: 'current', daily_limit_reached: false },
        { status: 'available', daily_limit_reached: false },
        { status: 'available', daily_limit_reached: false },
        { status: 'blocked', daily_limit_reached: true }
      ]
      
      const activeCount = keys.filter(k => 
        k.status === 'current' || k.status === 'available'
      ).length
      
      const blockedCount = keys.filter(k => k.status === 'blocked').length
      
      expect(activeCount).toBe(3)
      expect(blockedCount).toBe(1)
    })

    it('should identify current key correctly', () => {
      const keys = [
        { id: 8, status: 'current', is_current: true },
        { id: 9, status: 'available', is_current: false },
        { id: 10, status: 'blocked', is_current: false }
      ]
      
      const currentKey = keys.find(k => k.is_current)
      
      expect(currentKey).toBeDefined()
      expect(currentKey?.id).toBe(8)
      expect(currentKey?.status).toBe('current')
    })
  })

  // טסט פורמט נתונים
  describe('Data Formatting', () => {
    it('should format numbers with commas', () => {
      const testNumbers = [
        { input: 1234, expected: '1,234' },
        { input: 123456, expected: '123,456' },
        { input: 1000, expected: '1,000' }
      ]
      
      testNumbers.forEach(({ input, expected }) => {
        expect(input.toLocaleString()).toBe(expected)
      })
    })

    it('should handle small numbers without commas', () => {
      const smallNumbers = [123, 45, 7]
      
      smallNumbers.forEach(num => {
        const formatted = num.toLocaleString()
        expect(formatted).toBe(num.toString())
      })
    })
  })

  // טסט אגרגציה של נתונים
  describe('Data Aggregation', () => {
    it('should aggregate current minute usage', () => {
      const usageRecords = [
        { tokens_used: 5, requests_count: 1 },
        { tokens_used: 3, requests_count: 1 },
        { tokens_used: 2, requests_count: 1 }
      ]
      
      const totalTokens = usageRecords.reduce((sum, r) => sum + r.tokens_used, 0)
      const totalRequests = usageRecords.reduce((sum, r) => sum + r.requests_count, 0)
      
      expect(totalTokens).toBe(10)
      expect(totalRequests).toBe(3)
    })

    it('should calculate daily statistics per key', () => {
      const dailyRecords = [
        { key_id: 8, tokens_used: 100, requests_count: 1 },
        { key_id: 8, tokens_used: 50, requests_count: 1 },
        { key_id: 9, tokens_used: 200, requests_count: 2 }
      ]
      
      const aggregated: Record<number, { tokens: number, requests: number }> = {}
      
      dailyRecords.forEach(record => {
        if (!aggregated[record.key_id]) {
          aggregated[record.key_id] = { tokens: 0, requests: 0 }
        }
        aggregated[record.key_id].tokens += record.tokens_used
        aggregated[record.key_id].requests += record.requests_count
      })
      
      expect(aggregated[8].tokens).toBe(150) // 100 + 50
      expect(aggregated[8].requests).toBe(2)  // 1 + 1
      expect(aggregated[9].tokens).toBe(200)
      expect(aggregated[9].requests).toBe(2)
    })
  })

  // טסט תקינות נתונים
  describe('Data Validation', () => {
    it('should validate API response structure', () => {
      const mockResponse = {
        status: 'ok',
        keys: [
          {
            id: 8,
            status: 'current',
            tokens_today: 1196,
            requests_today: 15
          }
        ],
        key_management: {
          current_key_index: 0,
          total_keys: 7,
          available_keys: 5
        }
      }
      
      expect(mockResponse.status).toBe('ok')
      expect(mockResponse.keys).toBeDefined()
      expect(mockResponse.key_management).toBeDefined()
      expect(mockResponse.keys[0].id).toBeDefined()
      expect(typeof mockResponse.keys[0].tokens_today).toBe('number')
    })

    it('should handle missing data gracefully', () => {
      const incompleteData = {
        tokens_today: undefined,
        requests_today: null
      }
      
      const safeTokens = incompleteData.tokens_today || 0
      const safeRequests = incompleteData.requests_today || 0
      
      expect(safeTokens).toBe(0)
      expect(safeRequests).toBe(0)
    })
  })
}) 