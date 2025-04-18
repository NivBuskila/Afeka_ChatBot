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
      
      console.log('Supabase insert data:', sessionInput);
      
      // Create the chat session
      const { data: sessionResult, error: sessionError } = await supabase
        .from('chat_sessions')
        .insert(sessionInput)
        .select()
        .single();

      if (sessionError) {
        console.error('Supabase error creating chat session:', sessionError);
        return null;
      }

      if (!sessionResult) {
        console.error('No data returned from chat session creation');
        return null;
      }

      // Also create a corresponding conversation record
      const conversationData = {
        conversation_id: sessionResult.id, // Use the same ID as the chat session
        user_id: userId,
        title: title || null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        is_active: true
      };

      const { error: conversationError } = await supabase
        .from('conversations')
        .insert(conversationData);

      if (conversationError) {
        console.error('Error creating corresponding conversation:', conversationError);
        // Continue anyway since the chat session was created
      } else {
        console.log('Conversation record created successfully');
      }

      console.log('Chat session created successfully:', sessionResult);
      return sessionResult as ChatSession;
    } catch (error) {
      console.error('Exception in createChatSession:', error);
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
      console.log('Fetching chat session with ID:', sessionId);
      
      // Get the chat session
      const { data: sessionResult, error: sessionError } = await supabase
        .from('chat_sessions')
        .select('*')
        .eq('id', sessionId)
        .single();

      if (sessionError) {
        console.error('Error fetching chat session:', sessionError);
        return null;
      }

      if (!sessionResult) {
        console.error('No session data found for ID:', sessionId);
        return null;
      }

      console.log('Session data retrieved:', sessionResult);
      
      // Get messages for this session using conversation_id
      const { data: messagesData, error: messagesError } = await supabase
        .from('messages')
        .select('*')
        .eq('conversation_id', sessionId)
        .order('created_at', { ascending: true });

      if (messagesError) {
        console.error('Error fetching messages for session:', messagesError);
        // Return the session without messages if there was an error fetching messages
        return {
          ...sessionResult,
          messages: []
        } as ChatSession;
      }

      console.log(`Retrieved ${messagesData?.length || 0} messages for session`);
      
      // Process messages to normalize content from the actual schema
      const processedMessages = (messagesData || []).map(msg => {
        // Create a normalized message object
        const normalizedMsg: any = {
          id: msg.message_id?.toString() || msg.id,
          user_id: msg.user_id,
          chat_session_id: sessionId,
          created_at: msg.created_at,
          // Determine if it's a bot message - if response is filled and request is empty/null
          is_bot: msg.is_bot !== undefined ? msg.is_bot : (!!msg.response && !msg.request)
        };
        
        // Set content from the appropriate field
        if (normalizedMsg.is_bot) {
          // Bot message content comes from response
          normalizedMsg.content = msg.response || msg.content || '';
        } else {
          // User message content comes from request
          normalizedMsg.content = msg.request || msg.content || '';
        }
        
        return normalizedMsg;
      });

      // Combine session with its messages
      const sessionWithMessages = {
        ...sessionResult,
        messages: processedMessages
      } as ChatSession;
      
      return sessionWithMessages;
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
      console.log('Adding message to session:', message.chat_session_id);
      
      // First update the chat session's updated_at timestamp
      const { error: updateError } = await supabase
        .from('chat_sessions')
        .update({ updated_at: new Date().toISOString() })
        .eq('id', message.chat_session_id);
      
      if (updateError) {
        console.error('Error updating chat session timestamp:', updateError);
      }

      // Also update the conversation's updated_at timestamp
      const { error: conversationUpdateError } = await supabase
        .from('conversations')
        .update({ 
          updated_at: new Date().toISOString(),
          last_message_at: new Date().toISOString()
        })
        .eq('conversation_id', message.chat_session_id);
      
      if (conversationUpdateError) {
        console.error('Error updating conversation timestamp:', conversationUpdateError);
      }

      // Get column information from the messages table to understand the schema
      const { data: columnInfo, error: columnError } = await supabase
        .from('messages')
        .select('*')
        .limit(1);
      
      if (columnError) {
        console.error('Error fetching message schema:', columnError);
        return null;
      }

      if (columnInfo && columnInfo.length > 0) {
        const columns = Object.keys(columnInfo[0]);
        console.log('Available columns in messages table:', columns);
        
        // Determine which fields to use based on the schema
        const hasPrimaryKey = columns.includes('message_id');
        const hasConversationId = columns.includes('conversation_id');
        const hasRequest = columns.includes('request');
        const hasResponse = columns.includes('response');
        
        // Create message data with the appropriate schema
        let messageData: any = {};
        
        // Set the primary key
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
        
        console.log('Inserting message with adapted schema:', messageData);
        
        // Insert the message
        const { data, error } = await supabase
          .from('messages')
          .insert(messageData)
          .select();
        
        if (error) {
          console.error('Error adding message:', error);
          return null;
        }
        
        console.log('Message inserted successfully:', data);
        
        // Create a normalized message object to return
        const normalizedMessage: Message = {
          id: data[0].message_id?.toString() || data[0].id,
          user_id: message.user_id,
          chat_session_id: message.chat_session_id,
          content: message.content,
          created_at: new Date().toISOString(),
          is_bot: message.is_bot
        };
        
        return normalizedMessage;
      } else {
        console.error('No column information available');
        return null;
      }
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

      // First search for chat sessions with matching titles
      const { data: titleMatches, error: titleError } = await supabase
        .from('chat_sessions')
        .select('*')
        .eq('user_id', userId)
        .ilike('title', `%${searchTerm}%`);

      if (titleError) {
        console.error('Error searching chat sessions by title:', titleError);
      }

      // Then search for messages with matching content
      const { data: messageMatches, error: messageError } = await supabase
        .from('messages')
        .select('conversation_id')
        .eq('user_id', userId)
        .or(`request.ilike.%${searchTerm}%,response.ilike.%${searchTerm}%`);

      if (messageError) {
        console.error('Error searching messages:', messageError);
      }

      // Get unique session IDs from message matches
      const matchedSessionIds = messageMatches 
        ? [...new Set(messageMatches.map(m => m.conversation_id))]
        : [];

      // If we have session IDs from message content, fetch those sessions
      let contentMatchSessions: ChatSession[] = [];
      if (matchedSessionIds.length > 0) {
        const { data: sessions, error: sessionsError } = await supabase
          .from('chat_sessions')
          .select('*')
          .eq('user_id', userId)
          .in('id', matchedSessionIds);

        if (sessionsError) {
          console.error('Error fetching message-matched sessions:', sessionsError);
        } else {
          contentMatchSessions = sessions as ChatSession[];
        }
      }

      // Combine and deduplicate results
      const allSessions = [...(titleMatches || []), ...contentMatchSessions];
      const uniqueSessions = Array.from(
        new Map(allSessions.map(session => [session.id, session])).values()
      );

      // Sort by updated_at (newest first)
      return uniqueSessions.sort((a, b) => 
        new Date(b.updated_at || b.created_at).getTime() - 
        new Date(a.updated_at || a.created_at).getTime()
      );
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
      // First delete all messages in the session
      const { error: messagesError } = await supabase
        .from('messages')
        .delete()
        .eq('conversation_id', sessionId);

      if (messagesError) {
        console.error('Error deleting messages:', messagesError);
        return false;
      }

      // Delete the conversation record
      const { error: conversationError } = await supabase
        .from('conversations')
        .delete()
        .eq('conversation_id', sessionId);

      if (conversationError) {
        console.error('Error deleting conversation:', conversationError);
        // Continue anyway to delete the chat session
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
