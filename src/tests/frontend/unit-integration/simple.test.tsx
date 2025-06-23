import { describe, it, expect } from 'vitest'

describe('Simple Calculations', () => {
  it('should calculate total tokens', () => {
    const keys = [
      { tokens_today: 1196, requests_today: 15 },
      { tokens_today: 1125, requests_today: 52 }
    ]
    const total = keys.reduce((sum, key) => sum + key.tokens_today, 0)
    expect(total).toBe(2321)
  })

  it('should check if switching is needed at 60% threshold', () => {
    const requestsPerMinute = 9
    const limit = 15
    const threshold = limit * 0.6 // 9 requests
    const shouldSwitch = requestsPerMinute >= threshold
    expect(shouldSwitch).toBe(true)
  })

  it('should classify key status correctly', () => {
    const keys = [
      { status: 'current', daily_limit_reached: false },
      { status: 'available', daily_limit_reached: false },
      { status: 'blocked', daily_limit_reached: true }
    ]
    
    const activeCount = keys.filter(k => 
      k.status === 'current' || k.status === 'available'
    ).length
    
    expect(activeCount).toBe(2)
  })

  it('should format data correctly', () => {
    const data = {
      total_tokens: 123456,
      total_requests: 789
    }
    
    expect(data.total_tokens.toLocaleString()).toBe('123,456')
    expect(data.total_requests.toLocaleString()).toBe('789')
  })
}) 