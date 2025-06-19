import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { tokenService, TokenUsageData, TokenUsageReport } from '../../../src/services/tokenService'

// Mock environment variable
Object.defineProperty(import.meta, 'env', {
  value: {
    VITE_BACKEND_URL: 'http://localhost:8000'
  },
  writable: true
})

// Mock global fetch
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock data factories
const createMockTokenUsageData = (overrides?: Partial<TokenUsageData>): TokenUsageData => ({
  total_keys: 2,
  current_key_index: 0,
  fallback_key_available: true,
  fallback_key_hash: 'fallback_key_123',
  limits: {
    max_requests_per_minute: 60,
    max_tokens_per_day: 100000,
    max_tokens_per_minute: 4000,
  },
  keys: {
    'key_hash_1': {
      status: 'active',
      is_fallback: false,
      error_count: 0,
      requests_today: 150,
      requests_this_minute: 5,
      tokens_used_today: 25000,
      tokens_used_this_minute: 800,
      last_used: '2024-01-01T10:00:00Z',
      total_successful_requests: 1000,
      average_response_time: 250,
      last_response_time: 180,
      requests_per_minute_usage: '8.33%',
      tokens_per_day_usage: '25.00%',
      tokens_per_minute_usage: '20.00%',
    },
    'key_hash_2': {
      status: 'active',
      is_fallback: true,
      error_count: 2,
      requests_today: 50,
      requests_this_minute: 2,
      tokens_used_today: 5000,
      tokens_used_this_minute: 200,
      last_used: '2024-01-01T09:30:00Z',
      total_successful_requests: 500,
      average_response_time: 300,
      last_response_time: 220,
      requests_per_minute_usage: '3.33%',
      tokens_per_day_usage: '5.00%',
      tokens_per_minute_usage: '5.00%',
    },
  },
  ...overrides,
})

const createMockUsageReport = (overrides?: Partial<TokenUsageReport>): TokenUsageReport => ({
  summary: {
    total_keys: 2,
    total_requests_today: 200,
    total_tokens_today: 30000,
    tokens_remaining_today: 70000,
    keys_near_limit: 0,
  },
  limits: {
    max_requests_per_minute: 60,
    max_tokens_per_day: 100000,
    max_tokens_per_minute: 4000,
  },
  keys: createMockTokenUsageData().keys,
  warnings: [],
  ...overrides,
})

