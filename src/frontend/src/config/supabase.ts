// Directly create Supabase client instead of importing
import { createClient } from '@supabase/supabase-js';
import { Database } from '../../../supabase/config/types';

// If running in browser, use import.meta.env
// Otherwise, fallback to process.env (for SSR/Node.js environments)
// @ts-ignore - יש להתעלם מאזהרת TypeScript עבור import.meta.env
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://cqvicgimmzrffvarlokq.supabase.co';
// Use environment variables with fallback for local development
// @ts-ignore - יש להתעלם מאזהרת TypeScript עבור import.meta.env
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxdmljZ2ltbXpyZmZ2YXJsb2txIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5Mjc2NzksImV4cCI6MjA1ODUwMzY3OX0.9RvMl3bU7KRsZNHcc1ST4sY3Rax4-TR8DyVp7Mwqo9Y';

// Ensure we have the required values
if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Missing Supabase environment variables');
}

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey);

// ייצוא טיפוסים מקובץ types.ts
export * from '../../../supabase/config/types'; 