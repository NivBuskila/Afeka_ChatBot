import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock environment variables
vi.stubEnv('VITE_BACKEND_URL', 'http://localhost:8000');

// Mock Supabase
vi.mock('../../../src/config/supabase', () => ({
  supabase: {
    auth: {
      getUser: vi.fn(),
      getSession: vi.fn(),
    },
  },
}));

// Import after mocking
import chatService, { Message, ChatSession } from '../../../src/services/chatService';
import { supabase } from '../../../src/config/supabase';
import { createMockChatSession, createMockMessage } from '../../factories/chat.factory';

// Get typed mocks
const mockSupabase = supabase as any;

// Create a global fetch mock that properly handles all the apiRequest logic
const originalFetch = global.fetch;

describe('chatService', () => {
  let mockFetch: any;

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock fetch properly at the global level
    mockFetch = vi.fn();
    global.fetch = mockFetch;
    
    // Default successful session mock
    mockSupabase.auth.getSession.mockResolvedValue({
      data: { 
        session: { 
          access_token: 'mock-token' 
        } 
      }
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    global.fetch = originalFetch;
  });

  // Helper to create proper fetch response that matches apiRequest expectations
  const createMockFetchResponse = (data: any, status: number = 200, headers: Record<string, string> = {}) => {
    const isSuccess = status >= 200 && status < 300;
    const defaultHeaders = {
      'content-type': 'application/json',
      ...headers
    };
    
    const responseText = data === null ? '' : JSON.stringify(data);
    
    return Promise.resolve({
      ok: isSuccess,
      status,
      headers: {
        get: (key: string) => defaultHeaders[key.toLowerCase()] || null
      },
      text: () => Promise.resolve(responseText),
      json: () => Promise.resolve(data)
    });
  };

  describe('getCurrentUser', () => {
    it('should return current user when authenticated', async () => {
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        user_metadata: {
          first_name: 'John',
          last_name: 'Doe'
        }
      };

      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: mockUser },
        error: null
      });

      const result = await chatService.getCurrentUser();

      expect(result).toEqual(mockUser);
      expect(mockSupabase.auth.getUser).toHaveBeenCalled();
    });

    it('should return null when not authenticated', async () => {
      mockSupabase.auth.getUser.mockResolvedValue({
        data: { user: null },
        error: { message: 'No user found' }
      });

      const result = await chatService.getCurrentUser();

      expect(result).toBeNull();
    });

    it('should handle errors gracefully', async () => {
      mockSupabase.auth.getUser.mockRejectedValue(new Error('Network error'));

      const result = await chatService.getCurrentUser();

      expect(result).toBeNull();
    });
  });

  describe('createChatSession', () => {
    it('should create a new chat session successfully', async () => {
      const mockSession = createMockChatSession({
        id: 'session-123',
        user_id: 'user-123',
        title: 'Test Chat'
      });

      mockFetch.mockImplementation(() => createMockFetchResponse(mockSession));

      const result = await chatService.createChatSession('user-123', 'Test Chat');

      expect(result).toEqual(mockSession);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/proxy/chat_sessions',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-token'
          },
          body: expect.stringContaining('"user_id":"user-123"') && 
                expect.stringContaining('"title":"Test Chat"') &&
                expect.stringContaining('"updated_at"')
        }
      );
    });

    it('should handle array response from backend', async () => {
      const mockSession = createMockChatSession();
      
      mockFetch.mockImplementation(() => createMockFetchResponse([mockSession]));

      const result = await chatService.createChatSession('user-123');

      expect(result).toEqual(mockSession);
    });

    it('should return null on API error', async () => {
      mockFetch.mockImplementation(() => createMockFetchResponse(null, 500));

      const result = await chatService.createChatSession('user-123');

      expect(result).toBeNull();
    });

    it('should return null on network error', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'));

      const result = await chatService.createChatSession('user-123');

      expect(result).toBeNull();
    });

    it('should handle empty array response', async () => {
      mockFetch.mockImplementation(() => createMockFetchResponse([]));

      const result = await chatService.createChatSession('user-123');

      expect(result).toBeNull();
    });
  });

  describe('fetchAllChatSessions', () => {
    it('should fetch all chat sessions for a user', async () => {
      const mockSessions = [
        createMockChatSession({ user_id: 'user-123' }),
        createMockChatSession({ user_id: 'user-123' })
      ];

      mockFetch.mockImplementation(() => createMockFetchResponse(mockSessions));

      const result = await chatService.fetchAllChatSessions('user-123');

      expect(result).toEqual(mockSessions);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/proxy/chat_sessions?user_id=user-123',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-token'
          })
        })
      );
    });

    it('should return empty array on error', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'));

      const result = await chatService.fetchAllChatSessions('user-123');

      expect(result).toEqual([]);
    });

    it('should handle API error response', async () => {
      mockFetch.mockImplementation(() => createMockFetchResponse(null, 500));

      const result = await chatService.fetchAllChatSessions('user-123');

      expect(result).toEqual([]);
    });
  });

  describe('getUserChatSessions', () => {
    it('should call fetchAllChatSessions (legacy compatibility)', async () => {
      const mockSessions = [createMockChatSession()];
      
      mockFetch.mockImplementation(() => createMockFetchResponse(mockSessions));

      const result = await chatService.getUserChatSessions('user-123');

      expect(result).toEqual(mockSessions);
    });
  });

  describe('getChatSessionWithMessages', () => {
    it('should fetch chat session with messages', async () => {
      const mockSession = createMockChatSession({
        id: 'session-123',
        messages: [createMockMessage()]
      });

      mockFetch.mockImplementation(() => createMockFetchResponse(mockSession));

      const result = await chatService.getChatSessionWithMessages('session-123');

      expect(result).toEqual(mockSession);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/proxy/chat_sessions/session-123',
        expect.any(Object)
      );
    });

    it('should return null when session not found', async () => {
      mockFetch.mockImplementation(() => {
        // Return a response that will cause apiRequest to throw or return null
        return Promise.resolve({
          ok: false,
          status: 404,
          headers: {
            get: () => null
          },
          text: () => Promise.resolve(''),
          json: () => Promise.resolve(null)
        });
      });

      const result = await chatService.getChatSessionWithMessages('nonexistent');

      expect(result).toBeNull();
    });

    it('should handle API errors', async () => {
      mockFetch.mockRejectedValue(new Error('Not found'));

      const result = await chatService.getChatSessionWithMessages('session-123');

      expect(result).toBeNull();
    });
  });

  describe('sendMessage', () => {
    it('should send a user message successfully', async () => {
      const mockResponse = [{
        message_id: 'msg-123',
        created_at: '2024-01-01T10:00:00Z'
      }];

      mockFetch.mockImplementation(() => createMockFetchResponse(mockResponse));

      const result = await chatService.sendMessage(
        'Hello world',
        'user-123',
        'session-123',
        false
      );

      expect(result).toEqual({
        id: 'msg-123',
        user_id: 'user-123',
        chat_session_id: 'session-123',
        content: 'Hello world',
        created_at: '2024-01-01T10:00:00Z',
        is_bot: false
      });

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/proxy/messages',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-token'
          },
          body: expect.stringContaining('"conversation_id":"session-123"') &&
                expect.stringContaining('"user_id":"user-123"') &&
                expect.stringContaining('"message_text":"Hello world"') &&
                expect.stringContaining('"is_bot":false')
        }
      );
    });

    it('should send a bot message successfully', async () => {
      const mockResponse = [{
        id: 'msg-456',
        created_at: '2024-01-01T10:01:00Z'
      }];

      mockFetch.mockImplementation(() => createMockFetchResponse(mockResponse));

      const result = await chatService.sendMessage(
        'Hello! How can I help?',
        'user-123',
        'session-123',
        true
      );

      expect(result?.is_bot).toBe(true);
    });

    it('should return null on API error', async () => {
      mockFetch.mockImplementation(() => createMockFetchResponse(null, 500));

      const result = await chatService.sendMessage(
        'Hello world',
        'user-123',
        'session-123'
      );

      expect(result).toBeNull();
    });

    it('should return null when no data returned', async () => {
      mockFetch.mockImplementation(() => createMockFetchResponse([]));

      const result = await chatService.sendMessage(
        'Hello world',
        'user-123',
        'session-123'
      );

      expect(result).toBeNull();
    });
  });

  describe('addMessage', () => {
    it('should add message successfully', async () => {
      // Mock schema response first, then insert response
      mockFetch
        .mockImplementationOnce(() => createMockFetchResponse([
          { column_name: 'id' },
          { column_name: 'content' },
          { column_name: 'role' },
          { column_name: 'is_bot' }
        ]))
        .mockImplementationOnce(() => createMockFetchResponse({
          id: 'msg-123',
          created_at: '2024-01-01T10:00:00Z'
        }));

      const messageInput = {
        user_id: 'user-123',
        chat_session_id: 'session-123',
        content: 'Test message',
        is_bot: false
      };

      const result = await chatService.addMessage(messageInput);

      expect(result).toEqual({
        id: 'msg-123',
        user_id: 'user-123',
        chat_session_id: 'session-123',
        content: 'Test message',
        created_at: '2024-01-01T10:00:00Z',
        is_bot: false
      });
    });

    it('should fallback to local message on API error', async () => {
      // Mock schema response first, then fail on insert
      mockFetch
        .mockImplementationOnce(() => createMockFetchResponse([{ column_name: 'content' }]))
        .mockRejectedValueOnce(new Error('API Error'));

      const messageInput = {
        user_id: 'user-123',
        chat_session_id: 'session-123',
        content: 'Test message',
        is_bot: false
      };

      const result = await chatService.addMessage(messageInput);

      expect(result?.id).toMatch(/^local_\d+$/);
      expect(result?.content).toBe('Test message');
    });

    it('should return null on complete failure', async () => {
      mockFetch.mockRejectedValue(new Error('Complete failure'));

      const messageInput = {
        user_id: 'user-123',
        chat_session_id: 'session-123',
        content: 'Test message',
        is_bot: false
      };

      const result = await chatService.addMessage(messageInput);

      expect(result).toBeNull();
    });
  });

  describe('updateChatSessionTitle', () => {
    it('should update chat session title successfully', async () => {
      mockFetch.mockImplementation(() => createMockFetchResponse({ success: true }));

      const result = await chatService.updateChatSessionTitle('session-123', 'New Title');

      expect(result).toBe(true);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/proxy/chat_sessions/session-123',
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-token'
          },
          body: expect.stringContaining('"title":"New Title"') &&
                expect.stringContaining('"updated_at"')
        }
      );
    });

    it('should update timestamp only when title is null', async () => {
      mockFetch.mockImplementation(() => createMockFetchResponse({ success: true }));

      const result = await chatService.updateChatSessionTitle('session-123', null);

      expect(result).toBe(true);
      
      const lastCall = mockFetch.mock.calls[mockFetch.mock.calls.length - 1];
      const bodyData = JSON.parse(lastCall[1].body);
      expect(bodyData).not.toHaveProperty('title');
      expect(bodyData).toHaveProperty('updated_at');
    });

    it('should return false on API error', async () => {
      mockFetch.mockImplementation(() => createMockFetchResponse(null, 500));

      const result = await chatService.updateChatSessionTitle('session-123', 'New Title');

      expect(result).toBe(false);
    });

    it('should return false when success is false', async () => {
      mockFetch.mockImplementation(() => createMockFetchResponse({ success: false, error: 'Update failed' }));

      const result = await chatService.updateChatSessionTitle('session-123', 'New Title');

      expect(result).toBe(false);
    });
  });

  describe('searchChatSessions', () => {
    it('should search chat sessions successfully', async () => {
      const mockSessions = [createMockChatSession({ title: 'Test Search Result' })];

      mockFetch.mockImplementation(() => createMockFetchResponse(mockSessions));

      const result = await chatService.searchChatSessions('user-123', 'test query');

      expect(result).toEqual(mockSessions);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/proxy/search_chat_sessions?user_id=user-123&search_term=test+query',
        expect.any(Object)
      );
    });

    it('should return empty array for empty search term', async () => {
      const result = await chatService.searchChatSessions('user-123', '');

      expect(result).toEqual([]);
      expect(mockFetch).not.toHaveBeenCalled();
    });

    it('should return empty array for whitespace-only search term', async () => {
      const result = await chatService.searchChatSessions('user-123', '   ');

      expect(result).toEqual([]);
      expect(mockFetch).not.toHaveBeenCalled();
    });

    it('should handle API errors', async () => {
      mockFetch.mockRejectedValue(new Error('Search failed'));

      const result = await chatService.searchChatSessions('user-123', 'test');

      expect(result).toEqual([]);
    });
  });

  describe('deleteChatSession', () => {
    it('should delete chat session successfully with success response', async () => {
      mockFetch.mockImplementation(() => createMockFetchResponse({ success: true }));

      const result = await chatService.deleteChatSession('session-123');

      expect(result).toBe(true);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/proxy/chat_session/session-123',
        expect.objectContaining({
          method: 'DELETE'
        })
      );
    });

    it('should handle 204 No Content response', async () => {
      mockFetch.mockImplementation(() => createMockFetchResponse(
        { success: true }, 
        204, 
        { 'content-length': '0' }
      ));

      const result = await chatService.deleteChatSession('session-123');

      expect(result).toBe(true);
    });

    it('should return false on API error', async () => {
      mockFetch.mockImplementation(() => createMockFetchResponse(null, 404));

      const result = await chatService.deleteChatSession('session-123');

      expect(result).toBe(false);
    });

    it('should return false when success is false', async () => {
      mockFetch.mockImplementation(() => createMockFetchResponse({ success: false, error: 'Not found' }));

      const result = await chatService.deleteChatSession('session-123');

      expect(result).toBe(false);
    });
  });

  describe('sendStreamingMessage', () => {
    it('should handle streaming response successfully', async () => {
      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('data: {"type":"start"}\n')
          })
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('data: {"type":"chunk","content":"Hello"}\n')
          })
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('data: {"type":"chunk","content":" World","accumulated":"Hello World"}\n')
          })
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('data: {"type":"complete","content":"Hello World","sources":[],"chunks":2}\n')
          })
          .mockResolvedValueOnce({
            done: true,
            value: undefined
          }),
        releaseLock: vi.fn()
      };

      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: {
          getReader: () => mockReader
        }
      });

      const onChunk = vi.fn();
      const onComplete = vi.fn();
      const onError = vi.fn();

      await chatService.sendStreamingMessage(
        'Hello',
        'user-123',
        [],
        onChunk,
        onComplete,
        onError
      );

      expect(onChunk).toHaveBeenCalledWith('Hello', 'Hello');
      expect(onChunk).toHaveBeenCalledWith(' World', 'Hello World');
      expect(onComplete).toHaveBeenCalledWith('Hello World', [], 2);
      expect(onError).not.toHaveBeenCalled();
      expect(mockReader.releaseLock).toHaveBeenCalled();
    });

    it('should handle streaming errors', async () => {
      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('data: {"type":"error","content":"Something went wrong"}\n')
          }),
        releaseLock: vi.fn()
      };

      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: {
          getReader: () => mockReader
        }
      });

      const onChunk = vi.fn();
      const onComplete = vi.fn();
      const onError = vi.fn();

      await chatService.sendStreamingMessage(
        'Hello',
        'user-123',
        [],
        onChunk,
        onComplete,
        onError
      );

      expect(onError).toHaveBeenCalledWith('Something went wrong');
      expect(onComplete).not.toHaveBeenCalled();
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'));

      const onError = vi.fn();

      await chatService.sendStreamingMessage(
        'Hello',
        'user-123',
        [],
        undefined,
        undefined,
        onError
      );

      expect(onError).toHaveBeenCalledWith('Streaming failed: Network error');
    });

    it('should handle HTTP errors', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500
      });

      const onError = vi.fn();

      await chatService.sendStreamingMessage(
        'Hello',
        'user-123',
        [],
        undefined,
        undefined,
        onError
      );

      expect(onError).toHaveBeenCalledWith('Streaming failed: HTTP error! status: 500');
    });

    it('should handle missing reader', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: null
      });

      const onError = vi.fn();

      await chatService.sendStreamingMessage(
        'Hello',
        'user-123',
        [],
        undefined,
        undefined,
        onError
      );

      expect(onError).toHaveBeenCalledWith('Streaming failed: No reader available for streaming response');
    });

    it('should handle malformed JSON in stream', async () => {
      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('data: {invalid json}\n')
          })
          .mockResolvedValueOnce({
            done: true,
            value: undefined
          }),
        releaseLock: vi.fn()
      };

      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        body: {
          getReader: () => mockReader
        }
      });

      const onError = vi.fn();

      await chatService.sendStreamingMessage(
        'Hello',
        'user-123',
        [],
        undefined,
        undefined,
        onError
      );

      // Should not call onError for JSON parse errors, just log them
      expect(onError).not.toHaveBeenCalled();
      expect(mockReader.releaseLock).toHaveBeenCalled();
    });
  });
});