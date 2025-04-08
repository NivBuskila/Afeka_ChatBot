import { createClient } from '@supabase/supabase-js';
import { Database, Conversation, Message, ConversationWithStats, MessageView, UserChatStats } from '../config/types';

// יצירת לקוח Supabase
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
const supabase = createClient<Database>(supabaseUrl, supabaseKey);

/**
 * יצירת שיחה חדשה
 */
export async function createNewConversation(
  userId: string,
  title?: string,
  model: string = 'default'
): Promise<string | null> {
  try {
    const { data, error } = await supabase.rpc('create_conversation', {
      p_user_id: userId,
      p_title: title,
      p_model: model
    });

    if (error) {
      console.error('Error creating conversation:', error);
      return null;
    }

    return data;
  } catch (error) {
    console.error('Exception creating conversation:', error);
    return null;
  }
}

/**
 * הוספת הודעה לשיחה
 */
export async function addMessageToConversation(
  conversationId: string,
  userId: string,
  request: string,
  requestType: string = 'TEXT'
): Promise<number | null> {
  try {
    const { data, error } = await supabase.rpc('add_message', {
      p_conversation_id: conversationId,
      p_user_id: userId,
      p_request: request,
      p_request_type: requestType
    });

    if (error) {
      console.error('Error adding message:', error);
      return null;
    }

    return data;
  } catch (error) {
    console.error('Exception adding message:', error);
    return null;
  }
}

/**
 * עדכון תשובה להודעה
 */
export async function updateMessageResponse(
  messageId: number,
  response: string,
  status: string = 'COMPLETED',
  processingTimeMs?: number,
  responsePayload?: Record<string, any>
): Promise<boolean> {
  try {
    const { data, error } = await supabase.rpc('update_response', {
      p_message_id: messageId,
      p_response: response,
      p_status: status,
      p_processing_time_ms: processingTimeMs,
      p_response_payload: responsePayload
    });

    if (error) {
      console.error('Error updating response:', error);
      return false;
    }

    return data;
  } catch (error) {
    console.error('Exception updating response:', error);
    return false;
  }
}

/**
 * קבלת רשימת שיחות עבור משתמש
 */
export async function getUserConversations(
  userId: string,
  limit: number = 10,
  offset: number = 0
): Promise<ConversationWithStats[]> {
  try {
    const { data, error } = await supabase.rpc('get_user_conversations', {
      p_user_id: userId,
      p_limit: limit,
      p_offset: offset
    });

    if (error) {
      console.error('Error fetching conversations:', error);
      return [];
    }

    return data || [];
  } catch (error) {
    console.error('Exception fetching conversations:', error);
    return [];
  }
}

/**
 * קבלת הודעות עבור שיחה מסוימת
 */
export async function getConversationMessages(
  conversationId: string,
  limit: number = 100,
  offset: number = 0
): Promise<MessageView[]> {
  try {
    const { data, error } = await supabase.rpc('get_conversation_messages', {
      p_conversation_id: conversationId,
      p_limit: limit,
      p_offset: offset
    });

    if (error) {
      console.error('Error fetching messages:', error);
      return [];
    }

    return data || [];
  } catch (error) {
    console.error('Exception fetching messages:', error);
    return [];
  }
}

/**
 * קבלת סטטיסטיקות צ'אט עבור משתמש
 */
export async function getUserChatStatistics(userId: string): Promise<UserChatStats | null> {
  try {
    const { data, error } = await supabase.rpc('get_user_chat_statistics', {
      p_user_id: userId
    });

    if (error) {
      console.error('Error fetching chat statistics:', error);
      return null;
    }

    return data && data.length > 0 ? data[0] : null;
  } catch (error) {
    console.error('Exception fetching chat statistics:', error);
    return null;
  }
}

/**
 * מחיקת שיחה ספציפית
 */
export async function deleteConversation(conversationId: string): Promise<boolean> {
  try {
    const { error } = await supabase
      .from('conversations')
      .delete()
      .eq('conversation_id', conversationId);

    if (error) {
      console.error('Error deleting conversation:', error);
      return false;
    }

    return true;
  } catch (error) {
    console.error('Exception deleting conversation:', error);
    return false;
  }
}

/**
 * עדכון נתוני שיחה
 */
export async function updateConversation(
  conversationId: string,
  updates: Partial<Conversation>
): Promise<boolean> {
  try {
    const { error } = await supabase
      .from('conversations')
      .update(updates)
      .eq('conversation_id', conversationId);

    if (error) {
      console.error('Error updating conversation:', error);
      return false;
    }

    return true;
  } catch (error) {
    console.error('Exception updating conversation:', error);
    return false;
  }
}

/**
 * הפעלה/השבתה של שיחה
 */
export async function toggleConversationActive(
  conversationId: string, 
  isActive: boolean
): Promise<boolean> {
  return updateConversation(conversationId, { is_active: isActive });
}

/**
 * תהליך שלם של יצירת שיחה ושליחת הודעה ראשונה
 */
export async function startNewConversation(
  userId: string,
  initialMessage: string
): Promise<{ conversationId: string; messageId: number } | null> {
  try {
    // 1. יצירת שיחה חדשה
    const conversationId = await createNewConversation(userId);
    if (!conversationId) {
      return null;
    }

    // 2. הוספת הודעה ראשונה
    const messageId = await addMessageToConversation(conversationId, userId, initialMessage);
    if (!messageId) {
      return null;
    }

    // 3. החזרת מזהי השיחה וההודעה
    return { conversationId, messageId };
  } catch (error) {
    console.error('Exception starting new conversation:', error);
    return null;
  }
}

/**
 * תהליך שלם של שליחת הודעה וקבלת תשובה
 */
export async function sendMessageAndGetResponse(
  conversationId: string,
  userId: string,
  message: string,
  aiResponseGenerator: (message: string) => Promise<string>
): Promise<{ success: boolean; messageId?: number; response?: string }> {
  try {
    // 1. הוספת ההודעה
    const messageId = await addMessageToConversation(conversationId, userId, message);
    if (!messageId) {
      return { success: false };
    }

    try {
      // 2. עדכון סטטוס לעיבוד
      await updateMessageResponse(messageId, '', 'PROCESSING');

      // 3. קבלת תשובה מה-AI
      const processingStartTime = Date.now();
      const response = await aiResponseGenerator(message);
      const processingTimeMs = Date.now() - processingStartTime;

      // 4. עדכון התשובה
      await updateMessageResponse(
        messageId,
        response,
        'COMPLETED',
        processingTimeMs
      );

      return {
        success: true,
        messageId,
        response
      };
    } catch (error) {
      // במקרה של שגיאה בקבלת התשובה
      console.error('Error getting AI response:', error);
      await updateMessageResponse(
        messageId,
        'שגיאה בעיבוד ההודעה. אנא נסה שנית.',
        'FAILED',
        undefined,
        { error: error instanceof Error ? error.message : 'Unknown error' }
      );

      return { success: false, messageId };
    }
  } catch (error) {
    console.error('Exception in send message flow:', error);
    return { success: false };
  }
} 