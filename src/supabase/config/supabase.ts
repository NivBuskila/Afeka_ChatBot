import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://cqvicgimmzrffvarlokq.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxdmljZ2ltbXpyZmZ2YXJsb2txIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5Mjc2NzksImV4cCI6MjA1ODUwMzY3OX0.9RvMl3bU7KRsZNHcc1ST4sY3Rax4-TR8DyVp7Mwqo9Y';

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
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
