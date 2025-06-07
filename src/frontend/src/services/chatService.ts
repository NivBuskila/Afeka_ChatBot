import { supabase } from '../config/supabase';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';

// Get the backend URL from environment
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

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
  metadata?: any;
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
      const response = await axios.post(`${BACKEND_URL}/api/proxy/chat_sessions`, sessionInput);
      
      if (!response.data || response.data.length === 0) {
        console.error('No data returned from chat session creation');
        return null;
      }

      console.log('Chat session created successfully:', response.data[0]);
      return response.data[0] as ChatSession;
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
      const response = await axios.get(`${BACKEND_URL}/api/proxy/chat_sessions`, {
        params: { user_id: userId }
      });

      if (!response.data) {
        console.error('Error fetching chat sessions');
        return [];
      }

      return response.data as ChatSession[];
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
      
      const response = await axios.get(`${BACKEND_URL}/api/proxy/chat_sessions/${sessionId}`);
      
      if (!response.data) {
        console.error('No session data found for ID:', sessionId);
        return null;
      }

      return response.data as ChatSession;
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
      
      const response = await axios.post(`${BACKEND_URL}/api/proxy/messages`, messageObj);

      if (!response.data || response.data.length === 0) {
        console.error('No data returned from message creation');
        return null;
      }

      // Process to standardize the message object
      return {
        id: response.data[0].message_id || response.data[0].id,
        user_id: userId,
          chat_session_id: sessionId,
        content: message,
        created_at: response.data[0].created_at,
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
      console.log('Adding message to session:', message.chat_session_id);
      
      try {
        // First update the chat session's and conversation's updated_at timestamp
        await chatService.updateChatSessionTitle(message.chat_session_id, null);
      } catch (updateError) {
        console.error('Failed to update chat session timestamp:', updateError);
        // Continue anyway - this shouldn't prevent message creation
      }

      try {
        // Get messages schema to understand the column structure
        const response = await axios.get(`${BACKEND_URL}/api/proxy/messages_schema`);
        
        if (!response.data || !response.data.columns) {
          console.error('Failed to get messages schema');
        return null;
      }

        const columns = response.data.columns;
        console.log('Available columns in messages table:', columns);
        
        // Determine which fields to use based on the schema
        const hasPrimaryKey = columns.includes('message_id');
        const hasConversationId = columns.includes('conversation_id');
        const hasRequest = columns.includes('request');
        const hasResponse = columns.includes('response');
        
        // Create message data with the appropriate schema
        let messageData: any = {};
        
        // Set the primary key (use custom ID if needed)
        if (hasPrimaryKey) {
          // Generate a timestamp-based numeric ID instead of UUID
          const numericId = Date.now() * 1000 + Math.floor(Math.random() * 1000);
          messageData.message_id = numericId;
        } else {
          messageData.id = uuidv4();
        }
        
        // Set the user ID
        messageData.user_id = message.user_id;
        
        // Always use conversation_id field (our database schema requires it)
        messageData.conversation_id = message.chat_session_id;
        
        // Set the message content based on bot/user
        if (message.is_bot) {
          if (hasResponse) {
            messageData.response = message.content;
            messageData.request = ''; // Might be required
          } else {
            messageData.content = message.content;
          }
        } else {
          if (hasRequest) {
            messageData.request = message.content;
            messageData.response = ''; // Might be required
          } else {
            messageData.content = message.content;
          }
        }
        
        // Add bot flag if the schema uses it
        if (columns.includes('is_bot')) {
          messageData.is_bot = message.is_bot;
        }
        
        // Set status if the schema has it
        if (columns.includes('status')) {
          messageData.status = 'completed';
        }
        
        // Add metadata if provided and schema supports it
        if (message.metadata && columns.includes('metadata')) {
          messageData.metadata = message.metadata;
        }
        
        console.log('Inserting message with adapted schema:', messageData);
        
        try {
          // Insert the message using the backend proxy endpoint
          const insertResponse = await axios.put(`${BACKEND_URL}/api/proxy/message`, messageData);
          
          console.log('Message inserted successfully:', insertResponse.data);
          
          if (!insertResponse.data) {
            console.error('Error adding message via backend proxy: No data returned');
          return null;
        }
        
        // Create a normalized message object to return
        const normalizedMessage: Message = {
            id: insertResponse.data.message_id?.toString() || insertResponse.data.id,
            user_id: message.user_id,
            chat_session_id: message.chat_session_id,
            content: message.content,
            created_at: insertResponse.data.created_at || new Date().toISOString(),
            is_bot: message.is_bot,
            metadata: message.metadata
          };
          
          return normalizedMessage;
        } catch (insertError: any) {
          console.error('Error adding message via backend proxy:', insertError.message);
          if (insertError.response) {
            console.error('Server response:', insertError.response.data);
          }
          
          // יצירת הודעה מקומית - במקרה של כישלון, עדיין להחזיר אובייקט כדי שהממשק ימשיך לעבוד
          return {
            id: `local_${Date.now()}`,
            user_id: message.user_id,
            chat_session_id: message.chat_session_id,
            content: message.content,
            created_at: new Date().toISOString(),
            is_bot: message.is_bot
          };
        }
      } catch (schemaError) {
        console.error('Error fetching message schema:', schemaError);
        // יצירת הודעה מקומית במקרה של כישלון
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
      console.error('Exception adding message:', error);
      // יצירת הודעה מקומית במקרה של כישלון
      return {
        id: `local_${Date.now()}`,
        user_id: message.user_id,
        chat_session_id: message.chat_session_id,
        content: message.content,
        created_at: new Date().toISOString(),
        is_bot: message.is_bot
      };
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
      const response = await axios.patch(`${BACKEND_URL}/api/proxy/chat_sessions/${sessionId}`, updateData);
      
      if (!response.data || response.data.success !== true) {
        console.error('Error updating chat session:', response.data?.error || 'Unknown error');
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
      const response = await axios.get(`${BACKEND_URL}/api/proxy/search_chat_sessions`, {
        params: {
          user_id: userId,
          search_term: searchTerm
        }
      });

      if (!response.data) {
        console.error('Error searching chat sessions');
        return [];
      }

      return response.data as ChatSession[];
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
      const response = await axios.delete(`${BACKEND_URL}/api/proxy/chat_session/${sessionId}`);
      
      if (!response.data || response.data.success !== true) {
        console.error('Error deleting chat session:', response.data?.error || 'Unknown error');
        return false;
      }

      return true;
    } catch (error) {
      console.error('Exception deleting chat session:', error);
      return false;
    }
  }
};

export default chatService;