describe('🔑 TokenService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('📊 Token Usage Data', () => {
    it('should fetch token usage data successfully', async () => {
      const mockData = createMockTokenUsageData()
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockData),
      })

      const result = await tokenService.getTokenUsageData()

      expect(result).toEqual(mockData)
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/key-monitoring/metrics'
      )
    })

    it('should handle HTTP errors when fetching token usage data', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      })

      await expect(tokenService.getTokenUsageData()).rejects.toThrow(
        'HTTP error! status: 500'
      )
    })

    it('should handle network errors when fetching token usage data', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'))

      await expect(tokenService.getTokenUsageData()).rejects.toThrow('Network error')
    })

    it('should handle malformed JSON responses', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockRejectedValue(new Error('Invalid JSON')),
      })

      await expect(tokenService.getTokenUsageData()).rejects.toThrow('Invalid JSON')
    })
  })

  describe('📈 Metrics (Backward Compatibility)', () => {
    it('should get metrics using alias method', async () => {
      const mockData = createMockTokenUsageData()
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockData),
      })

      const result = await tokenService.getMetrics()

      expect(result).toEqual(mockData)
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/key-monitoring/metrics'
      )
    })

    it('should maintain same behavior as getTokenUsageData', async () => {
      const mockData = createMockTokenUsageData()
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockData),
      })

      const [usageData, metrics] = await Promise.all([
        tokenService.getTokenUsageData(),
        tokenService.getMetrics(),
      ])

      expect(usageData).toEqual(metrics)
    })
  })

  describe('📋 Usage Report', () => {
    it('should fetch usage report successfully', async () => {
      const mockReport = createMockUsageReport()
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockReport),
      })

      const result = await tokenService.getUsageReport()

      expect(result).toEqual(mockReport)
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/key-monitoring/usage-report'
      )
    })

    it('should handle errors when fetching usage report', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
      })

      await expect(tokenService.getUsageReport()).rejects.toThrow(
        'HTTP error! status: 404'
      )
    })

    it('should handle usage report with warnings', async () => {
      const mockReport = createMockUsageReport({
        warnings: [
          {
            key_hash: 'key_hash_1',
            tokens_today_pct: 85.5,
            requests_minute_pct: 90.0,
          },
        ],
      })
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockReport),
      })

      const result = await tokenService.getUsageReport()

      expect(result.warnings).toHaveLength(1)
      expect(result.warnings[0]).toEqual({
        key_hash: 'key_hash_1',
        tokens_today_pct: 85.5,
        requests_minute_pct: 90.0,
      })
    })
  })

  describe('⚙️ Key Configuration', () => {
    it('should fetch key configuration successfully', async () => {
      const mockConfig = {
        max_keys: 5,
        rotation_enabled: true,
        fallback_enabled: true,
        rate_limiting: true,
      }
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(mockConfig),
      })

      const result = await tokenService.getKeyConfig()

      expect(result).toEqual(mockConfig)
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/key-monitoring/config'
      )
    })

    it('should handle errors when fetching key configuration', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 403,
        statusText: 'Forbidden',
      })

      await expect(tokenService.getKeyConfig()).rejects.toThrow(
        'HTTP error! status: 403'
      )
    })
  })

  describe('🔧 Environment Configuration', () => {
    it('should use default backend URL when environment variable is not set', async () => {
      // Temporarily clear the environment variable
      const originalEnv = import.meta.env.VITE_BACKEND_URL
      delete import.meta.env.VITE_BACKEND_URL

      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(createMockTokenUsageData()),
      })

      await tokenService.getTokenUsageData()

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('http://localhost:8000'),
      )

      // Restore the environment variable
      import.meta.env.VITE_BACKEND_URL = originalEnv
    })

    it('should use custom backend URL from environment', async () => {
      import.meta.env.VITE_BACKEND_URL = 'https://api.example.com'

      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(createMockTokenUsageData()),
      })

      await tokenService.getTokenUsageData()

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('https://api.example.com'),
      )

      // Reset to default for other tests
      import.meta.env.VITE_BACKEND_URL = 'http://localhost:8000'
    })
  })

  describe('🚨 Error Handling and Edge Cases', () => {
    it('should handle empty response data', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(null),
      })

      const result = await tokenService.getTokenUsageData()

      expect(result).toBeNull()
    })

    it('should handle response with missing keys data', async () => {
      const incompleteData = {
        total_keys: 1,
        current_key_index: 0,
        // Missing keys object
      }
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        json: vi.fn().mockResolvedValue(incompleteData),
      })

      const result = await tokenService.getTokenUsageData()

      expect(result).toEqual(incompleteData)
    })

    it('should handle concurrent requests gracefully', async () => {
      const mockData1 = createMockTokenUsageData({ total_keys: 1 })
      const mockData2 = createMockTokenUsageData({ total_keys: 2 })
      const mockReport = createMockUsageReport()

      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: vi.fn().mockResolvedValue(mockData1),
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: vi.fn().mockResolvedValue(mockData2),
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: vi.fn().mockResolvedValue(mockReport),
        })

      const [result1, result2, result3] = await Promise.all([
        tokenService.getTokenUsageData(),
        tokenService.getMetrics(),
        tokenService.getUsageReport(),
      ])

      expect(result1.total_keys).toBe(1)
      expect(result2.total_keys).toBe(2)
      expect(result3.summary.total_keys).toBe(2)
      expect(mockFetch).toHaveBeenCalledTimes(3)
    })
  })
}) 
}) 