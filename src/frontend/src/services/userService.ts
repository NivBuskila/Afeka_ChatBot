import { supabase, Database } from '../config/supabase';

type User = Database['public']['Tables']['users']['Row'];
type UserInsert = Database['public']['Tables']['users']['Insert'];
type UserUpdate = Database['public']['Tables']['users']['Update'];

type Admin = Database['public']['Tables']['admins']['Row'];
type AdminInsert = Database['public']['Tables']['admins']['Insert'];
type AdminUpdate = Database['public']['Tables']['admins']['Update'];

type AdminUser = Database['public']['Views']['admin_users']['Row'];

export interface UserData {
  id: string;
  email: string;
  firstName?: string;
  lastName?: string;
  role?: string;
}

export const userService = {
  async getCurrentUser(): Promise<UserData | null> {
    const { data: { user }, error } = await supabase.auth.getUser();
    if (error || !user) return null;
    
    return {
      id: user.id,
      email: user.email || '',
      firstName: user.user_metadata?.first_name,
      lastName: user.user_metadata?.last_name,
      role: user.user_metadata?.role,
    };
  },

  async getCurrentUserRole() {
    const { data: { user }, error } = await supabase.auth.getUser();
    if (error || !user) throw error || new Error('No authenticated user');
    
    // בדיקה אם המשתמש הוא מנהל
    const { data: adminData } = await supabase
      .from('admins')
      .select('*')
      .eq('user_id', user.id)
      .maybeSingle();
      
    return adminData ? 'admin' : 'user';
  },

  async isCurrentUserAdmin() {
    try {
      const role = await this.getCurrentUserRole();
      return role === 'admin';
    } catch (error) {
      console.error('Error checking admin status:', error);
      return false;
    }
  },

  async getAllUsers() {
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) throw error;
    return data;
  },

  async getAllAdmins() {
    const { data, error } = await supabase
      .from('admin_users')
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

  async getAdminByUserId(userId: string) {
    const { data, error } = await supabase
      .from('admins')
      .select('*')
      .eq('user_id', userId)
      .maybeSingle();

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

  async createAdmin(admin: AdminInsert) {
    const { data, error } = await supabase
      .from('admins')
      .insert(admin)
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

  async updateAdmin(id: number, updates: AdminUpdate) {
    const { data, error } = await supabase
      .from('admins')
      .update(updates)
      .eq('id', id)
      .select()
      .single();

    if (error) throw error;
    return data;
  },

  async deleteUser(id: string) {
    // בדיקה אם המשתמש הוא מנהל, אם כן - למחוק גם את רשומת המנהל
    await this.deleteAdminByUserId(id);
    
    const { error } = await supabase
      .from('users')
      .delete()
      .eq('id', id);

    if (error) throw error;
  },

  async deleteAdmin(id: number) {
    const { error } = await supabase
      .from('admins')
      .delete()
      .eq('id', id);

    if (error) throw error;
  },

  async deleteAdminByUserId(userId: string) {
    const { error } = await supabase
      .from('admins')
      .delete()
      .eq('user_id', userId);

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
  },

  async updateEmail(newEmail: string): Promise<void> {
    const { error } = await supabase.auth.updateUser({
      email: newEmail,
    });

    if (error) {
      throw new Error(error.message);
    }
  },

  async resetPassword(email: string): Promise<void> {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`,
    });

    if (error) {
      throw new Error(error.message);
    }
  },

  async signInWithGoogle(): Promise<void> {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });

    if (error) {
      throw new Error(error.message);
    }
  },

  async updatePassword(newPassword: string): Promise<void> {
    const { error } = await supabase.auth.updateUser({
      password: newPassword,
    });

    if (error) {
      throw new Error(error.message);
    }
  },

  /**
   * פונקציה מיוחדת לקבלת נתוני משתמשים למטרות אנליטיקה
   * מחזירה נתונים גם אם יש מגבלות RLS
   */
  async getDashboardUsers() {
    try {
      console.log("Fetching dashboard users and admins...");
      
      // ננסה להשתמש בפונקציית RPC החדשה שיצרנו - החדשה מחזירה מערך אחד עם role
      const { data: usersData, error: rpcError } = await supabase.rpc('get_all_users_and_admins');
      
      // בדיקות מפורטות יותר לתוצאה שחזרה
      console.log("RPC result:", { data: usersData, error: rpcError });
      
      if (rpcError) {
        console.error("RPC error:", rpcError);
        return await this.fallbackGetDashboardUsers();
      }
      
      if (!usersData) {
        console.error("No data returned from RPC");
        return await this.fallbackGetDashboardUsers();
      }
      
      if (!Array.isArray(usersData)) {
        console.error("Data returned is not an array:", typeof usersData, usersData);
        
        // אם זה לא מערך אבל כן יש נתונים, ננסה להמיר למערך
        const dataArray = usersData ? [usersData] : [];
        
        if (dataArray.length > 0) {
          console.log("Converted data to array:", dataArray);
          
          // נפריד בין משתמשים רגילים למנהלים לפי השדה role
          const admins = dataArray.filter((user: any) => user.role === 'admin');
          const regularUsers = dataArray.filter((user: any) => user.role !== 'admin');
          
          console.log(`Converted data has ${regularUsers.length} users and ${admins.length} admins`);
          
          return { users: regularUsers, admins };
        }
        
        return await this.fallbackGetDashboardUsers();
      }
      
      // נפריד בין משתמשים רגילים למנהלים לפי השדה role
      const admins = usersData.filter((user: any) => user.role === 'admin');
      const regularUsers = usersData.filter((user: any) => user.role !== 'admin');
      
      console.log(`RPC returned ${regularUsers.length} users and ${admins.length} admins`);
      
      return { users: regularUsers, admins };
    } catch (error) {
      console.error("Error in getDashboardUsers:", error);
      return await this.fallbackGetDashboardUsers();
    }
  },
  
  async fallbackGetDashboardUsers() {
    try {
      console.log("Using fallback method to fetch users and admins...");
  
      // ניסיון לקבל את כל המשתמשים
      const { data: allUsersData, error: allUsersError } = await supabase
        .from('users')
        .select('*')
        .order('created_at', { ascending: false });
  
      if (allUsersError) {
        console.error('Error fetching all users:', allUsersError);
        return { users: [], admins: [] };
      }
      
      // ניסיון לקבל את כל המנהלים כדי לסנן את המשתמשים
      const { data: adminsData, error: adminsError } = await supabase
        .from('admins')
        .select('user_id, department');
      
      if (adminsError) {
        console.error('Error fetching admins:', adminsError);
        // גם אם יש שגיאה, נמשיך עם המשתמשים שכבר יש לנו
      }
      
      // יצירת מפתח של מזהי משתמשים שהם מנהלים
      const adminUserIds = new Set(adminsData?.map(admin => admin.user_id) || []);
      
      // סינון המשתמשים והוספת שדה role לכל משתמש
      const regularUsers = [];
      const admins = [];
      
      for (const user of allUsersData || []) {
        // בדיקה אם המשתמש הוא מנהל
        if (adminUserIds.has(user.id)) {
          // מצא את פרטי המנהל המתאימים
          const adminInfo = adminsData?.find(admin => admin.user_id === user.id);
          
          // הוסף את שדה ה-role ושדות נוספים רלוונטיים
          admins.push({
            ...user,
            role: 'admin',
            department: adminInfo?.department || null
          });
        } else {
          // זהו משתמש רגיל
          regularUsers.push({
            ...user,
            role: 'user'
          });
        }
      }
      
      console.log(`Fallback method found ${regularUsers.length} users and ${admins.length} admins`);
      
      return { users: regularUsers, admins };
    } catch (error) {
      console.error('Error in fallbackGetDashboardUsers:', error);
      return { users: [], admins: [] };
    }
  },
}; 