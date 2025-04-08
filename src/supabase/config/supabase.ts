import { createClient } from '@supabase/supabase-js';
import { Database } from './types';

// התאמה לפי סביבת הריצה
const isNode = typeof window === 'undefined';
// @ts-ignore - יש להתעלם מאזהרת TypeScript עבור import.meta.env
const envVars = isNode ? process.env : import.meta.env;

const supabaseUrl = (envVars.VITE_SUPABASE_URL || envVars.NEXT_PUBLIC_SUPABASE_URL) || 'https://cqvicgimmzrffvarlokq.supabase.co';
const supabaseAnonKey = (envVars.VITE_SUPABASE_ANON_KEY || envVars.NEXT_PUBLIC_SUPABASE_ANON_KEY) || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxdmljZ2ltbXpyZmZ2YXJsb2txIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5Mjc2NzksImV4cCI6MjA1ODUwMzY3OX0.9RvMl3bU7KRsZNHcc1ST4sY3Rax4-TR8DyVp7Mwqo9Y';

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey);

// ייצוא טיפוסים מקובץ types.ts
export * from './types';

export type Document = Database['public']['Tables']['documents']['Row'] & {
  title?: string;
  category?: string;
  uploadDate?: string;
  status?: string;
};
