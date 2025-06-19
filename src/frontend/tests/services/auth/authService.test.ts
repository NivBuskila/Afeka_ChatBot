import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { authService } from '../../../src/services/authService'
import { createMockUser } from '../../factories/auth.factory'

// Mock Supabase
// Create mock functions that will be reused
const mockMaybeSingle = vi.fn()
const mockEq = vi.fn(() => ({ maybeSingle: mockMaybeSingle }))
const mockSelect = vi.fn(() => ({ eq: mockEq }))
const mockUpdate = vi.fn()
const mockUpdateEq = vi.fn()
const mockInsert = vi.fn()
const mockFrom = vi.fn()

vi.mock('../../../src/config/supabase', () => ({
  supabase: {
    auth: {
      signInWithPassword: vi.fn(),
      signOut: vi.fn(),
      getUser: vi.fn(),
      getSession: vi.fn(),
      resetPasswordForEmail: vi.fn(),
    },
    from: mockFrom,
    rpc: vi.fn(),
  },
}))

// Get reference to mocked Supabase after mock is set up
const { supabase: mockSupabase } = await import('../../../src/config/supabase')

describe('🔐 AuthService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    
    // Set up the from() method chain
    mockFrom.mockReturnValue({
      select: mockSelect,
      update: mockUpdate,
      insert: mockInsert,
    })
    
    mockUpdate.mockReturnValue({
      eq: mockUpdateEq,
    })
    
    // Mock window.location for password reset tests
    Object.defineProperty(window, 'location', {
      value: { origin: 'http://localhost:3000' },
      writable: true,
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('📝 Login', () => {
    it('should successfully login with valid credentials', async () => {
      const mockUser = createMockUser({ 
        email: 'user@test.com',
        id: 'user-123',
        role: 'user' 
      })
      
      mockSupabase.auth.signInWithPassword.mockResolvedValue({
        data: { user: mockUser },
        error: null,
      })

      mockMaybeSingle.mockResolvedValue({
        data: null,
        error: null,
      })

      mockUpdateEq.mockResolvedValue({
        data: null,
        error: null,
      })

      const result = await authService.login('user@test.com', 'password123')

      expect(result).toEqual({
        user: mockUser,
        isAdmin: false,
        error: null,
      })
      expect(mockSupabase.auth.signInWithPassword).toHaveBeenCalledWith({
        email: 'user@test.com',
        password: 'password123',
      })
    })

    it('should successfully login admin user and set admin flag', async () => {
      const mockAdminUser = createMockUser({ 
        email: 'admin@test.com',
        id: 'admin-123',
        role: 'admin' 
      })
      
      mockSupabase.auth.signInWithPassword.mockResolvedValue({
        data: { user: mockAdminUser },
        error: null,
      })

      mockMaybeSingle.mockResolvedValue({
        data: { id: '1', user_id: 'admin-123' },
        error: null,
      })

      mockUpdateEq.mockResolvedValue({
        data: null,
        error: null,
      })

      mockSupabase.rpc.mockResolvedValue({
        data: null,
        error: null,
      })

      const result = await authService.login('admin@test.com', 'admin123')

      expect(result).toEqual({
        user: mockAdminUser,
        isAdmin: true,
        error: null,
      })
    })

    it('should handle invalid login credentials', async () => {
      mockSupabase.auth.signInWithPassword.mockResolvedValue({
        data: { user: null },
        error: { message: 'Invalid login credentials' },
      })

      const result = await authService.login('wrong@test.com', 'wrongpass')

      expect(result).toEqual({
        user: null,
        isAdmin: false,
        error: 'אימייל או סיסמה שגויים',
      })
    })

    it('should handle network errors during login', async () => {
      mockSupabase.auth.signInWithPassword.mockRejectedValue(
        new Error('Network error')
      )

      const result = await authService.login('user@test.com', 'password123')

      expect(result).toEqual({
        user: null,
        isAdmin: false,
        error: 'Network error',
      })
    })

    it('should handle unknown supabase errors', async () => {
      mockSupabase.auth.signInWithPassword.mockResolvedValue({
        data: { user: null },
        error: { message: 'Unknown database error' },
      })

      const result = await authService.login('user@test.com', 'password123')

      expect(result).toEqual({
        user: null,
        isAdmin: false,
        error: 'Unknown database error',
      })
    })

    it('should update last sign in time after successful login', async () => {
      const mockUser = createMockUser({ id: 'user-123' })
      
      mockSupabase.auth.signInWithPassword.mockResolvedValue({
        data: { user: mockUser },
        error: null,
      })

      mockMaybeSingle.mockResolvedValue({
        data: null,
        error: null,
      })

      mockUpdateEq.mockResolvedValue({ data: null, error: null })

      await authService.login('user@test.com', 'password123')

      expect(mockSupabase.from).toHaveBeenCalledWith('users')
      expect(mockUpdateEq).toHaveBeenCalled()
    })
  })

  describe('🔍 Admin Checks', () => {
    it('should correctly identify admin user from database', async () => {
      mockMaybeSingle.mockResolvedValue({
        data: { id: '1', user_id: 'admin-123' },
        error: null,
      })

      const isAdmin = await authService.checkIsAdmin('admin-123')

      expect(isAdmin).toBe(true)
      expect(mockSupabase.from).toHaveBeenCalledWith('admins')
    })

    it('should return false for non-admin user', async () => {
      mockSupabase.from().select().eq().maybeSingle.mockResolvedValue({
        data: null,
        error: null,
      })

      mockSupabase.rpc.mockResolvedValue({
        data: false,
        error: null,
      })

      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: { user_metadata: { role: 'user' } } },
        error: null,
      })

      const isAdmin = await authService.checkIsAdmin('user-123')

      expect(isAdmin).toBe(false)
    })

    it('should fallback to RPC when direct table access fails', async () => {
      mockSupabase.from().select().eq().maybeSingle.mockResolvedValue({
        data: null,
        error: { message: 'Permission denied' },
      })

      mockSupabase.rpc.mockResolvedValue({
        data: true,
        error: null,
      })

      const isAdmin = await authService.checkIsAdmin('admin-123')

      expect(isAdmin).toBe(true)
      expect(mockSupabase.rpc).toHaveBeenCalledWith('is_admin', { user_id: 'admin-123' })
    })

    it('should fallback to user metadata when RPC fails', async () => {
      mockSupabase.from().select().eq().maybeSingle.mockResolvedValue({
        data: null,
        error: { message: 'Permission denied' },
      })

      mockSupabase.rpc.mockRejectedValue(new Error('RPC error'))

      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: { user_metadata: { role: 'admin' } } },
        error: null,
      })

      const isAdmin = await authService.checkIsAdmin('admin-123')

      expect(isAdmin).toBe(true)
    })

    it('should handle errors gracefully and return false', async () => {
      mockSupabase.from().select().eq().maybeSingle.mockRejectedValue(
        new Error('Database error')
      )

      const isAdmin = await authService.checkIsAdmin('user-123')

      expect(isAdmin).toBe(false)
    })
  })

  describe('🛠️ Admin Record Management', () => {
    it('should skip creating admin record if one already exists', async () => {
      mockSupabase.from().select().eq().maybeSingle.mockResolvedValue({
        data: { id: '1', user_id: 'admin-123' },
        error: null,
      })

      await authService.ensureAdminRecord('admin-123')

      expect(mockSupabase.rpc).not.toHaveBeenCalled()
      expect(mockSupabase.from().insert).not.toHaveBeenCalled()
    })

    it('should create admin record using RPC when none exists', async () => {
      mockSupabase.from().select().eq().maybeSingle.mockResolvedValue({
        data: null,
        error: null,
      })

      mockSupabase.rpc.mockResolvedValue({
        data: null,
        error: null,
      })

      await authService.ensureAdminRecord('admin-123')

      expect(mockSupabase.rpc).toHaveBeenCalledWith('promote_to_admin', { user_id: 'admin-123' })
    })

    it('should fallback to direct insert when RPC fails', async () => {
      mockSupabase.from().select().eq().maybeSingle.mockResolvedValue({
        data: null,
        error: null,
      })

      mockSupabase.rpc.mockRejectedValue(new Error('RPC not available'))

      mockSupabase.from().insert.mockResolvedValue({
        data: null,
        error: null,
      })

      await authService.ensureAdminRecord('admin-123')

      expect(mockSupabase.from().insert).toHaveBeenCalledWith({
        user_id: 'admin-123',
        permissions: ['read', 'write'],
      })
    })

    it('should handle duplicate admin record creation gracefully', async () => {
      mockSupabase.from().select().eq().maybeSingle.mockResolvedValue({
        data: null,
        error: null,
      })

      mockSupabase.rpc.mockRejectedValue(new Error('RPC not available'))

      mockSupabase.from().insert.mockResolvedValue({
        data: null,
        error: { code: '23505', message: 'Duplicate key' },
      })

      // Should not throw an error
      await expect(authService.ensureAdminRecord('admin-123')).resolves.toBeUndefined()
    })
  })

  describe('🔄 Password Reset', () => {
    it('should send password reset email successfully', async () => {
      mockSupabase.auth.resetPasswordForEmail.mockResolvedValue({
        data: null,
        error: null,
      })

      const result = await authService.resetPassword('user@test.com')

      expect(result).toEqual({ error: null })
      expect(mockSupabase.auth.resetPasswordForEmail).toHaveBeenCalledWith(
        'user@test.com',
        { redirectTo: 'http://localhost:3000/reset-password' }
      )
    })

    it('should handle password reset errors', async () => {
      mockSupabase.auth.resetPasswordForEmail.mockResolvedValue({
        data: null,
        error: { message: 'Email not found' },
      })

      const result = await authService.resetPassword('nonexistent@test.com')

      expect(result).toEqual({ error: 'Email not found' })
    })

    it('should handle network errors during password reset', async () => {
      mockSupabase.auth.resetPasswordForEmail.mockRejectedValue(
        new Error('Network timeout')
      )

      const result = await authService.resetPassword('user@test.com')

      expect(result).toEqual({ error: 'Network timeout' })
    })
  })

  describe('🚪 Logout', () => {
    it('should logout successfully', async () => {
      mockSupabase.auth.signOut.mockResolvedValue({
        error: null,
      })

      await authService.logout()

      expect(mockSupabase.auth.signOut).toHaveBeenCalled()
    })

    it('should handle logout errors gracefully', async () => {
      mockSupabase.auth.signOut.mockRejectedValue(
        new Error('Logout failed')
      )

      // Should not throw an error
      await expect(authService.logout()).resolves.toBeUndefined()
    })
  })

  describe('👤 User Management', () => {
    it('should get current user successfully', async () => {
      const mockUser = createMockUser()
      
      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: mockUser },
        error: null,
      })

      const user = await authService.getCurrentUser()

      expect(user).toEqual(mockUser)
    })

    it('should throw error when getting current user fails', async () => {
      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: null },
        error: { message: 'Not authenticated' },
      })

      await expect(authService.getCurrentUser()).rejects.toThrow('Not authenticated')
    })

    it('should check authentication status correctly when authenticated', async () => {
      mockSupabase.auth.getSession.mockResolvedValue({
        data: { session: { access_token: 'valid-token' } },
        error: null,
      })

      const isAuthenticated = await authService.isAuthenticated()

      expect(isAuthenticated).toBe(true)
    })

    it('should check authentication status correctly when not authenticated', async () => {
      mockSupabase.auth.getSession.mockResolvedValue({
        data: { session: null },
        error: null,
      })

      const isAuthenticated = await authService.isAuthenticated()

      expect(isAuthenticated).toBe(false)
    })

    it('should check if current user is admin', async () => {
      const mockAdminUser = createMockUser({ 
        id: 'admin-123',
        role: 'admin' 
      })
      
      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: mockAdminUser },
        error: null,
      })

      mockSupabase.from().select().eq().maybeSingle.mockResolvedValue({
        data: { id: '1', user_id: 'admin-123' },
        error: null,
      })

      const isAdmin = await authService.isAdmin()

      expect(isAdmin).toBe(true)
    })

    it('should return false for admin check when user is not authenticated', async () => {
      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: null },
        error: { message: 'Not authenticated' },
      })

      const isAdmin = await authService.isAdmin()

      expect(isAdmin).toBe(false)
    })
  })
}) 