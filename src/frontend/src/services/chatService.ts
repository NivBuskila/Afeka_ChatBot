import { supabase } from '../config/supabase';

// Get the backend URL from environment
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

// Helper function to replace axios with native fetch
const apiRequest = async (url: string, options: RequestInit = {}) => {
  // Get current session
  const { data: { session } } = await supabase.auth.getSession();
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(session?.access_token && {
        'Authorization': `Bearer ${session.access_token}`
      }),
      ...options.headers,
    },
    ...options,
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  // Handle responses with no content (like 204 No Content)
  if (response.status === 204 || response.headers.get('content-length') === '0') {
    return { success: true };
  }
  
  // Check if response has content to parse
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    const text = await response.text();
    if (text.trim() === '') {
      return { success: true };
    }
    return JSON.parse(text);
  }
  
  return response.json();
};

/**
 * Types for chat functionality
 */
export interface Message {
  id: string;
  user_id: string;
  chat_session_id: string;
  content: string;
  created_at: string;
  is_bot: boolean;
  // Alternative column names that might be used in the database
  message_content?: string;
  message_text?: string;
  text?: string;
}

export interface ChatSession {
  id: string;
  user_id: string;
  title: string | null;
  created_at: string;
  updated_at: string | null;
  messages?: Message[];
}

/**
 * Service for handling chat related operations
 */
