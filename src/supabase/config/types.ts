import { PostgrestError } from '@supabase/supabase-js';

export type Database = {
  public: {
    Tables: {
      documents: {
        Row: {
          id: number;
          name: string;
          type: string;
          size: number;
          url: string;
          created_at: string;
          updated_at: string;
        };
        Insert: Omit<Database['public']['Tables']['documents']['Row'], 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Database['public']['Tables']['documents']['Insert']>;
      };
      users: {
        Row: {
          id: string;
          email: string;
          created_at: string;
          updated_at: string;
          name?: string;
          status?: string;
          last_sign_in?: string;
          preferred_language?: string;
          timezone?: string;
          subscription_plan?: string;
          subscription_expiry?: string;
          metadata?: Record<string, any>;
        };
        Insert: Omit<Database['public']['Tables']['users']['Row'], 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Database['public']['Tables']['users']['Insert']>;
      };
      admins: {
        Row: {
          id: number;
          user_id: string;
          permissions: string[];
          department?: string;
          created_at: string;
          updated_at: string;
        };
        Insert: Omit<Database['public']['Tables']['admins']['Row'], 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Database['public']['Tables']['admins']['Insert']>;
      };
      document_analytics: {
        Row: {
          id: number;
          document_id: number;
          user_id: string;
          action: string;
          created_at: string;
        };
        Insert: Omit<Database['public']['Tables']['document_analytics']['Row'], 'id' | 'created_at'>;
        Update: Partial<Database['public']['Tables']['document_analytics']['Insert']>;
      };
      conversations: {
        Row: {
          conversation_id: string;
          user_id: string;
          title?: string;
          created_at: string;
          updated_at: string;
          is_active: boolean;
          last_message_at?: string;
          model?: string;
          metadata?: Record<string, any>;
        };
        Insert: Omit<Database['public']['Tables']['conversations']['Row'], 'conversation_id' | 'created_at' | 'updated_at'>;
        Update: Partial<Database['public']['Tables']['conversations']['Insert']>;
      };
      messages: {
        Row: {
          message_id: number;
          conversation_id: string;
          user_id: string;
          request?: string;
          response?: string;
          created_at: string;
          status: string;
          status_updated_at: string;
          error_message?: string;
          request_type?: string;
          request_payload?: Record<string, any>;
          response_payload?: Record<string, any>;
          status_code?: number;
          processing_start_time?: string;
          processing_end_time?: string;
          processing_time_ms?: number;
          is_sensitive: boolean;
          metadata?: Record<string, any>;
        };
        Insert: Omit<Database['public']['Tables']['messages']['Row'], 'message_id' | 'created_at' | 'status_updated_at'>;
        Update: Partial<Database['public']['Tables']['messages']['Insert']>;
      };
    };
    Views: {
      admin_users: {
        Row: {
          id: string;
          email: string;
          name?: string;
          created_at: string;
          updated_at: string;
          last_sign_in?: string;
          status?: string;
          admin_id: number;
          permissions: string[];
          department?: string;
        };
      };
    };
    Functions: {
      create_conversation: {
        Args: {
          p_user_id: string;
          p_title?: string;
          p_model?: string;
        };
        Returns: string;
      };
      add_message: {
        Args: {
          p_conversation_id: string;
          p_user_id: string;
          p_request: string;
          p_request_type?: string;
        };
        Returns: number;
      };
      update_response: {
        Args: {
          p_message_id: number;
          p_response: string;
          p_status?: string;
          p_processing_time_ms?: number;
          p_response_payload?: Record<string, any>;
        };
        Returns: boolean;
      };
      get_user_conversations: {
        Args: {
          p_user_id: string;
          p_limit?: number;
          p_offset?: number;
        };
        Returns: {
          conversation_id: string;
          title: string | null;
          created_at: string;
          updated_at: string;
          last_message_at: string | null;
          is_active: boolean;
          model: string | null;
          message_count: number;
          last_message_text: string | null;
        }[];
      };
      get_conversation_messages: {
        Args: {
          p_conversation_id: string;
          p_limit?: number;
          p_offset?: number;
        };
        Returns: {
          message_id: number;
          request: string | null;
          response: string | null;
          created_at: string;
          status: string;
          request_type: string | null;
        }[];
      };
      get_user_chat_statistics: {
        Args: {
          p_user_id: string;
        };
        Returns: {
          total_conversations: number;
          total_messages: number;
          avg_messages_per_conversation: number;
          last_conversation_at: string | null;
          active_conversations: number;
        }[];
      };
      is_admin: {
        Args: {
          user_id: string;
        };
        Returns: boolean;
      };
      promote_to_admin: {
        Args: {
          user_id: string;
          department?: string;
        };
        Returns: boolean;
      };
      get_all_users_and_admins: {
        Args: Record<string, never>;
        Returns: {
          id: string;
          email: string;
          name: string | null;
          created_at: string;
          is_admin: boolean;
          department: string | null;
        }[];
      };
    };
  };
};

export type DbResult<T> = T extends PromiseLike<infer U> ? U : never;
export type DbResultOk<T> = T extends PromiseLike<{ data: infer U }> ? Exclude<U, null> : never;
export type DbResultErr = PostgrestError;

// מודלים נוחים לשימוש
export type User = Database['public']['Tables']['users']['Row'];
export type Admin = Database['public']['Tables']['admins']['Row'];
export type AdminUser = Database['public']['Views']['admin_users']['Row'];
export type Conversation = Database['public']['Tables']['conversations']['Row'];
export type Message = Database['public']['Tables']['messages']['Row'];
export type Document = Database['public']['Tables']['documents']['Row'] & {
  title?: string;
  category?: string;
  uploadDate?: string;
  status?: string;
};

// טיפוסים לתצוגה בממשק המשתמש
export type ConversationWithStats = {
  conversation_id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  last_message_at: string | null;
  is_active: boolean;
  model: string | null;
  message_count: number;
  last_message_text: string | null;
};

export type MessageView = {
  message_id: number;
  request: string | null;
  response: string | null;
  created_at: string;
  status: string;
  request_type: string | null;
};

export type UserChatStats = {
  total_conversations: number;
  total_messages: number;
  avg_messages_per_conversation: number;
  last_conversation_at: string | null;
  active_conversations: number;
}; 