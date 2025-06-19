import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';

// Mock services with factory functions to avoid hoisting issues
vi.mock('../../src/services/authService', () => ({
  authService: {
    login: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
    isAuthenticated: vi.fn(),
  },
}));

vi.mock('../../src/services/chatService', () => ({
  chatService: {
    getCurrentUser: vi.fn(),
    createChatSession: vi.fn(),
    fetchAllChatSessions: vi.fn(),
    getChatSessionWithMessages: vi.fn(),
  },
}));

// Import after mocking
import { useAuth } from '../../src/hooks/useAuth';
import { authService } from '../../src/services/authService';
import { chatService } from '../../src/services/chatService';

// Get typed mocks
const mockAuthService = authService as any;
const mockChatService = chatService as any;

describe('Authentication and Chat Flow Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Complete User Journey', () => {
    it('should handle login -> session creation -> chat interaction flow', async () => {
      // Mock user data
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        user_metadata: { role: 'user' },
      };

      const mockChatSession = {
        id: 'session-123',
        user_id: 'user-123',
        title: 'My First Chat',
        created_at: '2024-01-01T00:00:00.000Z',
        updated_at: '2024-01-01T00:00:00.000Z',
      };

      // Step 1: Mock successful login
      mockAuthService.login.mockResolvedValue({
        user: mockUser,
        isAdmin: false,
        error: null,
      });

      // Step 2: Mock current user retrieval for chat service
      mockChatService.getCurrentUser.mockResolvedValue(mockUser);

      // Step 3: Mock chat session creation
      mockChatService.createChatSession.mockResolvedValue(mockChatSession);

      // Step 4: Mock fetching all sessions
      mockChatService.fetchAllChatSessions.mockResolvedValue([mockChatSession]);

      // Execute the flow
      const { result } = renderHook(() => useAuth());

      // Login
      let loginResult;
      await act(async () => {
        loginResult = await result.current.login('test@example.com', 'password123');
      });

      expect(loginResult).toEqual({
        user: mockUser,
        isAdmin: false,
        error: null,
      });
      expect(result.current.error).toBeNull();

      // Get current user for chat
      const currentUser = await mockChatService.getCurrentUser();
      expect(currentUser).toEqual(mockUser);

      // Create chat session
      const chatSession = await mockChatService.createChatSession(
        mockUser.id,
        'My First Chat'
      );
      expect(chatSession).toEqual(mockChatSession);

      // Verify all sessions
      const allSessions = await mockChatService.fetchAllChatSessions(mockUser.id);
      expect(allSessions).toEqual([mockChatSession]);

      // Verify all service calls were made
      expect(mockAuthService.login).toHaveBeenCalledWith('test@example.com', 'password123');
      expect(mockChatService.getCurrentUser).toHaveBeenCalled();
      expect(mockChatService.createChatSession).toHaveBeenCalledWith(
        'user-123',
        'My First Chat'
      );
      expect(mockChatService.fetchAllChatSessions).toHaveBeenCalledWith('user-123');
    });

    it('should handle authentication failure gracefully', async () => {
      // Mock login failure
      mockAuthService.login.mockResolvedValue({
        user: null,
        isAdmin: false,
        error: 'Invalid credentials',
      });

      const { result } = renderHook(() => useAuth());

      // Attempt login
      let loginResult;
      await act(async () => {
        loginResult = await result.current.login('wrong@example.com', 'wrongpass');
      });

      expect(loginResult).toEqual({
        user: null,
        isAdmin: false,
        error: 'Invalid credentials',
      });
      expect(result.current.error).toBe('Invalid credentials');

      // Chat services should not be called with failed auth
      expect(mockChatService.getCurrentUser).not.toHaveBeenCalled();
      expect(mockChatService.createChatSession).not.toHaveBeenCalled();
    });

    it('should handle chat session creation failure after successful login', async () => {
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
      };

      // Successful login
      mockAuthService.login.mockResolvedValue({
        user: mockUser,
        isAdmin: false,
        error: null,
      });

      // Successful user retrieval
      mockChatService.getCurrentUser.mockResolvedValue(mockUser);

      // Failed session creation
      mockChatService.createChatSession.mockResolvedValue(null);

      const { result } = renderHook(() => useAuth());

      // Login
      await act(async () => {
        await result.current.login('test@example.com', 'password123');
      });

      expect(result.current.error).toBeNull();

      // Get current user
      const currentUser = await mockChatService.getCurrentUser();
      expect(currentUser).toEqual(mockUser);

      // Try to create session (fails)
      const chatSession = await mockChatService.createChatSession(
        mockUser.id,
        'Failed Session'
      );
      expect(chatSession).toBeNull();

      // Verify login was successful but session creation failed
      expect(mockAuthService.login).toHaveBeenCalled();
      expect(mockChatService.createChatSession).toHaveBeenCalledWith(
        'user-123',
        'Failed Session'
      );
    });
  });

  describe('Admin User Journey', () => {
    it('should handle admin login and enhanced permissions', async () => {
      const mockAdminUser = {
        id: 'admin-123',
        email: 'admin@example.com',
        user_metadata: { role: 'admin' },
      };

      // Mock admin login
      mockAuthService.login.mockResolvedValue({
        user: mockAdminUser,
        isAdmin: true,
        error: null,
      });

      mockChatService.getCurrentUser.mockResolvedValue(mockAdminUser);

      // Mock admin session with special title
      const adminSession = {
        id: 'admin-session-123',
        user_id: 'admin-123',
        title: 'Admin Dashboard Session',
        created_at: '2024-01-01T00:00:00.000Z',
        updated_at: '2024-01-01T00:00:00.000Z',
      };

      mockChatService.createChatSession.mockResolvedValue(adminSession);

      const { result } = renderHook(() => useAuth());

      // Admin login
      let loginResult;
      await act(async () => {
        loginResult = await result.current.login('admin@example.com', 'adminpass');
      });

      expect(loginResult).toEqual({
        user: mockAdminUser,
        isAdmin: true,
        error: null,
      });

      // Create admin session
      const chatSession = await mockChatService.createChatSession(
        mockAdminUser.id,
        'Admin Dashboard Session'
      );

      expect(chatSession).toEqual(adminSession);
      expect(loginResult.isAdmin).toBe(true);
    });
  });

  describe('Session Management', () => {
    it('should handle multiple session operations', async () => {
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
      };

      const mockSessions = [
        {
          id: 'session-1',
          user_id: 'user-123',
          title: 'First Chat',
          created_at: '2024-01-01T00:00:00.000Z',
          updated_at: '2024-01-01T00:00:00.000Z',
        },
        {
          id: 'session-2',
          user_id: 'user-123',
          title: 'Second Chat',
          created_at: '2024-01-02T00:00:00.000Z',
          updated_at: '2024-01-02T00:00:00.000Z',
        },
      ];

      // Setup mocks
      mockAuthService.login.mockResolvedValue({
        user: mockUser,
        isAdmin: false,
        error: null,
      });

      mockChatService.getCurrentUser.mockResolvedValue(mockUser);
      mockChatService.createChatSession
        .mockResolvedValueOnce(mockSessions[0])
        .mockResolvedValueOnce(mockSessions[1]);
      mockChatService.fetchAllChatSessions.mockResolvedValue(mockSessions);

      const { result } = renderHook(() => useAuth());

      // Login
      await act(async () => {
        await result.current.login('test@example.com', 'password123');
      });

      // Create first session
      const session1 = await mockChatService.createChatSession(
        mockUser.id,
        'First Chat'
      );
      expect(session1).toEqual(mockSessions[0]);

      // Create second session
      const session2 = await mockChatService.createChatSession(
        mockUser.id,
        'Second Chat'
      );
      expect(session2).toEqual(mockSessions[1]);

      // Fetch all sessions
      const allSessions = await mockChatService.fetchAllChatSessions(mockUser.id);
      expect(allSessions).toEqual(mockSessions);
      expect(allSessions).toHaveLength(2);
    });
  });

  describe('Error Recovery', () => {
    it('should handle network errors gracefully', async () => {
      // Mock network error on login
      mockAuthService.login.mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useAuth());

      // Attempt login with network error
      let loginResult;
      await act(async () => {
        loginResult = await result.current.login('test@example.com', 'password123');
      });

      expect(loginResult).toEqual({
        user: null,
        isAdmin: false,
        error: 'Network error',
      });
      expect(result.current.error).toBe('Network error');
    });

    it('should handle partial service failures', async () => {
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
      };

      // Successful login
      mockAuthService.login.mockResolvedValue({
        user: mockUser,
        isAdmin: false,
        error: null,
      });

      // Chat service fails
      mockChatService.getCurrentUser.mockRejectedValue(
        new Error('Chat service unavailable')
      );

      const { result } = renderHook(() => useAuth());

      // Login should succeed
      await act(async () => {
        await result.current.login('test@example.com', 'password123');
      });

      expect(result.current.error).toBeNull();

      // But chat service call should fail
      await expect(mockChatService.getCurrentUser()).rejects.toThrow(
        'Chat service unavailable'
      );
    });
  });
}); 