// @ts-ignore - Import may not be available in all environments
import { createClient } from '@supabase/supabase-js';

// Get Supabase configuration from environment variables only
// @ts-ignore - Ignore TypeScript warning for import.meta.env
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
// @ts-ignore - Ignore TypeScript warning for import.meta.env
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Validate required environment variables
if (!supabaseUrl || !supabaseAnonKey) {
  const errorMessage = `Missing required Supabase environment variables:
    ${!supabaseUrl ? '❌ VITE_SUPABASE_URL' : '✅ VITE_SUPABASE_URL'}
    ${!supabaseAnonKey ? '❌ VITE_SUPABASE_ANON_KEY' : '✅ VITE_SUPABASE_ANON_KEY'}
  
  Please check your .env file and ensure these variables are set.`;
  
  console.error(errorMessage);
  throw new Error('Missing required Supabase configuration. Check your environment variables.');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

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
          role: string;
          created_at: string;
          updated_at: string;
        };
        Insert: Omit<Database['public']['Tables']['users']['Row'], 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Database['public']['Tables']['users']['Insert']>;
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
      chat_sessions: {
        Row: {
          id: string;
          user_id: string;
          title: string | null;
          created_at: string;
          updated_at: string | null;
        };
        Insert: Omit<Database['public']['Tables']['chat_sessions']['Row'], 'id' | 'created_at'>;
        Update: Partial<Omit<Database['public']['Tables']['chat_sessions']['Row'], 'id' | 'created_at'>>;
      };
      messages: {
        Row: {
          id: string;
          user_id: string;
          chat_session_id: string;
          content: string;
          created_at: string;
          is_bot: boolean;
        };
        Insert: Omit<Database['public']['Tables']['messages']['Row'], 'id' | 'created_at'>;
        Update: Partial<Omit<Database['public']['Tables']['messages']['Row'], 'id'>>;
      };
    };
  };
};

export type Document = Database['public']['Tables']['documents']['Row'] & {
  title?: string;
  category?: string;
  uploadDate?: string;
  status?: string;
};