const chatService = {
  /**
   * Gets the current logged-in user
   * @returns The current user or null if not logged in
   */
  getCurrentUser: async () => {
    try {
      const { data: { user }, error } = await supabase.auth.getUser();

      if (error || !user) {
        console.error('Error getting current user:', error);
        return null;
      }

      return user;
    } catch (error) {
      console.error('Exception getting user:', error);
      return null;
    }
  },

  /**
   * Creates a new chat session
   * @param userId The ID of the user creating the session
   * @param title Optional title for the chat session
   * @returns The newly created chat session
   */
  createChatSession: async (userId: string, title?: string): Promise<ChatSession | null> => {
    try {
      console.log('Creating chat session with params:', { userId, title });
      
      const sessionInput = {
        user_id: userId,
        title: title || null,
        updated_at: new Date().toISOString()
      };
      
      console.log('Session input data:', sessionInput);
      
      // Create the chat session through the backend
      const response = await apiRequest(`${BACKEND_URL}/api/proxy/chat_sessions`, {
        method: 'POST',
        body: JSON.stringify(sessionInput)
      });
      
      if (!response) {
        console.error('No data returned from chat session creation');
        return null;
      }

      // Handle both array and object responses
      let sessionData;
      if (Array.isArray(response)) {
        if (response.length === 0) {
          console.error('Empty array returned from chat session creation');
          return null;
        }
        sessionData = response[0];
      } else {
        sessionData = response;
      }

      console.log('Chat session created successfully:', sessionData);
      return sessionData as ChatSession;
    } catch (error) {
      console.error('Exception in createChatSession:', error);
      return null;
    }
  },

  /**
   * Fetches all chat sessions for a given user
   * @param userId The ID of the user
   * @returns Array of chat sessions
   */
  fetchAllChatSessions: async (userId: string): Promise<ChatSession[]> => {
    try {
      // Fetch chat sessions through the backend proxy endpoint
      const url = new URL(`${BACKEND_URL}/api/proxy/chat_sessions`);
      url.searchParams.append('user_id', userId);
      
      const response = await apiRequest(url.toString());

      if (!response) {
        console.error('Error fetching chat sessions');
        return [];
      }

      return response as ChatSession[];
    } catch (error) {
      console.error('Exception fetching chat sessions:', error);
      return [];
    }
  },

  /**
   * Legacy function name - Gets all chat sessions for a user
   * @param userId The ID of the user
   * @returns Array of chat sessions
   */
  getUserChatSessions: async (userId: string): Promise<ChatSession[]> => {
    // Call the renamed function to maintain backwards compatibility
    return chatService.fetchAllChatSessions(userId);
  },

  /**
   * Gets a specific chat session with its messages
   * @param sessionId The ID of the chat session
   * @returns Chat session with messages
   */
  getChatSessionWithMessages: async (sessionId: string): Promise<ChatSession | null> => {
    try {
      console.log('Fetching chat session with ID:', sessionId);
      
      const response = await apiRequest(`${BACKEND_URL}/api/proxy/chat_sessions/${sessionId}`);
      
      if (!response) {
        console.error('No session data found for ID:', sessionId);
        return null;
      }

      return response as ChatSession;
    } catch (error) {
      console.error('Error fetching chat session:', error);
      return null;
    }
  },

  /**
   * Sends a message to the backend
   * @param message The message content
   * @param userId The user ID
   * @param sessionId The chat session ID
   * @param isBot Whether this is a bot message
   * @returns The created message
   */
  sendMessage: async (
    message: string,
    userId: string,
    sessionId: string,
    isBot: boolean = false
  ): Promise<Message | null> => {
    try {
      const messageObj = {
        conversation_id: sessionId,
        user_id: userId,
        message_text: message,
        is_bot: isBot,
        created_at: new Date().toISOString()
      };
      
      const response = await apiRequest(`${BACKEND_URL}/api/proxy/messages`, {
        method: 'POST',
        body: JSON.stringify(messageObj)
      });

      if (!response || response.length === 0) {
        console.error('No data returned from message creation');
        return null;
      }

      // Process to standardize the message object
      return {
        id: response[0].message_id || response[0].id,
        user_id: userId,
          chat_session_id: sessionId,
        content: message,
        created_at: response[0].created_at,
        is_bot: isBot
      };
    } catch (error) {
      console.error('Error sending message:', error);
      return null;
    }
  },

  /**
   * Adds a message to a chat session
   * @param message The message to add
   * @returns The added message
   */
  addMessage: async (message: Omit<Message, 'id' | 'created_at'>): Promise<Message | null> => {
    try {
      // Get the schema first to understand what columns are available
      const schemaResponse = await apiRequest(`${BACKEND_URL}/api/proxy/messages_schema`);
      const columns = schemaResponse.map((col: any) => col.column_name);
      
      const messageData: any = {
        id: crypto.randomUUID(),
        user_id: message.user_id,
        conversation_id: message.chat_session_id,
        content: message.content,
      };
      
      // Add role field based on is_bot flag
      if (columns.includes('role')) {
        messageData.role = message.is_bot ? 'bot' : 'user';
      }
      
      // Add bot flag if the schema uses it
      if (columns.includes('is_bot')) {
        messageData.is_bot = message.is_bot;
      }
      
      try {
        const insertResponse = await apiRequest(`${BACKEND_URL}/api/proxy/message`, {
          method: 'PUT',
          body: JSON.stringify(messageData)
        });
        
        if (!insertResponse) {
          console.error('Error adding message via backend proxy: No data returned');
          return null;
        }
        
        const normalizedMessage: Message = {
          id: insertResponse.id,
          user_id: message.user_id,
          chat_session_id: message.chat_session_id,
          content: message.content,
          created_at: insertResponse.created_at || new Date().toISOString(),
          is_bot: message.is_bot
        };
        
        return normalizedMessage;
      } catch (insertError: any) {
        console.error('Error adding message via backend proxy:', insertError.message);
        
        return {
          id: `local_${Date.now()}`,
          user_id: message.user_id,
          chat_session_id: message.chat_session_id,
          content: message.content,
          created_at: new Date().toISOString(),
          is_bot: message.is_bot
        };
      }
    } catch (error) {
      console.error('Exception in addMessage:', error);
      return null;
    }
  },

  /**
   * Updates the title of a chat session
   * @param sessionId The ID of the chat session
   * @param title The new title
   * @returns Boolean indicating success
   */
  updateChatSessionTitle: async (sessionId: string, title: string | null): Promise<boolean> => {
    try {
      const updateData: any = { updated_at: new Date().toISOString() };
      
      // Only include title if it's not null (to support timestamp-only updates)
      if (title !== null) {
        updateData.title = title;
      }
      
      // Update the chat session through the backend proxy endpoint
      const response = await apiRequest(`${BACKEND_URL}/api/proxy/chat_sessions/${sessionId}`, {
        method: 'PATCH',
        body: JSON.stringify(updateData)
      });
      
      if (!response || response.success !== true) {
        console.error('Error updating chat session:', response?.error || 'Unknown error');
        return false;
      }

      return true;
    } catch (error) {
      console.error('Exception updating chat session:', error);
      return false;
    }
  },

  /**
   * Searches chat sessions by title and message content
   * @param userId The ID of the user
   * @param searchTerm The term to search for
   * @returns Array of matching chat sessions
   */
  searchChatSessions: async (userId: string, searchTerm: string): Promise<ChatSession[]> => {
    try {
      if (!searchTerm.trim()) {
        return [];
      }

      // Search chat sessions through the backend proxy endpoint
      const url = new URL(`${BACKEND_URL}/api/proxy/search_chat_sessions`);
      url.searchParams.append('user_id', userId);
      url.searchParams.append('search_term', searchTerm);
      
      const response = await apiRequest(url.toString());

      if (!response) {
        console.error('Error searching chat sessions');
        return [];
      }

      return response as ChatSession[];
    } catch (error) {
      console.error('Exception searching chat sessions:', error);
      return [];
    }
  },

  /**
   * Deletes a chat session and all its messages
   * @param sessionId The ID of the chat session to delete
   * @returns Boolean indicating success
   */
  deleteChatSession: async (sessionId: string): Promise<boolean> => {
    try {
      // Delete the chat session through the backend proxy endpoint
      const response = await apiRequest(`${BACKEND_URL}/api/proxy/chat_session/${sessionId}`, {
        method: 'DELETE'
      });
      
      // Handle both 204 responses and JSON responses
      if (response && (response.success === true || response.success === undefined)) {
        return true;
      }
      
      console.error('Error deleting chat session:', response?.error || 'Unknown error');
      return false;
    } catch (error) {
      console.error('Exception deleting chat session:', error);
      return false;
    }
  },

  /**
   * Sends a streaming chat message and handles real-time responses
   * @param message The message content
   * @param userId The user ID
   * @param history Chat history
   * @param onChunk Callback for receiving streaming chunks
   * @param onComplete Callback when streaming completes
   * @param onError Callback for errors
   */
  sendStreamingMessage: async (
    message: string,
    userId: string,
    history: Array<{ type: string; content: string }> = [],
    onChunk?: (chunk: string, accumulated: string) => void,
    onComplete?: (fullResponse: string, sources?: any[], chunks?: number) => void,
    onError?: (error: string) => void
  ): Promise<void> => {
    try {
      // Get current session
      const { data: { session } } = await supabase.auth.getSession();
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      
      if (session?.access_token) {
        headers['Authorization'] = `Bearer ${session.access_token}`;
      }

      // Use fetch with streaming
      const response = await fetch(`${BACKEND_URL}/api/chat/stream`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          message,
          user_id: userId,
          history
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No reader available for streaming response');
      }

      let accumulatedContent = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            break;
          }

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const jsonStr = line.slice(6); // Remove 'data: ' prefix
                if (jsonStr.trim() === '') continue;
                
                const data = JSON.parse(jsonStr);
                
                switch (data.type) {
                  case 'start':
                    // Stream started
                    console.log('🚀 Stream started');
                    break;
                    
                  case 'chunk':
                    accumulatedContent = data.accumulated || (accumulatedContent + data.content);
                    if (onChunk) {
                      onChunk(data.content, accumulatedContent);
                    }
                    break;
                    
                  case 'complete':
                    if (onComplete) {
                      onComplete(data.content, data.sources, data.chunks);
                    }
                    return;
                    
                  case 'error':
                    if (onError) {
                      onError(data.content || 'Streaming error occurred');
                    }
                    return;
                    
                  case 'end':
                    // Stream ended
                    console.log('✅ Stream ended');
                    return;
                }
              } catch (parseError) {
                console.warn('Failed to parse streaming data:', parseError);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
      
    } catch (error) {
      console.error('Streaming error:', error);
      if (onError) {
        onError(`Streaming failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }
  },
};

export default chatService;
