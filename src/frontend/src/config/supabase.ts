// Re-export everything from the new Supabase location
import * as SupabaseExports from '../../../supabase/config/supabase';

export const supabase = SupabaseExports.supabase;
export type Database = SupabaseExports.Database;
export type Document = SupabaseExports.Document; 