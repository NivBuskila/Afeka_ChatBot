import { http, HttpResponse } from 'msw'
import { createMockAnalyticsData, createMockTokenUsage } from '../factories/analytics.factory'

export const analyticsHandlers = [
  // Get analytics overview
  http.get('*/api/analytics/overview', () => {
    return HttpResponse.json({
      data: createMockAnalyticsData()
    })
  }),
  
  // Get token usage analytics
  http.get('*/api/analytics/token-usage', ({ request }) => {
    const url = new URL(request.url)
    const timeframe = url.searchParams.get('timeframe') || '7d'
    const apiKeyId = url.searchParams.get('api_key_id')
    
    const data = createMockTokenUsage({ timeframe, apiKeyId })
    
    return HttpResponse.json({ data })
  }),
  
  // Get user activity analytics
  http.get('*/api/analytics/user-activity', ({ request }) => {
    const url = new URL(request.url)
    const days = parseInt(url.searchParams.get('days') || '30')
    
    // Generate mock daily activity data
    const dailyActivity = Array.from({ length: days }, (_, i) => {
      const date = new Date()
      date.setDate(date.getDate() - (days - 1 - i))
      
      return {
        date: date.toISOString().split('T')[0],
        active_users: Math.floor(Math.random() * 100) + 20,
        total_sessions: Math.floor(Math.random() * 200) + 50,
        messages_sent: Math.floor(Math.random() * 1000) + 200
      }
    })
    
    return HttpResponse.json({
      data: {
        daily_activity: dailyActivity,
        summary: {
          total_users: Math.floor(Math.random() * 1000) + 500,
          active_users_today: dailyActivity[dailyActivity.length - 1].active_users,
          total_sessions: dailyActivity.reduce((sum, day) => sum + day.total_sessions, 0),
          total_messages: dailyActivity.reduce((sum, day) => sum + day.messages_sent, 0)
        }
      }
    })
  }),
  
  // Get API key performance
  http.get('*/api/analytics/api-keys', () => {
    const mockApiKeys = Array.from({ length: 5 }, (_, i) => ({
      id: `key-${i + 1}`,
      name: `API Key ${i + 1}`,
      status: i === 0 ? 'current' : Math.random() > 0.3 ? 'available' : 'blocked',
      tokens_today: Math.floor(Math.random() * 10000) + 1000,
      requests_today: Math.floor(Math.random() * 100) + 10,
      daily_limit: 15000,
      requests_per_minute: Math.floor(Math.random() * 10) + 1,
      minute_limit: 15,
      daily_limit_reached: false,
      created_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString()
    }))
    
    return HttpResponse.json({
      data: {
        api_keys: mockApiKeys,
        summary: {
          total_keys: mockApiKeys.length,
          active_keys: mockApiKeys.filter(k => k.status !== 'blocked').length,
          total_tokens_today: mockApiKeys.reduce((sum, k) => sum + k.tokens_today, 0),
          total_requests_today: mockApiKeys.reduce((sum, k) => sum + k.requests_today, 0)
        }
      }
    })
  }),
  
  // Get system performance metrics
  http.get('*/api/analytics/performance', () => {
    return HttpResponse.json({
      data: {
        response_times: {
          average: Math.random() * 2000 + 500, // 500-2500ms
          p95: Math.random() * 5000 + 1000,   // 1000-6000ms
          p99: Math.random() * 10000 + 2000   // 2000-12000ms
        },
        error_rates: {
          total_errors: Math.floor(Math.random() * 50),
          error_rate: Math.random() * 0.05, // 0-5%
          common_errors: [
            { type: 'timeout', count: Math.floor(Math.random() * 20) },
            { type: 'rate_limit', count: Math.floor(Math.random() * 15) },
            { type: 'auth_error', count: Math.floor(Math.random() * 10) }
          ]
        },
        usage_patterns: {
          peak_hours: [9, 10, 11, 14, 15, 16], // Peak usage hours
          peak_load: Math.floor(Math.random() * 1000) + 200,
          off_peak_load: Math.floor(Math.random() * 200) + 50
        }
      }
    })
  }),
  
  // Get document analytics
  http.get('*/api/analytics/documents', () => {
    return HttpResponse.json({
      data: {
        total_documents: Math.floor(Math.random() * 1000) + 100,
        documents_processed_today: Math.floor(Math.random() * 50) + 5,
        total_chunks: Math.floor(Math.random() * 10000) + 1000,
        average_processing_time: Math.random() * 30000 + 5000, // 5-35 seconds
        storage_used: Math.floor(Math.random() * 1000000000) + 100000000, // 100MB-1GB
        document_types: [
          { type: 'pdf', count: Math.floor(Math.random() * 500) + 50 },
          { type: 'docx', count: Math.floor(Math.random() * 300) + 30 },
          { type: 'txt', count: Math.floor(Math.random() * 200) + 20 },
          { type: 'md', count: Math.floor(Math.random() * 100) + 10 }
        ]
      }
    })
  }),
]
