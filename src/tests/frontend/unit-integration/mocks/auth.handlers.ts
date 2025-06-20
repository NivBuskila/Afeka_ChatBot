import { http, HttpResponse } from 'msw'
import { createMockUser, createMockSession } from '../factories/auth.factory'

export const authHandlers = [
  // Supabase Auth endpoints
  http.post('*/auth/v1/token', async ({ request }) => {
    const body = await request.text()
    const params = new URLSearchParams(body)
    const grantType = params.get('grant_type')
    
    if (grantType === 'password') {
      const email = params.get('email')
      const password = params.get('password')
      
      // Mock login logic
      if (email === 'admin@test.com' && password === 'admin123') {
        return HttpResponse.json({
          access_token: 'mock-access-token-admin',
          refresh_token: 'mock-refresh-token-admin',
          expires_in: 3600,
          token_type: 'bearer',
          user: createMockUser({ 
            email: 'admin@test.com',
            id: 'admin-user-id',
            role: 'admin' 
          })
        })
      }
      
      if (email === 'user@test.com' && password === 'user123') {
        return HttpResponse.json({
          access_token: 'mock-access-token-user',
          refresh_token: 'mock-refresh-token-user',
          expires_in: 3600,
          token_type: 'bearer',
          user: createMockUser({ 
            email: 'user@test.com',
            id: 'regular-user-id',
            role: 'user' 
          })
        })
      }
      
      // Invalid credentials
      return HttpResponse.json(
        { error: 'invalid_grant', error_description: 'Invalid login credentials' },
        { status: 400 }
      )
    }
    
    if (grantType === 'refresh_token') {
      const refreshToken = params.get('refresh_token')
      
      if (refreshToken?.includes('admin')) {
        return HttpResponse.json({
          access_token: 'mock-access-token-admin-refreshed',
          refresh_token: 'mock-refresh-token-admin-refreshed',
          expires_in: 3600,
          token_type: 'bearer',
          user: createMockUser({ 
            email: 'admin@test.com',
            id: 'admin-user-id',
            role: 'admin' 
          })
        })
      }
      
      return HttpResponse.json({
        access_token: 'mock-access-token-user-refreshed',
        refresh_token: 'mock-refresh-token-user-refreshed',
        expires_in: 3600,
        token_type: 'bearer',
        user: createMockUser({ 
          email: 'user@test.com',
          id: 'regular-user-id',
          role: 'user' 
        })
      })
    }
    
    return HttpResponse.json(
      { error: 'unsupported_grant_type' },
      { status: 400 }
    )
  }),
  
  // Get session
  http.get('*/auth/v1/user', () => {
    return HttpResponse.json({
      ...createMockUser(),
      aud: 'authenticated',
      exp: Math.floor(Date.now() / 1000) + 3600
    })
  }),
  
  // Sign up
  http.post('*/auth/v1/signup', async ({ request }) => {
    const { email, password } = await request.json()
    
    if (!email || !password) {
      return HttpResponse.json(
        { error: 'invalid_request', error_description: 'Email and password are required' },
        { status: 400 }
      )
    }
    
    return HttpResponse.json({
      access_token: 'mock-access-token-new',
      refresh_token: 'mock-refresh-token-new',
      expires_in: 3600,
      token_type: 'bearer',
      user: createMockUser({ email, id: 'new-user-id' })
    })
  }),
  
  // Sign out
  http.post('*/auth/v1/logout', () => {
    return HttpResponse.json({}, { status: 204 })
  }),
  
  // Password reset
  http.post('*/auth/v1/recover', async ({ request }) => {
    const { email } = await request.json()
    
    return HttpResponse.json({
      message: `Password reset email sent to ${email}`
    })
  }),
  
  // Update password
  http.put('*/auth/v1/user', async ({ request }) => {
    const { password } = await request.json()
    
    if (!password) {
      return HttpResponse.json(
        { error: 'invalid_request', error_description: 'Password is required' },
        { status: 400 }
      )
    }
    
    return HttpResponse.json({
      ...createMockUser(),
      updated_at: new Date().toISOString()
    })
  }),
  
  // Check admin status
  http.get('*/rest/v1/admins', ({ request }) => {
    const url = new URL(request.url)
    const userId = url.searchParams.get('user_id')
    
    if (userId === 'admin-user-id') {
      return HttpResponse.json([{
        id: '1',
        user_id: 'admin-user-id',
        created_at: '2024-01-01T00:00:00Z'
      }])
    }
    
    return HttpResponse.json([])
  }),
] 