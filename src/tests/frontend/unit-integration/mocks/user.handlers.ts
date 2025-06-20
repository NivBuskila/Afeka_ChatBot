import { http, HttpResponse } from 'msw'
import { createMockUser } from '../factories/auth.factory'

let mockUsers: any[] = [
  createMockUser({ 
    id: 'admin-user-id',
    email: 'admin@test.com',
    role: 'admin',
    name: 'Test Admin'
  }),
  createMockUser({ 
    id: 'regular-user-id',
    email: 'user@test.com',
    role: 'user',
    name: 'Test User'
  })
]

export const userHandlers = [
  // Get users list (admin only)
  http.get('*/rest/v1/users', ({ request }) => {
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const limit = parseInt(url.searchParams.get('limit') || '20')
    
    // Simulate admin check
    const authHeader = request.headers.get('authorization')
    if (!authHeader?.includes('admin')) {
      return HttpResponse.json(
        { error: 'Insufficient permissions' },
        { status: 403 }
      )
    }
    
    // Pagination
    const startIndex = (page - 1) * limit
    const paginatedUsers = mockUsers.slice(startIndex, startIndex + limit)
    
    return HttpResponse.json({
      data: paginatedUsers,
      count: mockUsers.length,
      page,
      limit
    })
  }),
  
  // Get user profile
  http.get('*/rest/v1/users/:userId', ({ params }) => {
    const { userId } = params
    
    const user = mockUsers.find(u => u.id === userId)
    if (!user) {
      return HttpResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }
    
    return HttpResponse.json({ data: user })
  }),
  
  // Update user profile
  http.put('*/rest/v1/users/:userId', async ({ params, request }) => {
    const { userId } = params
    const updates = await request.json()
    
    const userIndex = mockUsers.findIndex(u => u.id === userId)
    if (userIndex === -1) {
      return HttpResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }
    
    mockUsers[userIndex] = {
      ...mockUsers[userIndex],
      ...updates,
      updated_at: new Date().toISOString()
    }
    
    return HttpResponse.json({ data: mockUsers[userIndex] })
  }),
  
  // Delete user (admin only)
  http.delete('*/rest/v1/users/:userId', ({ params, request }) => {
    const { userId } = params
    
    // Simulate admin check
    const authHeader = request.headers.get('authorization')
    if (!authHeader?.includes('admin')) {
      return HttpResponse.json(
        { error: 'Insufficient permissions' },
        { status: 403 }
      )
    }
    
    const userIndex = mockUsers.findIndex(u => u.id === userId)
    if (userIndex === -1) {
      return HttpResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }
    
    // Prevent admin from deleting themselves
    if (userId === 'admin-user-id') {
      return HttpResponse.json(
        { error: 'Cannot delete your own account' },
        { status: 400 }
      )
    }
    
    mockUsers.splice(userIndex, 1)
    
    return HttpResponse.json({}, { status: 204 })
  }),
  
  // Get user preferences
  http.get('*/api/user/preferences', ({ request }) => {
    const url = new URL(request.url)
    const userId = url.searchParams.get('user_id') || 'test-user-id'
    
    return HttpResponse.json({
      data: {
        user_id: userId,
        theme: 'light',
        language: 'en',
        notifications: {
          email: true,
          push: false,
          chat_sounds: true
        },
        display: {
          messages_per_page: 50,
          show_timestamps: true,
          compact_mode: false
        },
        privacy: {
          data_collection: true,
          analytics: true
        }
      }
    })
  }),
  
  // Update user preferences
  http.put('*/api/user/preferences', async ({ request }) => {
    const preferences = await request.json()
    
    return HttpResponse.json({
      data: {
        ...preferences,
        updated_at: new Date().toISOString()
      }
    })
  }),
  
  // Get user activity summary
  http.get('*/api/user/:userId/activity', ({ params, request }) => {
    const { userId } = params
    const url = new URL(request.url)
    const days = parseInt(url.searchParams.get('days') || '30')
    
    const user = mockUsers.find(u => u.id === userId)
    if (!user) {
      return HttpResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }
    
    return HttpResponse.json({
      data: {
        user_id: userId,
        total_sessions: Math.floor(Math.random() * 100) + 10,
        total_messages: Math.floor(Math.random() * 1000) + 50,
        average_session_length: Math.floor(Math.random() * 1800) + 300, // 5-35 minutes
        last_active: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
        favorite_topics: [
          'documentation',
          'help',
          'technical support'
        ],
        usage_by_day: Array.from({ length: days }, (_, i) => {
          const date = new Date()
          date.setDate(date.getDate() - (days - 1 - i))
          
          return {
            date: date.toISOString().split('T')[0],
            sessions: Math.floor(Math.random() * 5),
            messages: Math.floor(Math.random() * 20),
            time_spent: Math.floor(Math.random() * 3600) // seconds
          }
        })
      }
    })
  }),
]

// Helper function to reset mock data
export const resetUserMockData = () => {
  mockUsers = [
    createMockUser({ 
      id: 'admin-user-id',
      email: 'admin@test.com',
      role: 'admin',
      name: 'Test Admin'
    }),
    createMockUser({ 
      id: 'regular-user-id',
      email: 'user@test.com',
      role: 'user',
      name: 'Test User'
    })
  ]
}
