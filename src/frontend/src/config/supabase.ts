// Directly create Supabase client instead of importing
import { createClient } from '@supabase/supabase-js';
// Manual type definition to avoid import issues
type Database = any;

// Document type definition
export interface Document {
  id: string;
  name: string;
  type: string;
  size: number;
  url: string;
  created_at: string;
  updated_at: string;
}

// IMPORTANT: Do not use this client directly for data operations.
// Instead, use the backend proxy endpoints that start with /api/proxy/
// Direct Supabase usage should be limited to:
// 1. Authentication operations that must be client-side
// 2. Storage operations that aren't yet proxied through the backend
// 3. When specifically required for real-time subscriptions

// Get Supabase configuration from environment variables
// @ts-ignore - Ignore TypeScript warning for import.meta.env
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
// @ts-ignore - Ignore TypeScript warning for import.meta.env
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Configuration validation

// Ensure we have the required values
if (!supabaseUrl || !supabaseAnonKey) {
  const errorMessage = `Missing required Supabase environment variables:
    ${!supabaseUrl ? '❌ VITE_SUPABASE_URL' : '✅ VITE_SUPABASE_URL'}
    ${!supabaseAnonKey ? '❌ VITE_SUPABASE_ANON_KEY' : '✅ VITE_SUPABASE_ANON_KEY'}
  
  Please check your .env file and ensure these variables are set.`;
  
  console.error(errorMessage);
  throw new Error('Missing required Supabase configuration. Check your environment variables.');
}

let supabaseClient;

try {
  supabaseClient = createClient<Database>(supabaseUrl, supabaseAnonKey);
} catch (error) {
  console.error('Failed to create Supabase client:', error);
  throw error;
}

export const supabase = supabaseClient;

// Export the client and necessary types
export type { Database }; 