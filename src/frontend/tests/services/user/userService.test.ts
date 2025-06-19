import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock Supabase before any imports
vi.mock('../../../src/config/supabase', () => {
  const mockSupabase = {
    auth: {
      getUser: vi.fn(),
      signInWithPassword: vi.fn(),
      signOut: vi.fn(),
      signUp: vi.fn(),
      updateUser: vi.fn(),
    },
    from: vi.fn(),
    rpc: vi.fn(),
  };
  
  return {
    supabase: mockSupabase,
  };
});

import { userService } from '../../../src/services/userService';
import { supabase } from '../../../src/config/supabase';

// Get the mocked supabase instance
const mockSupabase = supabase as any;

describe('userService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Setup default successful mocking structure
    const createSuccessfulQueryChain = (data: any) => ({
      select: vi.fn(() => ({
        eq: vi.fn(() => ({
          single: vi.fn().mockResolvedValue({ data, error: null }),
          maybeSingle: vi.fn().mockResolvedValue({ data, error: null }),
        })),
        order: vi.fn().mockResolvedValue({ data, error: null }),
        single: vi.fn().mockResolvedValue({ data, error: null }),
        maybeSingle: vi.fn().mockResolvedValue({ data, error: null }),
      })),
      insert: vi.fn(() => ({
        select: vi.fn(() => ({
          single: vi.fn().mockResolvedValue({ data, error: null }),
        })),
      })),
      update: vi.fn(() => ({
        eq: vi.fn(() => ({
          select: vi.fn(() => ({
            single: vi.fn().mockResolvedValue({ data, error: null }),
          })),
        })),
      })),
      delete: vi.fn(() => ({
        eq: vi.fn().mockResolvedValue({ error: null }),
      })),
    });
    
    // Default mock for from() calls
    mockSupabase.from.mockImplementation(() => createSuccessfulQueryChain(null));
    mockSupabase.rpc.mockResolvedValue({ data: null, error: null });
  });

  describe('getCurrentUser', () => {
    it('should return current user data', async () => {
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        user_metadata: {
          first_name: 'John',
          last_name: 'Doe',
          role: 'user',
        },
      };

      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: mockUser },
        error: null,
      });

      const result = await userService.getCurrentUser();

      expect(result).toEqual({
        id: 'user-123',
        email: 'test@example.com',
        firstName: 'John',
        lastName: 'Doe',
        role: 'user',
      });
    });

    it('should return null when no user', async () => {
      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: null },
        error: null,
      });

      const result = await userService.getCurrentUser();

      expect(result).toBeNull();
    });

    it('should return null on error', async () => {
      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: null },
        error: new Error('Auth error'),
      });

      const result = await userService.getCurrentUser();

      expect(result).toBeNull();
    });
  });

  describe('getCurrentUserRole', () => {
    it('should return admin role for metadata admin', async () => {
      const mockUser = {
        id: 'user-123',
        user_metadata: { is_admin: true },
      };

      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: mockUser },
        error: null,
      });

      mockSupabase.rpc.mockResolvedValue({ data: null, error: null });

      const result = await userService.getCurrentUserRole();

      expect(result).toBe('admin');
      expect(mockSupabase.rpc).toHaveBeenCalledWith('promote_to_admin', { user_id: 'user-123' });
    });

    it('should return admin role for database admin', async () => {
      const mockUser = {
        id: 'user-123',
        user_metadata: {},
      };

      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: mockUser },
        error: null,
      });

      // Mock the admin check query
      const adminData = { id: 1, user_id: 'user-123' };
      mockSupabase.from.mockImplementation((table) => {
        if (table === 'admins') {
          return {
            select: vi.fn(() => ({
              eq: vi.fn(() => ({
                maybeSingle: vi.fn().mockResolvedValue({ data: adminData, error: null }),
              })),
            })),
          };
        }
        return {};
      });

      mockSupabase.auth.updateUser.mockResolvedValue({ data: null, error: null });

      const result = await userService.getCurrentUserRole();

      expect(result).toBe('admin');
    });

    it('should return user role for regular user', async () => {
      const mockUser = {
        id: 'user-123',
        user_metadata: {},
      };

      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: mockUser },
        error: null,
      });

      // Mock the admin check query returning no admin record
      mockSupabase.from.mockImplementation((table) => {
        if (table === 'admins') {
          return {
            select: vi.fn(() => ({
              eq: vi.fn(() => ({
                maybeSingle: vi.fn().mockResolvedValue({ data: null, error: null }),
              })),
            })),
          };
        }
        return {};
      });

      const result = await userService.getCurrentUserRole();

      expect(result).toBe('user');
    });
  });

  describe('isCurrentUserAdmin', () => {
    it('should return true for admin user', async () => {
      const mockUser = {
        id: 'user-123',
        user_metadata: { is_admin: true },
      };

      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: mockUser },
        error: null,
      });

      mockSupabase.rpc.mockResolvedValue({ data: null, error: null });

      const result = await userService.isCurrentUserAdmin();

      expect(result).toBe(true);
    });

    it('should return false for regular user', async () => {
      const mockUser = {
        id: 'user-123',
        user_metadata: {},
      };

      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: mockUser },
        error: null,
      });

      // Mock the admin check query returning no admin record
      const adminQueryResult = { data: null, error: null };
      const mockQueryChain = mockSupabase.from('admins').select();
      mockQueryChain.eq().maybeSingle.mockResolvedValue(adminQueryResult);

      const result = await userService.isCurrentUserAdmin();

      expect(result).toBe(false);
    });

    it('should return false on error', async () => {
      mockSupabase.auth.getUser.mockRejectedValue(new Error('Error'));

      const result = await userService.isCurrentUserAdmin();

      expect(result).toBe(false);
    });
  });

  describe('getAllUsers', () => {
    it('should fetch all users', async () => {
      const mockUsers = [
        { id: 'user-1', email: 'user1@example.com' },
        { id: 'user-2', email: 'user2@example.com' },
      ];

      mockSupabase.from.mockImplementation((table) => {
        if (table === 'users') {
          return {
            select: vi.fn(() => ({
              order: vi.fn().mockResolvedValue({ data: mockUsers, error: null }),
            })),
          };
        }
        return {};
      });

      const result = await userService.getAllUsers();

      expect(result).toEqual(mockUsers);
      expect(mockSupabase.from).toHaveBeenCalledWith('users');
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Fetch failed');
      
      mockSupabase.from.mockImplementation((table) => {
        if (table === 'users') {
          return {
            select: vi.fn(() => ({
              order: vi.fn().mockResolvedValue({ data: null, error }),
            })),
          };
        }
        return {};
      });

      await expect(userService.getAllUsers()).rejects.toThrow('Fetch failed');
    });
  });

  describe('getUserById', () => {
    it('should fetch user by ID', async () => {
      const mockUser = { id: 'user-123', email: 'test@example.com' };

      mockSupabase.from.mockImplementation((table) => {
        if (table === 'users') {
          return {
            select: vi.fn(() => ({
              eq: vi.fn(() => ({
                single: vi.fn().mockResolvedValue({ data: mockUser, error: null }),
              })),
            })),
          };
        }
        return {};
      });

      const result = await userService.getUserById('user-123');

      expect(result).toEqual(mockUser);
      expect(mockSupabase.from).toHaveBeenCalledWith('users');
    });

    it('should handle user not found', async () => {
      const error = new Error('User not found');
      
      mockSupabase.from.mockImplementation((table) => {
        if (table === 'users') {
          return {
            select: vi.fn(() => ({
              eq: vi.fn(() => ({
                single: vi.fn().mockResolvedValue({ data: null, error }),
              })),
            })),
          };
        }
        return {};
      });

      await expect(userService.getUserById('nonexistent')).rejects.toThrow('User not found');
    });
  });

  describe('createUser', () => {
    it('should create user successfully', async () => {
      const userData = { email: 'new@example.com', first_name: 'New', last_name: 'User' };
      const createdUser = { id: 'new-user-id', ...userData };

      mockSupabase.from.mockImplementation((table) => {
        if (table === 'users') {
          return {
            insert: vi.fn(() => ({
              select: vi.fn(() => ({
                single: vi.fn().mockResolvedValue({ data: createdUser, error: null }),
              })),
            })),
          };
        }
        return {};
      });

      const result = await userService.createUser(userData);

      expect(result).toEqual(createdUser);
      expect(mockSupabase.from).toHaveBeenCalledWith('users');
    });

    it('should handle creation errors', async () => {
      const error = new Error('Creation failed');
      
      mockSupabase.from.mockImplementation((table) => {
        if (table === 'users') {
          return {
            insert: vi.fn(() => ({
              select: vi.fn(() => ({
                single: vi.fn().mockResolvedValue({ data: null, error }),
              })),
            })),
          };
        }
        return {};
      });

      const userData = { email: 'test@example.com' };
      await expect(userService.createUser(userData)).rejects.toThrow('Creation failed');
    });
  });

  describe('updateUser', () => {
    it('should update user successfully', async () => {
      const updateData = { first_name: 'Updated' };
      const updatedUser = { id: 'user-123', first_name: 'Updated' };

      mockSupabase.from.mockImplementation((table) => {
        if (table === 'users') {
          return {
            update: vi.fn(() => ({
              eq: vi.fn(() => ({
                select: vi.fn(() => ({
                  single: vi.fn().mockResolvedValue({ data: updatedUser, error: null }),
                })),
              })),
            })),
          };
        }
        return {};
      });

      const result = await userService.updateUser('user-123', updateData);

      expect(result).toEqual(updatedUser);
      expect(mockSupabase.from).toHaveBeenCalledWith('users');
    });

    it('should handle update errors', async () => {
      const error = new Error('Update failed');
      
      mockSupabase.from.mockImplementation((table) => {
        if (table === 'users') {
          return {
            update: vi.fn(() => ({
              eq: vi.fn(() => ({
                select: vi.fn(() => ({
                  single: vi.fn().mockResolvedValue({ data: null, error }),
                })),
              })),
            })),
          };
        }
        return {};
      });

      const updateData = { first_name: 'Updated' };
      await expect(userService.updateUser('user-123', updateData)).rejects.toThrow('Update failed');
    });
  });

  describe('deleteUser', () => {
    it('should delete user successfully', async () => {
      mockSupabase.from.mockImplementation((table) => {
        return {
          delete: vi.fn(() => ({
            eq: vi.fn().mockResolvedValue({ error: null }),
          })),
        };
      });

      await userService.deleteUser('user-123');

      expect(mockSupabase.from).toHaveBeenCalledWith('admins');
      expect(mockSupabase.from).toHaveBeenCalledWith('users');
    });

    it('should handle delete errors', async () => {
      const error = new Error('Delete failed');
      
      mockSupabase.from.mockImplementation((table) => {
        if (table === 'admins') {
          return {
            delete: vi.fn(() => ({
              eq: vi.fn().mockResolvedValue({ error: null }),
            })),
          };
        }
        if (table === 'users') {
          return {
            delete: vi.fn(() => ({
              eq: vi.fn().mockResolvedValue({ error }),
            })),
          };
        }
        return {};
      });

      await expect(userService.deleteUser('user-123')).rejects.toThrow('Delete failed');
    });
  });

  describe('signIn', () => {
    it('should sign in successfully', async () => {
      const authData = {
        user: { id: 'user-123', email: 'test@example.com' },
        session: { access_token: 'token' },
      };

      const authResponse = {
        data: authData,
        error: null,
      };

      mockSupabase.auth.signInWithPassword.mockResolvedValue(authResponse);

      const result = await userService.signIn('test@example.com', 'password');

      expect(result).toEqual(authData); // Expect only the data part
      expect(mockSupabase.auth.signInWithPassword).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password',
      });
    });

    it('should handle sign in errors', async () => {
      const error = new Error('Invalid credentials');
      const errorResponse = {
        data: { user: null, session: null },
        error,
      };

      mockSupabase.auth.signInWithPassword.mockResolvedValue(errorResponse);

      await expect(userService.signIn('test@example.com', 'wrongpassword')).rejects.toThrow('Invalid credentials');
    });
  });

  describe('signOut', () => {
    it('should sign out successfully', async () => {
      mockSupabase.auth.signOut.mockResolvedValue({ error: null });

      await userService.signOut();

      expect(mockSupabase.auth.signOut).toHaveBeenCalled();
    });

    it('should handle sign out errors', async () => {
      const error = new Error('Sign out failed');
      mockSupabase.auth.signOut.mockResolvedValue({ error });

      await expect(userService.signOut()).rejects.toThrow('Sign out failed');
    });
  });

  describe('signUp', () => {
    it('should sign up regular user successfully', async () => {
      const authData = {
        user: { id: 'new-user-id', email: 'new@example.com' },
        session: null,
      };

      const authResponse = {
        data: authData,
        error: null,
      };

      mockSupabase.auth.signUp.mockResolvedValue(authResponse);

      // Mock the user existence check and insert
      mockSupabase.from.mockImplementation((table) => {
        if (table === 'users') {
          return {
            select: vi.fn(() => ({
              eq: vi.fn(() => ({
                maybeSingle: vi.fn().mockResolvedValue({ data: null, error: null }),
              })),
            })),
            insert: vi.fn().mockResolvedValue({ error: null }),
          };
        }
        return {};
      });

      const result = await userService.signUp('new@example.com', 'password', false);

      expect(result).toEqual(authData); // Expect the data part
      expect(mockSupabase.auth.signUp).toHaveBeenCalledWith({
        email: 'new@example.com',
        password: 'password',
        options: {
          data: {
            is_admin: false,
            role: 'user',
            name: 'new',
          },
        },
      });
    });

    it('should sign up admin user successfully', async () => {
      const authData = {
        user: { id: 'admin-user-id', email: 'admin@example.com' },
        session: null,
      };

      const authResponse = {
        data: authData,
        error: null,
      };

      mockSupabase.auth.signUp.mockResolvedValue(authResponse);

      // Mock the user existence check and admin insert
      mockSupabase.from.mockImplementation((table) => {
        if (table === 'users') {
          return {
            select: vi.fn(() => ({
              eq: vi.fn(() => ({
                maybeSingle: vi.fn().mockResolvedValue({ data: null, error: null }),
              })),
            })),
            insert: vi.fn().mockResolvedValue({ error: null }),
          };
        }
        if (table === 'admins') {
          return {
            select: vi.fn(() => ({
              eq: vi.fn(() => ({
                maybeSingle: vi.fn().mockResolvedValue({ data: null, error: null }),
              })),
            })),
            insert: vi.fn().mockResolvedValue({ error: null }),
          };
        }
        return {};
      });

      const result = await userService.signUp('admin@example.com', 'password', true);

      expect(result).toEqual(authData); // Expect the data part
      expect(mockSupabase.auth.signUp).toHaveBeenCalledWith({
        email: 'admin@example.com',
        password: 'password',
        options: {
          data: {
            is_admin: true,
            role: 'admin',
            name: 'admin',
          },
        },
      });
    });
  });

  describe('getDashboardUsers', () => {
    it('should get dashboard users successfully', async () => {
      const mockAllUsers = [
        { id: 'user-1', email: 'user1@example.com', created_at: '2023-01-01', last_sign_in_at: '2023-01-02', is_admin: false },
        { id: 'user-2', email: 'user2@example.com', created_at: '2023-01-03', last_sign_in_at: null, is_admin: false },
      ];

      // Mock RPC to return success
      mockSupabase.rpc.mockResolvedValue({
        data: mockAllUsers,
        error: null,
      });

      const result = await userService.getDashboardUsers();

      expect(result).toEqual({ users: mockAllUsers, admins: [] });
      expect(mockSupabase.rpc).toHaveBeenCalledWith('get_all_users_and_admins');
    });

    it('should fallback on error', async () => {
      const error = new Error('Database error');
      
      // Mock RPC to fail
      mockSupabase.rpc.mockResolvedValue({
        data: null,
        error,
      });

      // Mock fallback queries
      mockSupabase.from.mockImplementation((table) => {
        if (table === 'users') {
          return {
            select: vi.fn(() => ({
              order: vi.fn().mockResolvedValue({ data: [], error: null }),
            })),
          };
        }
        if (table === 'admins') {
          return {
            select: vi.fn().mockResolvedValue({ data: [], error: null }),
          };
        }
        return {};
      });

      const result = await userService.getDashboardUsers();

      expect(result).toEqual({ users: [], admins: [] });
    });
  });
}); 