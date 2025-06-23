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
    
    // Check if user has admin role in metadata
    const isAdminInMetadata = user.user_metadata?.is_admin === true || 
                              user.user_metadata?.role === 'admin';
    
    if (isAdminInMetadata) {
      // If user should be admin in metadata, ensure they're also in admins table
      try {
        await supabase.rpc('promote_to_admin', { user_id: user.id });
        return 'admin';
      } catch (error) {
        // Silent fail
      }
    }
    
    // Check if user is admin in admins table
    const { data: adminData } = await supabase
      .from('admins')
      .select('*')
      .eq('user_id', user.id)
      .maybeSingle();
    
    // Update user metadata if found in admins table
    if (adminData && !isAdminInMetadata) {
      try {
        await supabase.auth.updateUser({
          data: { is_admin: true }
        });
      } catch (error) {
        // Silent fail
      }
    }
      
    return adminData ? 'admin' : 'user';
  },

  async isCurrentUserAdmin() {
    try {
      const role = await this.getCurrentUserRole();
      return role === 'admin';
    } catch (error) {
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
    // Check if user is admin, if so delete admin record first
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
    try {
        // 1. Register user in auth service
        const { data: authData, error: authError } = await supabase.auth.signUp({
            email,
            password,
            options: {
                data: {
                    is_admin: isAdmin,
                    role: isAdmin ? 'admin' : 'user',
                    name: email.split('@')[0]
                }
            }
        });
        
        if (authError) {
            throw authError;
        }
        
        if (!authData.user) {
            throw new Error('User registration failed - no user data');
        }
        
        // 2. Check if user already exists in admin list
        const { data: existingUser, error: checkError } = await supabase
            .from('users')
            .select('id')
            .eq('id', authData.user.id)
            .maybeSingle();
            
        // If user doesn't exist in table yet, try creating manually
        if (!existingUser && !checkError) {
            const { error: insertUserError } = await supabase
                .from('users')
                .insert({
                    id: authData.user.id,
                    email: email,
                    name: email.split('@')[0],
                    status: 'active',
                    last_sign_in: new Date().toISOString(),
                    preferred_language: 'he',
                    timezone: 'Asia/Jerusalem'
                });
            
            if (insertUserError) {
                // Don't delete user from Auth, rely on trigger to handle it on next login
            } else {
                // User inserted successfully
            }
        } else if (existingUser) {
            // User already exists in users table
        } else if (checkError) {
            // Silent fail
        }
        
        // 3. The code to add a user to the admins table if needed
        if (isAdmin) {
            // Check if the user is already in the admins table
            const { data: existingAdmin, error: checkAdminError } = await supabase
                .from('admins')
                .select('id')
                .eq('user_id', authData.user.id)
                .maybeSingle();
                
            if (!existingAdmin && !checkAdminError) {
                const { error: adminError } = await supabase
                    .from('admins')
                    .insert({ user_id: authData.user.id });
                
                if (adminError) {
                    // Don't throw here, user is still created as regular user
                } else {
                    // Admin role set successfully
                }
            } else if (existingAdmin) {
                // User is already an admin
            }
        }
        
        return authData;
    } catch (error) {
        throw error;
    }
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
   * Special function to get user data for analytics purposes
   * Returns data even with RLS restrictions
   */
  async getDashboardUsers() {
    try {
      // Check if we're in development and should use fallback immediately
      const isDevelopment = process.env.NODE_ENV === 'development';
      
      if (isDevelopment) {
        return await this.fallbackGetDashboardUsers();
      }

      // Try using the RPC function first
      const { data: usersData, error: rpcError } = await supabase.rpc('get_all_users_and_admins');
      
      if (rpcError) {
        return await this.fallbackGetDashboardUsers();
      }
      
      if (!usersData) {
        return await this.fallbackGetDashboardUsers();
      }
      
      if (!Array.isArray(usersData)) {
        
        // If it's not an array but data exists, try converting to array
        const dataArray = usersData ? [usersData] : [];
        
        if (dataArray.length > 0) {
          // Separate regular users and admins by is_admin field
          const admins = dataArray.filter((user: any) => user.is_admin === true);
          const regularUsers = dataArray.filter((user: any) => user.is_admin !== true);
          
          return { users: regularUsers, admins };
        }
        
        return await this.fallbackGetDashboardUsers();
      }
      
      // Separate regular users and admins by is_admin field
      const admins = usersData.filter((user: any) => user.is_admin === true);
      const regularUsers = usersData.filter((user: any) => user.is_admin !== true);
      
      return { users: regularUsers, admins };
    } catch (error) {
      return await this.fallbackGetDashboardUsers();
    }
  },
  
  async fallbackGetDashboardUsers() {
    try {
      // Attempt to get all users
      const { data: allUsersData, error: allUsersError } = await supabase
        .from('users')
        .select('*')
        .order('created_at', { ascending: false });
  
      if (allUsersError) {
        return { users: [], admins: [] };
      }
      
      // Attempt to get all admins to filter users
      const { data: adminsData, error: adminsError } = await supabase
        .from('admins')
        .select('user_id, department');
      
      if (adminsError) {
        // Even if there's an error, continue with the users we already have
      }
      
      // Create a set of user IDs that are admins
      const adminUserIds = new Set(adminsData?.map(admin => admin.user_id) || []);
      
      // Filter users and add is_admin field to each user
      const regularUsers = [];
      const admins = [];
      
      for (const user of allUsersData || []) {
        // Check if the user is an admin
        if (adminUserIds.has(user.id)) {
          // Find the corresponding admin details
          const adminInfo = adminsData?.find(admin => admin.user_id === user.id);
          
          // Add the is_admin field and other relevant fields
          admins.push({
            ...user,
            is_admin: true,
            department: adminInfo?.department || null
          });
        } else {
          // This is a regular user
          regularUsers.push({
            ...user,
            is_admin: false
          });
        }
      }
      
      return { users: regularUsers, admins };
    } catch (error) {
      return { users: [], admins: [] };
    }
  },

  promoteUserFromMetadata: async (userId: string, isAdminValue: boolean) => {
    try {
      const { error } = await supabase
        .from('user_metadata')
        .update({ is_admin: isAdminValue })
        .eq('user_id', userId);
      
      return !error;
    } catch (error) {
      return false;
    }
  },

  updateUserMetadata: async (userId: string, metadata: any) => {
    try {
      const { error } = await supabase
        .from('user_metadata')
        .upsert({ user_id: userId, ...metadata });
      
      return !error;
    } catch (error) {
      return false;
    }
  },

  checkIsAdmin: async (userId: string): Promise<boolean> => {
    try {
      const { data } = await supabase
        .from('admins')
        .select('id')
        .eq('user_id', userId)
        .maybeSingle();
      
      return !!data;
    } catch (error) {
      return false;
    }
  },

  signUpWithAdditionalMetadata: async (email: string, password: string, isAdmin: boolean, displayName?: string, additionalMetadata: any = {}) => {
    try {
      const { data: authData, error: authError } = await supabase.auth.signUp({
        email: email.toLowerCase().trim(),
        password,
        options: {
          data: {
            display_name: displayName || email.split('@')[0],
            ...additionalMetadata
          }
        }
      });

      if (authError) {
        throw authError;
      }

      if (!authData.user) {
        throw new Error('No user data returned');
      }

      const userId = authData.user.id;
      
      // Check if user already exists in our users table
      const { data: existingUser, error: checkError } = await supabase
        .from('users')
        .select('id')
        .eq('id', userId)
        .maybeSingle();

      if (checkError && checkError.code !== 'PGRST116') {
        // Ignore only if error is "not found"
        throw checkError;
      }

      if (!existingUser) {
        // Create user record
        const { error: insertUserError } = await supabase
          .from('users')
          .insert([{ 
            id: userId,
            email: email.toLowerCase().trim(),
            display_name: displayName || email.split('@')[0]
          }]);
          
        if (insertUserError) {
          throw insertUserError;
        }
      }
      
      // Set admin role if needed
      if (isAdmin) {
        const { error: adminError } = await supabase
          .from('admins')
          .insert([{ user_id: userId }]);
          
        if (adminError) {
          // Log but don't fail registration
        }
      }

      return { user: authData.user, error: null };
    } catch (error: any) {
      return { user: null, error };
    }
  },


}; 