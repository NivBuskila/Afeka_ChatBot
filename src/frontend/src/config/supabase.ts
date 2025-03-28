// Directly create Supabase client instead of importing
import { createClient } from '@supabase/supabase-js';

// Use environment variables
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://cqvicgimmzrffvarlokq.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Type definitions
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
    };
  };
};

export type Document = Database['public']['Tables']['documents']['Row'] & {
  title?: string;
  category?: string;
  uploadDate?: string;
  status?: string;
}; 