import { supabase } from '../../../supabase/config/supabase';
import { v4 as uuidv4 } from 'uuid';

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
      const { data, error } = await supabase
        .from('chat_sessions')
        .insert({
          user_id: userId,
          title: title || null,
          updated_at: new Date().toISOString()
        })
        .select()
        .single();

      if (error) {
        console.error('Error creating chat session:', error);
        return null;
      }

      return data as ChatSession;
    } catch (error) {
      console.error('Exception creating chat session:', error);
      return null;
    }
  },

  /**
   * Gets all chat sessions for a user
   * @param userId The ID of the user
   * @returns Array of chat sessions
   */
  getUserChatSessions: async (userId: string): Promise<ChatSession[]> => {
    try {
      const { data, error } = await supabase
        .from('chat_sessions')
        .select('*')
        .eq('user_id', userId)
        .order('updated_at', { ascending: false });

      if (error) {
        console.error('Error fetching chat sessions:', error);
        return [];
      }

      return data as ChatSession[];
    } catch (error) {
      console.error('Exception fetching chat sessions:', error);
      return [];
    }
  },

  /**
   * Gets a specific chat session with its messages
   * @param sessionId The ID of the chat session
   * @returns Chat session with messages
   */
  getChatSessionWithMessages: async (sessionId: string): Promise<ChatSession | null> => {
    try {
      // Get the chat session
      const { data: sessionData, error: sessionError } = await supabase
        .from('chat_sessions')
        .select('*')
        .eq('id', sessionId)
        .single();

      if (sessionError) {
        console.error('Error fetching chat session:', sessionError);
        return null;
      }

      // Get messages for this session
      const { data: messagesData, error: messagesError } = await supabase
        .from('messages')
        .select('*')
        .eq('chat_session_id', sessionId)
        .order('created_at', { ascending: true });

      if (messagesError) {
        console.error('Error fetching messages:', messagesError);
        return sessionData as ChatSession;
      }

      // Combine session with its messages
      return {
        ...sessionData,
        messages: messagesData
      } as ChatSession;
    } catch (error) {
      console.error('Exception fetching chat session with messages:', error);
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
      // First update the chat session's updated_at timestamp
      await supabase
        .from('chat_sessions')
        .update({ updated_at: new Date().toISOString() })
        .eq('id', message.chat_session_id);

      // Then add the message
      const { data, error } = await supabase
        .from('messages')
        .insert({
          ...message,
          id: uuidv4()
        })
        .select()
        .single();

      if (error) {
        console.error('Error adding message:', error);
        return null;
      }

      return data as Message;
    } catch (error) {
      console.error('Exception adding message:', error);
      return null;
    }
  },

  /**
   * Updates the title of a chat session
   * @param sessionId The ID of the chat session
   * @param title The new title
   * @returns Boolean indicating success
   */
  updateChatSessionTitle: async (sessionId: string, title: string): Promise<boolean> => {
    try {
      const { error } = await supabase
        .from('chat_sessions')
        .update({ 
          title, 
          updated_at: new Date().toISOString() 
        })
        .eq('id', sessionId);

      if (error) {
        console.error('Error updating chat session title:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Exception updating chat session title:', error);
      return false;
    }
  },

  /**
   * Deletes a chat session and all its messages
   * @param sessionId The ID of the chat session to delete
   * @returns Boolean indicating success
   */
  deleteChatSession: async (sessionId: string): Promise<boolean> => {
    try {
      // First delete all messages in the session
      const { error: messagesError } = await supabase
        .from('messages')
        .delete()
        .eq('chat_session_id', sessionId);

      if (messagesError) {
        console.error('Error deleting messages:', messagesError);
        return false;
      }

      // Then delete the session itself
      const { error: sessionError } = await supabase
        .from('chat_sessions')
        .delete()
        .eq('id', sessionId);

      if (sessionError) {
        console.error('Error deleting chat session:', sessionError);
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
