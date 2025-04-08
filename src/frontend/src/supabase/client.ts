import { createClient } from '@supabase/supabase-js';
import { Database } from '../../../supabase/config/types';

// אם אנחנו בדפדפן, משתמשים ב-import.meta.env
// אחרת, משתמשים ב-process.env (לסביבות SSR/Node.js)
// @ts-ignore - יש להתעלם מאזהרת TypeScript עבור import.meta.env
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://cqvicgimmzrffvarlokq.supabase.co';
// משתמשים במשתני סביבה עם ברירת מחדל לפיתוח מקומי
// @ts-ignore - יש להתעלם מאזהרת TypeScript עבור import.meta.env
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxdmljZ2ltbXpyZmZ2YXJsb2txIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI5Mjc2NzksImV4cCI6MjA1ODUwMzY3OX0.9RvMl3bU7KRsZNHcc1ST4sY3Rax4-TR8DyVp7Mwqo9Y';

// וידוא שיש לנו את הערכים הנדרשים
if (!supabaseUrl || !supabaseAnonKey) {
  console.error('חסרים משתני סביבה של Supabase');
}

// יצירת לקוח Supabase
export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey);

// ייצוא טיפוסים מקובץ types.ts
export * from '../../../supabase/config/types'; 