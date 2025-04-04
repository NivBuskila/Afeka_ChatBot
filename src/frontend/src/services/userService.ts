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
    
    // Check if user is admin
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
    // 1. Register user in auth service
    const { data: authData, error: authError } = await supabase.auth.signUp({
      email,
      password,
    });
    
    if (authError) {
      // If user already registered, try to sign in to get ID
      if (authError.message.includes('User already registered')) {
        // Try signing in to get user details
        const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        
        if (signInError) throw signInError;
        if (!signInData.user) throw new Error('Could not authenticate with existing user');
        
        // If admin promotion requested, use the RPC function
        if (isAdmin) {
          try {
            const { data: promoteResult, error: promoteError } = await supabase.rpc('promote_to_admin', {
              user_id: signInData.user.id
            });
            
            if (promoteError) {
              console.error('Error promoting user to admin:', promoteError);
              // Continue despite error
            } else {
              console.log('User promoted to admin:', promoteResult);
            }
          } catch (adminError) {
            console.error('Error in admin promotion RPC call:', adminError);
          }
        }
        
        return signInData;
      }
      
      // Throw other errors
      throw authError;
    }
    
    if (!authData.user) throw new Error('User registration failed');
    
    // 2. Add user to users table
    try {
      const { error: insertUserError } = await supabase
        .from('users')
        .insert({
          id: authData.user.id,
          email: email,
          name: email.split('@')[0], // Default name from email
          status: 'active'
        });

      if (insertUserError) {
        console.error('Error inserting user:', insertUserError);
        throw insertUserError;
      }
      
      // 3. If it's an admin, use the RPC function instead of direct insertion
      if (isAdmin) {
        try {
          const { data: promoteResult, error: promoteError } = await supabase.rpc('promote_to_admin', {
            user_id: authData.user.id
          });
          
          if (promoteError) {
            console.error('Error promoting user to admin:', promoteError);
            // Continue despite error
          } else {
            console.log('User promoted to admin successfully:', promoteResult);
          }
        } catch (adminError) {
          console.error('Error in admin promotion RPC call:', adminError);
          // Continue despite error
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
   * Special function to get user data for analytics purposes
   * Returns data even with RLS restrictions
   */
  async getDashboardUsers() {
    try {
      console.log("Fetching dashboard users and admins...");
      
      // Try using the new RPC function we created - it returns a single array with role
      const { data: usersData, error: rpcError } = await supabase.rpc('get_all_users_and_admins');
      
      // More detailed checks for the returned result
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
        
        // If it's not an array but data exists, try converting to array
        const dataArray = usersData ? [usersData] : [];
        
        if (dataArray.length > 0) {
          console.log("Converted data to array:", dataArray);
          
          // Separate regular users and admins by role field
          const admins = dataArray.filter((user: any) => user.role === 'admin');
          const regularUsers = dataArray.filter((user: any) => user.role !== 'admin');
          
          console.log(`Converted data has ${regularUsers.length} users and ${admins.length} admins`);
          
          return { users: regularUsers, admins };
        }
        
        return await this.fallbackGetDashboardUsers();
      }
      
      // Separate regular users and admins by role field
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
  
      // Attempt to get all users
      const { data: allUsersData, error: allUsersError } = await supabase
        .from('users')
        .select('*')
        .order('created_at', { ascending: false });
  
      if (allUsersError) {
        console.error('Error fetching all users:', allUsersError);
        return { users: [], admins: [] };
      }
      
      // Attempt to get all admins to filter users
      const { data: adminsData, error: adminsError } = await supabase
        .from('admins')
        .select('user_id, department');
      
      if (adminsError) {
        console.error('Error fetching admins:', adminsError);
        // Even if there's an error, continue with the users we already have
      }
      
      // Create a key of user IDs that are admins
      const adminUserIds = new Set(adminsData?.map(admin => admin.user_id) || []);
      
      // Filter users and add role field to each user
      const regularUsers = [];
      const admins = [];
      
      for (const user of allUsersData || []) {
        // Check if the user is an admin
        if (adminUserIds.has(user.id)) {
          // Find the corresponding admin details
          const adminInfo = adminsData?.find(admin => admin.user_id === user.id);
          
          // Add the role field and other relevant fields
          admins.push({
            ...user,
            role: 'admin',
            department: adminInfo?.department || null
          });
        } else {
          // This is a regular user
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