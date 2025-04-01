import { supabase, Database } from '../config/supabase';

type User = Database['public']['Tables']['users']['Row'];
type UserInsert = Database['public']['Tables']['users']['Insert'];
type UserUpdate = Database['public']['Tables']['users']['Update'];

export const userService = {
  async getCurrentUser() {
    const { data: { user }, error } = await supabase.auth.getUser();
    if (error) throw error;
    return user;
  },

  async getAllUsers() {
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) throw error;
    return data;
  },

  async getUserById(id: string) {
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('id', id)
      .single();

    if (error) throw error;
    return data;
  },

  async createUser(user: UserInsert) {
    const { data, error } = await supabase
      .from('users')
      .insert(user)
      .select()
      .single();

    if (error) throw error;
    return data;
  },

  async updateUser(id: string, updates: UserUpdate) {
    const { data, error } = await supabase
      .from('users')
      .update(updates)
      .eq('id', id)
      .select()
      .single();

    if (error) throw error;
    return data;
  },

  async deleteUser(id: string) {
    const { error } = await supabase
      .from('users')
      .delete()
      .eq('id', id);

    if (error) throw error;
  },

  async signIn(email: string, password: string) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) throw error;
    return data;
  },

  async signOut() {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
  },

<<<<<<< Updated upstream
=======
  async signUp(email: string, password: string, isAdmin: boolean = false) {
    // 1. רישום המשתמש בשירות האימות
    const { data: authData, error: authError } = await supabase.auth.signUp({
      email,
      password,
    });
    
    if (authError) {
      // אם המשתמש כבר רשום, ננסה להתחבר כדי לקבל את ה-ID שלו
      if (authError.message.includes('User already registered')) {
        // ננסה להתחבר ולקבל את פרטי המשתמש
        const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        
        if (signInError) throw signInError;
        if (!signInData.user) throw new Error('Could not authenticate with existing user');
        
        // אם מבקשים להפוך למנהל, נשתמש בפונקציית RPC שתיקנו
        if (isAdmin) {
          try {
            const { data: promoteResult, error: promoteError } = await supabase.rpc('promote_to_admin', {
              user_id: signInData.user.id
            });
            
            if (promoteError) {
              console.error('Error promoting user to admin:', promoteError);
              // לא נזרוק שגיאה, נמשיך למרות השגיאה
            } else {
              console.log('User promoted to admin:', promoteResult);
            }
          } catch (adminError) {
            console.error('Error in admin promotion RPC call:', adminError);
          }
        }
        
        return signInData;
      }
      
      // אם יש שגיאה אחרת, נזרוק אותה
      throw authError;
    }
    
    if (!authData.user) throw new Error('User registration failed');
    
    // 2. הוספת המשתמש לטבלת המשתמשים
    try {
      const { error: insertUserError } = await supabase
        .from('users')
        .insert({
          id: authData.user.id,
          email: email,
          name: email.split('@')[0], // שם ברירת מחדל מהאימייל
          status: 'active'
        });

      if (insertUserError) {
        console.error('Error inserting user:', insertUserError);
        throw insertUserError;
      }
      
      // 3. אם מדובר במנהל, נשתמש בפונקציית RPC במקום הכנסה ישירה לטבלה
      if (isAdmin) {
        try {
          const { data: promoteResult, error: promoteError } = await supabase.rpc('promote_to_admin', {
            user_id: authData.user.id
          });
          
          if (promoteError) {
            console.error('Error promoting user to admin:', promoteError);
            // לא נזרוק שגיאה, נמשיך למרות זאת כדי לאפשר לפחות התחברות רגילה
          } else {
            console.log('User promoted to admin successfully:', promoteResult);
          }
        } catch (adminError) {
          console.error('Error in admin promotion RPC call:', adminError);
          // נמשיך לתת למשתמש להירשם למרות שגיאת המנהל
        }
      }
    } catch (error) {
      console.error('Error in user creation:', error);
      throw error;
    }
    
    return authData;
  },

>>>>>>> Stashed changes
  async getUserProfile(id: string) {
    const { data, error } = await supabase.rpc('get_user_profile', {
      user_id: id
    });

    if (error) throw error;
    return data;
  },

  async getUserActivitySummary(id: string, days: number = 30) {
    const { data, error } = await supabase.rpc('get_user_activity_summary', {
      user_id: id,
      days: days
    });

    if (error) throw error;
    return data;
  },

  async getUserSecurityStatus(id: string) {
    const { data, error } = await supabase.rpc('get_user_security_status', {
      user_id: id
    });

    if (error) throw error;
    return data;
  },

  async getUserSecurityEvents(id: string, limit: number = 10) {
    const { data, error } = await supabase.rpc('get_user_security_events', {
      user_id: id,
      limit_count: limit
    });

    if (error) throw error;
    return data;
  }
}; 