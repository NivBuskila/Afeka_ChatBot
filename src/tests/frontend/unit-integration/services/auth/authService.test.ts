import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock Supabase with factory function to avoid hoisting issues
vi.mock('../../../src/config/supabase', () => ({
  supabase: {
    auth: {
      signInWithPassword: vi.fn(),
      signOut: vi.fn(),
      getUser: vi.fn(),
      getSession: vi.fn(),
      resetPasswordForEmail: vi.fn(),
    },
    from: vi.fn(() => ({
      select: vi.fn().mockReturnThis(),
      eq: vi.fn().mockReturnThis(),
      maybeSingle: vi.fn(),
      update: vi.fn().mockReturnThis(),
      insert: vi.fn(),
    })),
    rpc: vi.fn(),
  },
}));

// Import after mocking
import { authService, AuthResult } from '../../../src/services/authService';
import { supabase } from '../../../src/config/supabase';

// Get typed mock
const mockSupabase = supabase as any;

describe('authService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Object.defineProperty(window, 'location', {
      value: { origin: 'http://localhost:3000' },
      writable: true,
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('login', () => {
    it('should successfully login with valid credentials', async () => {
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        user_metadata: { is_admin: true },
      };
      
      mockSupabase.auth.signInWithPassword.mockResolvedValue({
        data: { user: mockUser },
        error: null,
      });
      
      mockSupabase.from().maybeSingle.mockResolvedValue({
        data: { id: 'admin-123' },
        error: null,
      });

      const result = await authService.login('test@example.com', 'password123');

      expect(result).toEqual({
        user: mockUser,
        isAdmin: true,
        error: null,
      });
      expect(mockSupabase.auth.signInWithPassword).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });

    it('should handle invalid login credentials', async () => {
      mockSupabase.auth.signInWithPassword.mockResolvedValue({
        data: { user: null },
        error: { message: 'Invalid login credentials' },
      });

      const result = await authService.login('wrong@example.com', 'wrongpass');

      expect(result).toEqual({
        user: null,
        isAdmin: false,
        error: 'אימייל או סיסמה שגויים',
      });
    });

    it('should detect admin user from metadata', async () => {
      const mockUser = {
        id: 'user-123',
        email: 'admin@example.com',
        user_metadata: { role: 'admin' },
      };
      
      mockSupabase.auth.signInWithPassword.mockResolvedValue({
        data: { user: mockUser },
        error: null,
      });

      const result = await authService.login('admin@example.com', 'password123');

      expect(result.isAdmin).toBe(true);
    });

    it('should detect admin user from database', async () => {
      const mockUser = {
        id: 'user-123',
        email: 'admin@example.com',
        user_metadata: {},
      };
      
      mockSupabase.auth.signInWithPassword.mockResolvedValue({
        data: { user: mockUser },
        error: null,
      });
      
      // Mock admin query to return admin record
      mockSupabase.from.mockReturnValueOnce({
        select: vi.fn().mockReturnThis(),
        eq: vi.fn().mockReturnThis(),
        maybeSingle: vi.fn().mockResolvedValue({
          data: { id: 'admin-123' },
          error: null,
        }),
        update: vi.fn().mockResolvedValue({ error: null })
      });

      const result = await authService.login('admin@example.com', 'password123');

      expect(result.isAdmin).toBe(true);
    });

    it('should update last sign in time', async () => {
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        user_metadata: {},
      };
      
      mockSupabase.auth.signInWithPassword.mockResolvedValue({
        data: { user: mockUser },
        error: null,
      });
      
      const mockUpdate = vi.fn().mockResolvedValue({ error: null });
      mockSupabase.from.mockReturnValue({
        select: vi.fn().mockReturnThis(),
        eq: vi.fn().mockReturnThis(),
        maybeSingle: vi.fn().mockResolvedValue({ data: null }),
        update: mockUpdate,
      });

      await authService.login('test@example.com', 'password123');

      expect(mockUpdate).toHaveBeenCalledWith({ 
        last_sign_in: expect.any(String) 
      });
    });

    it('should handle unexpected errors', async () => {
      mockSupabase.auth.signInWithPassword.mockRejectedValue(
        new Error('Network error')
      );

      const result = await authService.login('test@example.com', 'password123');

      expect(result).toEqual({
        user: null,
        isAdmin: false,
        error: 'Network error',
      });
    });
  });

  describe('checkIsAdmin', () => {
    it('should return true for admin user in database', async () => {
      mockSupabase.from.mockReturnValue({
        select: vi.fn().mockReturnThis(),
        eq: vi.fn().mockReturnThis(),
        maybeSingle: vi.fn().mockResolvedValue({
          data: { id: 'admin-123' },
          error: null,
        })
      });

      const result = await authService.checkIsAdmin('user-123');

      expect(result).toBe(true);
    });

    it('should return true for admin user via RPC', async () => {
      mockSupabase.from.mockReturnValue({
        select: vi.fn().mockReturnThis(),
        eq: vi.fn().mockReturnThis(),
        maybeSingle: vi.fn().mockResolvedValue({
          data: null,
          error: { message: 'Access denied' },
        })
      });
      
      mockSupabase.rpc.mockResolvedValue({
        data: true,
        error: null,
      });

      const result = await authService.checkIsAdmin('user-123');

      expect(result).toBe(true);
    });

    it('should return true for admin user from metadata', async () => {
      mockSupabase.from.mockReturnValue({
        select: vi.fn().mockReturnThis(),
        eq: vi.fn().mockReturnThis(),
        maybeSingle: vi.fn().mockResolvedValue({
          data: null,
          error: { message: 'Access denied' },
        })
      });
      
      mockSupabase.rpc.mockRejectedValue(new Error('RPC failed'));
      
      mockSupabase.auth.getUser.mockResolvedValue({
        data: {
          user: {
            user_metadata: { role: 'admin' },
          },
        },
      });

      const result = await authService.checkIsAdmin('user-123');

      expect(result).toBe(true);
    });

    it('should return false for non-admin user', async () => {
      mockSupabase.from().maybeSingle.mockResolvedValue({
        data: null,
        error: null,
      });
      
      mockSupabase.rpc.mockResolvedValue({
        data: false,
        error: null,
      });
      
      mockSupabase.auth.getUser.mockResolvedValue({
        data: {
          user: {
            user_metadata: { role: 'user' },
          },
        },
      });

      const result = await authService.checkIsAdmin('user-123');

      expect(result).toBe(false);
    });

    it('should handle errors gracefully', async () => {
      mockSupabase.from().maybeSingle.mockRejectedValue(
        new Error('Database error')
      );

      const result = await authService.checkIsAdmin('user-123');

      expect(result).toBe(false);
    });
  });

  describe('resetPassword', () => {
    it('should successfully send password reset email', async () => {
      mockSupabase.auth.resetPasswordForEmail.mockResolvedValue({
        error: null,
      });

      const result = await authService.resetPassword('test@example.com');

      expect(result).toEqual({ error: null });
      expect(mockSupabase.auth.resetPasswordForEmail).toHaveBeenCalledWith(
        'test@example.com',
        {
          redirectTo: 'http://localhost:3000/reset-password',
        }
      );
    });

    it('should handle email sending errors', async () => {
      mockSupabase.auth.resetPasswordForEmail.mockResolvedValue({
        error: { message: 'Email not found' },
      });

      const result = await authService.resetPassword('notfound@example.com');

      expect(result).toEqual({ error: 'Email not found' });
    });

    it('should handle unexpected errors', async () => {
      mockSupabase.auth.resetPasswordForEmail.mockRejectedValue(
        new Error('Service unavailable')
      );

      const result = await authService.resetPassword('test@example.com');

      expect(result).toEqual({ error: 'Service unavailable' });
    });
  });

  describe('logout', () => {
    it('should successfully logout user', async () => {
      mockSupabase.auth.signOut.mockResolvedValue({ error: null });

      await authService.logout();

      expect(mockSupabase.auth.signOut).toHaveBeenCalled();
    });
  });

  describe('getCurrentUser', () => {
    it('should return current user when authenticated', async () => {
      const mockUser = { id: 'user-123', email: 'test@example.com' };
      
      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: mockUser },
        error: null,
      });

      const result = await authService.getCurrentUser();

      expect(result).toEqual(mockUser);
    });

    it('should throw error when not authenticated', async () => {
      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: null },
        error: { message: 'Not authenticated' },
      });

      await expect(authService.getCurrentUser()).rejects.toThrow();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when user has valid session', async () => {
      mockSupabase.auth.getSession.mockResolvedValue({
        data: {
          session: {
            access_token: 'valid-token',
            user: { id: 'user-123' },
          },
        },
      });

      const result = await authService.isAuthenticated();

      expect(result).toBe(true);
    });

    it('should return false when user has no session', async () => {
      mockSupabase.auth.getSession.mockResolvedValue({
        data: { session: null },
      });

      const result = await authService.isAuthenticated();

      expect(result).toBe(false);
    });
  });

  describe('isAdmin', () => {
    it('should return true for admin user', async () => {
      mockSupabase.auth.getUser.mockResolvedValue({
        data: {
          user: {
            id: 'user-123',
            user_metadata: { role: 'admin' },
          },
        },
      });

      const result = await authService.isAdmin();

      expect(result).toBe(true);
    });

    it('should return false for non-admin user', async () => {
      mockSupabase.auth.getUser.mockResolvedValue({
        data: {
          user: {
            id: 'user-123',
            user_metadata: { role: 'user' },
          },
        },
      });

      const result = await authService.isAdmin();

      expect(result).toBe(false);
    });

    it('should return false when not authenticated', async () => {
      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: null },
        error: { message: 'Not authenticated' },
      });

      const result = await authService.isAdmin();

      expect(result).toBe(false);
    });
  });

  describe('ensureAdminRecord', () => {
    it('should skip creating record if admin already exists', async () => {
      mockSupabase.from.mockReturnValue({
        select: vi.fn().mockReturnThis(),
        eq: vi.fn().mockReturnThis(),
        maybeSingle: vi.fn().mockResolvedValue({
          data: { id: 'admin-123' },
          error: null,
        })
      });

      await authService.ensureAdminRecord('user-123');

      expect(mockSupabase.rpc).not.toHaveBeenCalled();
    });

    it('should create admin record via RPC', async () => {
      mockSupabase.from.mockReturnValue({
        select: vi.fn().mockReturnThis(),
        eq: vi.fn().mockReturnThis(),
        maybeSingle: vi.fn().mockResolvedValue({
          data: null,
          error: null,
        })
      });
      
      mockSupabase.rpc.mockResolvedValue({ error: null });

      await authService.ensureAdminRecord('user-123');

      expect(mockSupabase.rpc).toHaveBeenCalledWith('promote_to_admin', {
        user_id: 'user-123',
      });
    });

    it('should fallback to direct insert if RPC fails', async () => {
      const mockInsert = vi.fn().mockResolvedValue({ error: null });
      
      // First call for checking existing admin
      mockSupabase.from.mockReturnValueOnce({
        select: vi.fn().mockReturnThis(),
        eq: vi.fn().mockReturnThis(),
        maybeSingle: vi.fn().mockResolvedValue({
          data: null,
          error: null,
        })
      });
      
      // Second call for insert
      mockSupabase.from.mockReturnValueOnce({
        insert: mockInsert,
      });
      
      mockSupabase.rpc.mockRejectedValue(new Error('RPC failed'));

      await authService.ensureAdminRecord('user-123');

      expect(mockInsert).toHaveBeenCalledWith({
        user_id: 'user-123',
        permissions: ['read', 'write'],
      });
    });

    it('should handle duplicate admin record error', async () => {
      const mockInsert = vi.fn().mockResolvedValue({
        error: { code: '23505', message: 'duplicate key value' },
      });
      
      // First call for checking existing admin
      mockSupabase.from.mockReturnValueOnce({
        select: vi.fn().mockReturnThis(),
        eq: vi.fn().mockReturnThis(),
        maybeSingle: vi.fn().mockResolvedValue({
          data: null,
          error: null,
        })
      });
      
      // Second call for insert
      mockSupabase.from.mockReturnValueOnce({
        insert: mockInsert,
      });
      
      mockSupabase.rpc.mockRejectedValue(new Error('RPC failed'));

      // Should not throw error
      await expect(authService.ensureAdminRecord('user-123')).resolves.toBeUndefined();
    });
  });
}); 