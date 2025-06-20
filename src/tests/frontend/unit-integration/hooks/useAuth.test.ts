import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';

// Mock the authService
vi.mock('../../src/services/authService', () => ({
  authService: {
    login: vi.fn(),
    resetPassword: vi.fn(),
    logout: vi.fn(),
  },
}));

// Import after mocking
import { useAuth } from '../../src/hooks/useAuth';

// Get the mocked authService
const { authService: mockAuthService } = await vi.importMock('../../src/services/authService');

describe('useAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('initial state', () => {
    it('should initialize with correct default values', () => {
      const { result } = renderHook(() => useAuth());

      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(null);
      expect(typeof result.current.login).toBe('function');
      expect(typeof result.current.resetPassword).toBe('function');
      expect(typeof result.current.logout).toBe('function');
      expect(typeof result.current.clearError).toBe('function');
    });
  });

  describe('login', () => {
    it('should handle successful login', async () => {
      const mockUser = { id: 'user-123', email: 'test@example.com' };
      const mockResult = {
        user: mockUser,
        isAdmin: true,
        error: null,
      };

      mockAuthService.login.mockResolvedValue(mockResult);

      const { result } = renderHook(() => useAuth());

      let loginResult;
      await act(async () => {
        loginResult = await result.current.login('test@example.com', 'password123');
      });

      expect(loginResult).toEqual(mockResult);
      expect(mockAuthService.login).toHaveBeenCalledWith('test@example.com', 'password123');
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(null);
    });

    it('should handle login with service error', async () => {
      const mockResult = {
        user: null,
        isAdmin: false,
        error: 'Invalid credentials',
      };

      mockAuthService.login.mockResolvedValue(mockResult);

      const { result } = renderHook(() => useAuth());

      let loginResult;
      await act(async () => {
        loginResult = await result.current.login('wrong@example.com', 'wrongpass');
      });

      expect(loginResult).toEqual(mockResult);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe('Invalid credentials');
    });

    it('should handle login with exception', async () => {
      const errorMessage = 'Network error occurred';
      mockAuthService.login.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useAuth());

      let loginResult;
      await act(async () => {
        loginResult = await result.current.login('test@example.com', 'password123');
      });

      expect(loginResult).toEqual({
        user: null,
        isAdmin: false,
        error: errorMessage,
      });
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(errorMessage);
    });

    it('should set loading state during login', async () => {
      mockAuthService.login.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({
          user: null,
          isAdmin: false,
          error: null,
        }), 100))
      );

      const { result } = renderHook(() => useAuth());

      // Start login
      act(() => {
        result.current.login('test@example.com', 'password123');
      });

      // Should be loading
      expect(result.current.isLoading).toBe(true);
      expect(result.current.error).toBe(null);

      // Wait for completion
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });
    });
  });

  describe('resetPassword', () => {
    it('should handle successful password reset', async () => {
      const mockResult = { error: null };
      mockAuthService.resetPassword.mockResolvedValue(mockResult);

      const { result } = renderHook(() => useAuth());

      let resetResult;
      await act(async () => {
        resetResult = await result.current.resetPassword('test@example.com');
      });

      expect(resetResult).toEqual(mockResult);
      expect(mockAuthService.resetPassword).toHaveBeenCalledWith('test@example.com');
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(null);
    });

    it('should handle password reset with service error', async () => {
      const mockResult = { error: 'Email not found' };
      mockAuthService.resetPassword.mockResolvedValue(mockResult);

      const { result } = renderHook(() => useAuth());

      let resetResult;
      await act(async () => {
        resetResult = await result.current.resetPassword('notfound@example.com');
      });

      expect(resetResult).toEqual(mockResult);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe('Email not found');
    });

    it('should handle password reset with exception', async () => {
      const errorMessage = 'Service unavailable';
      mockAuthService.resetPassword.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useAuth());

      let resetResult;
      await act(async () => {
        resetResult = await result.current.resetPassword('test@example.com');
      });

      expect(resetResult).toEqual({ error: errorMessage });
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(errorMessage);
    });
  });

  describe('logout', () => {
    it('should handle successful logout', async () => {
      const mockResult = { error: null };
      mockAuthService.logout.mockResolvedValue(mockResult);

      const { result } = renderHook(() => useAuth());

      let logoutResult;
      await act(async () => {
        logoutResult = await result.current.logout();
      });

      expect(logoutResult).toEqual(mockResult);
      expect(mockAuthService.logout).toHaveBeenCalled();
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(null);
    });

    it('should handle logout with exception', async () => {
      const errorMessage = 'Logout service error';
      mockAuthService.logout.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useAuth());

      let logoutResult;
      await act(async () => {
        logoutResult = await result.current.logout();
      });

      expect(logoutResult).toEqual({ error: errorMessage });
      expect(result.current.error).toBe(errorMessage);
    });
  });

  describe('clearError', () => {
    it('should clear error state', async () => {
      mockAuthService.login.mockResolvedValue({
        user: null,
        isAdmin: false,
        error: 'Some error',
      });

      const { result } = renderHook(() => useAuth());

      // Set an error first
      await act(async () => {
        await result.current.login('test@example.com', 'wrongpass');
      });

      expect(result.current.error).toBe('Some error');

      // Clear the error
      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBe(null);
    });
  });
}); 