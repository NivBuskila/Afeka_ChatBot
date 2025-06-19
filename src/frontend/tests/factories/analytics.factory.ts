import { faker } from '@faker-js/faker'

export interface MockAnalyticsData {
  total_users: number
  active_users_today: number
  total_sessions: number
  total_messages: number
  total_tokens: number
  average_session_length: number
  response_time_avg: number
  uptime_percentage: number
  created_at: string
}

export interface MockTokenUsage {
  date: string
  total_tokens: number
  total_requests: number
  api_key_id?: string
  cost_estimate: number
  breakdown: {
    input_tokens: number
    output_tokens: number
    cached_tokens: number
  }
}

export const createMockAnalyticsData = (overrides: Partial<MockAnalyticsData> = {}): MockAnalyticsData => {
  const baseData: MockAnalyticsData = {
    total_users: faker.number.int({ min: 100, max: 10000 }),
    active_users_today: faker.number.int({ min: 10, max: 500 }),
    total_sessions: faker.number.int({ min: 1000, max: 100000 }),
    total_messages: faker.number.int({ min: 5000, max: 500000 }),
    total_tokens: faker.number.int({ min: 100000, max: 10000000 }),
    average_session_length: faker.number.int({ min: 300, max: 3600 }),
    response_time_avg: faker.number.int({ min: 500, max: 3000 }),
    uptime_percentage: faker.number.float({ min: 95, max: 100, fractionDigits: 2 }),
    created_at: new Date().toISOString()
  }

  return {
    ...baseData,
    ...overrides
  }
}

export const createMockTokenUsage = (options: { timeframe?: string; apiKeyId?: string } = {}): MockTokenUsage[] => {
  const { timeframe = '7d', apiKeyId } = options
  
  let days: number
  switch (timeframe) {
    case '1d':
      days = 1
      break
    case '7d':
      days = 7
      break
    case '30d':
      days = 30
      break
    default:
      days = 7
  }

  return Array.from({ length: days }, (_, i) => {
    const date = new Date()
    date.setDate(date.getDate() - (days - 1 - i))
    
    const totalTokens = faker.number.int({ min: 1000, max: 50000 })
    const inputTokens = Math.floor(totalTokens * 0.7)
    const outputTokens = Math.floor(totalTokens * 0.25)
    const cachedTokens = totalTokens - inputTokens - outputTokens

    return {
      date: date.toISOString().split('T')[0],
      total_tokens: totalTokens,
      total_requests: faker.number.int({ min: 10, max: 1000 }),
      api_key_id: apiKeyId || undefined,
      cost_estimate: faker.number.float({ min: 0.1, max: 50.0, fractionDigits: 2 }),
      breakdown: {
        input_tokens: inputTokens,
        output_tokens: outputTokens,
        cached_tokens: cachedTokens
      }
    }
  })
}
