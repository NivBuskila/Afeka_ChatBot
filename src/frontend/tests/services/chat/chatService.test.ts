import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { chatService } from '../../../src/services/chatService'
import { createMockUser } from '../../factories/auth.factory'
import { createMockChatSession, createMockMessage } from '../../factories/chat.factory'

// Mock environment variable
Object.defineProperty(import.meta, 'env', {
  value: {
    VITE_BACKEND_URL: 'http://localhost:8000'
  },
  writable: true
})

// Mock Supabase
vi.mock('../../../src/config/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn(),
      getUser: vi.fn(),
    },
  },
}))

// Get reference to mocked Supabase after mock is set up
const { supabase: mockSupabase } = await import('../../../src/config/supabase')

// Mock global fetch
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('💬 ChatService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    
    // Default session mock
    mockSupabase.auth.getSession.mockResolvedValue({
      data: { session: { access_token: 'test-token' } },
      error: null,
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('👤 User Management', () => {
    it('should get current user successfully', async () => {
      const mockUser = createMockUser()
      
      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: mockUser },
        error: null,
      })

      const user = await chatService.getCurrentUser()

      expect(user).toEqual(mockUser)
    })

    it('should return null when user retrieval fails', async () => {
      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: null },
        error: { message: 'Not authenticated' },
      })

      const user = await chatService.getCurrentUser()

      expect(user).toBeNull()
    })

    it('should handle exceptions when getting user', async () => {
      mockSupabase.auth.getUser.mockRejectedValue(
        new Error('Network error')
      )

      const user = await chatService.getCurrentUser()

      expect(user).toBeNull()
    })
  })

  describe('💬 Chat Session Management', () => {
    it('should create a chat session successfully', async () => {
      const mockSession = createMockChatSession({ 
        user_id: 'user-123',
        title: 'Test Chat' 
      })
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: vi.fn().mockResolvedValue(mockSession),
        text: vi.fn().mockResolvedValue(JSON.stringify(mockSession)),
      })

      const result = await chatService.createChatSession('user-123', 'Test Chat')

      expect(result).toEqual(mockSession)
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/proxy/chat_sessions',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token',
          }),
          body: JSON.stringify({
            user_id: 'user-123',
            title: 'Test Chat',
            updated_at: expect.any(String),
          }),
        })
      )
    })

    it('should create a chat session without title', async () => {
      const mockSession = createMockChatSession({ 
        user_id: 'user-123',
        title: null 
      })
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: vi.fn().mockResolvedValue(mockSession),
        text: vi.fn().mockResolvedValue(JSON.stringify(mockSession)),
      })

      const result = await chatService.createChatSession('user-123')

      expect(result).toEqual(mockSession)
      expect(JSON.parse(mockFetch.mock.calls[0][1].body)).toEqual(
        expect.objectContaining({
          user_id: 'user-123',
          title: null,
        })
      )
    })

    it('should handle array response when creating chat session', async () => {
      const mockSession = createMockChatSession()
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: vi.fn().mockResolvedValue([mockSession]),
        text: vi.fn().mockResolvedValue(JSON.stringify([mockSession])),
      })

      const result = await chatService.createChatSession('user-123')

      expect(result).toEqual(mockSession)
    })

    it('should handle empty array response when creating chat session', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: vi.fn().mockResolvedValue([]),
        text: vi.fn().mockResolvedValue('[]'),
      })

      const result = await chatService.createChatSession('user-123')

      expect(result).toBeNull()
    })

    it('should handle network errors when creating chat session', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'))

      const result = await chatService.createChatSession('user-123')

      expect(result).toBeNull()
    })

    it('should handle HTTP errors when creating chat session', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      })

      const result = await chatService.createChatSession('user-123')

      expect(result).toBeNull()
    })
  })

  describe('📋 Fetching Chat Sessions', () => {
    it('should fetch all chat sessions for a user', async () => {
      const mockSessions = [
        createMockChatSession({ user_id: 'user-123', title: 'Chat 1' }),
        createMockChatSession({ user_id: 'user-123', title: 'Chat 2' }),
      ]
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: vi.fn().mockResolvedValue(mockSessions),
        text: vi.fn().mockResolvedValue(JSON.stringify(mockSessions)),
      })

      const result = await chatService.fetchAllChatSessions('user-123')

      expect(result).toEqual(mockSessions)
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/proxy/chat_sessions?user_id=user-123',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token',
          }),
        })
      )
    })

    it('should return empty array when no sessions found', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: vi.fn().mockResolvedValue([]),
        text: vi.fn().mockResolvedValue('[]'),
      })

      const result = await chatService.fetchAllChatSessions('user-123')

      expect(result).toEqual([])
    })

    it('should handle errors when fetching chat sessions', async () => {
      mockFetch.mockRejectedValue(new Error('API error'))

      const result = await chatService.fetchAllChatSessions('user-123')

      expect(result).toEqual([])
    })

    it('should handle null response when fetching chat sessions', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: vi.fn().mockResolvedValue(null),
        text: vi.fn().mockResolvedValue('null'),
      })

      const result = await chatService.fetchAllChatSessions('user-123')

      expect(result).toEqual([])
    })

    it('should maintain backward compatibility with getUserChatSessions', async () => {
      const mockSessions = [createMockChatSession()]
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: vi.fn().mockResolvedValue(mockSessions),
        text: vi.fn().mockResolvedValue(JSON.stringify(mockSessions)),
      })

      const result = await chatService.getUserChatSessions('user-123')

      expect(result).toEqual(mockSessions)
    })
  })

  describe('📄 Chat Session with Messages', () => {
    it('should get chat session with messages successfully', async () => {
      const mockMessages = [
        createMockMessage({ is_bot: false, content: 'Hello' }),
        createMockMessage({ is_bot: true, content: 'Hi there!' }),
      ]
      const mockSession = createMockChatSession({ 
        id: 'session-123',
        messages: mockMessages 
      })
      
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: vi.fn().mockResolvedValue(mockSession),
        text: vi.fn().mockResolvedValue(JSON.stringify(mockSession)),
      })

      const result = await chatService.getChatSessionWithMessages('session-123')

      expect(result).toEqual(mockSession)
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/proxy/chat_sessions/session-123',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token',
          }),
        })
      )
    })

    it('should return null when session not found', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: vi.fn().mockResolvedValue(null),
        text: vi.fn().mockResolvedValue('null'),
      })

      const result = await chatService.getChatSessionWithMessages('nonexistent')

      expect(result).toBeNull()
    })

    it('should handle errors when getting session with messages', async () => {
      mockFetch.mockRejectedValue(new Error('Session fetch error'))

      const result = await chatService.getChatSessionWithMessages('session-123')

      expect(result).toBeNull()
    })
  })

  describe('🔄 API Request Helper', () => {
    it('should handle requests without authentication', async () => {
      mockSupabase.auth.getSession.mockResolvedValue({
        data: { session: null },
        error: null,
      })

      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: vi.fn().mockResolvedValue({ success: true }),
        text: vi.fn().mockResolvedValue('{"success": true}'),
      })

      const result = await chatService.fetchAllChatSessions('user-123')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.not.objectContaining({
            'Authorization': expect.any(String),
          }),
        })
      )
    })

    it('should handle 204 No Content responses', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 204,
        headers: new Headers(),
        json: vi.fn(),
        text: vi.fn().mockResolvedValue(''),
      })

      // This would be for a delete operation, but we'll test with create for simplicity
      const result = await chatService.createChatSession('user-123')

      expect(result).toBeNull() // Since the service expects data back for creation
    })

    it('should handle responses with no content-length', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-length': '0' }),
        json: vi.fn(),
        text: vi.fn().mockResolvedValue(''),
      })

      const result = await chatService.createChatSession('user-123')

      expect(result).toBeNull()
    })

    it('should handle non-JSON responses', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'text/plain' }),
        json: vi.fn().mockResolvedValue({ success: true }),
        text: vi.fn().mockResolvedValue('Plain text response'),
      })

      const result = await chatService.fetchAllChatSessions('user-123')

      expect(result).toEqual({ success: true })
    })

    it('should handle empty JSON responses', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: vi.fn().mockResolvedValue({ success: true }),
        text: vi.fn().mockResolvedValue(''),
      })

      const result = await chatService.fetchAllChatSessions('user-123')

      expect(result).toEqual({ success: true })
    })

    it('should handle HTTP error responses', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
      })

      await expect(chatService.fetchAllChatSessions('user-123')).rejects.toThrow(
        'HTTP error! status: 401'
      )
    })
  })

  describe('🔧 Environment Configuration', () => {
    it('should use default backend URL when environment variable is not set', async () => {
      // Temporarily clear the environment variable
      const originalEnv = import.meta.env.VITE_BACKEND_URL
      delete import.meta.env.VITE_BACKEND_URL

      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: vi.fn().mockResolvedValue([]),
        text: vi.fn().mockResolvedValue('[]'),
      })

      await chatService.fetchAllChatSessions('user-123')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('http://localhost:8000'),
        expect.any(Object)
      )

      // Restore the environment variable
      import.meta.env.VITE_BACKEND_URL = originalEnv
    })

    it('should use custom backend URL from environment', async () => {
      import.meta.env.VITE_BACKEND_URL = 'https://api.example.com'

      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: vi.fn().mockResolvedValue([]),
        text: vi.fn().mockResolvedValue('[]'),
      })

      await chatService.fetchAllChatSessions('user-123')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('https://api.example.com'),
        expect.any(Object)
      )

      // Reset to default for other tests
      import.meta.env.VITE_BACKEND_URL = 'http://localhost:8000'
    })
  })
}) 