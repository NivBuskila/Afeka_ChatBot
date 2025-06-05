// Directly create Supabase client instead of importing
import { createClient } from '@supabase/supabase-js';
// Manual type definition to avoid import issues
type Database = any;

// IMPORTANT: Do not use this client directly for data operations.
// Instead, use the backend proxy endpoints that start with /api/proxy/
// Direct Supabase usage should be limited to:
// 1. Authentication operations that must be client-side
// 2. Storage operations that aren't yet proxied through the backend
// 3. When specifically required for real-time subscriptions
console.log('Initializing Supabase client...');

// If running in browser, use import.meta.env
// Otherwise, fallback to process.env (for SSR/Node.js environments)
// @ts-ignore - Ignore TypeScript warning for import.meta.env
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://cqvicgimmzrffvarlokq.supabase.co';
// Use environment variables with fallback for local development
// @ts-ignore - Ignore TypeScript warning for import.meta.env
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxdmljZ2ltbXpyZmZ2YXJsb2txIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcyNDE0MjgsImV4cCI6MjA2MjgxNzQyOH0.TBCN4icU22HJGHK6ka2_cQjA9tBQ-t3IMCPDstBdaUM';

// Log the configuration
console.log('Supabase Configuration:');
console.log('  - URL:', supabaseUrl);
console.log('  - ANON_KEY:', supabaseAnonKey ? `${supabaseAnonKey.substring(0, 10)}...` : 'Not set');

// Ensure we have the required values
if (!supabaseUrl || !supabaseAnonKey) {
  console.error('ERROR: Missing Supabase environment variables');
  throw new Error('Missing required Supabase configuration. Check your environment variables.');
}

let supabaseClient;

try {
  console.log('Creating Supabase client...');
  supabaseClient = createClient<Database>(supabaseUrl, supabaseAnonKey);
  console.log('Supabase client created successfully');
} catch (error) {
  console.error('Failed to create Supabase client:', error);
  throw error;
}

export const supabase = supabaseClient;

// Export the client and necessary types
export type { Database }; 