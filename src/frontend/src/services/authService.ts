import { supabase } from '../config/supabase';

export interface AuthResult {
  user: any | null;
  isAdmin: boolean;
  error: string | null;
}

export const authService = {
  async login(email: string, password: string): Promise<AuthResult> {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      
      if (error) {
        if (error.message.includes('Invalid login credentials')) {
          return {
            user: null,
            isAdmin: false,
            error: 'אימייל או סיסמה שגויים'
          };
        }
        
        return {
          user: null,
          isAdmin: false,
          error: error.message
        };
      }
      
      let isAdmin = false;
      
      if (data.user) {
        const userData = data.user;
        isAdmin = 
          userData.user_metadata?.is_admin === true || 
          userData.user_metadata?.role === 'admin';
        
        if (!isAdmin) {
          try {
            const { data: adminData } = await supabase
              .from('admins')
              .select('id')
              .eq('user_id', userData.id)
              .maybeSingle();
            
            isAdmin = !!adminData;
          } catch (adminCheckError) {
            // Admin check failed, defaulting to false
          }
        }
        
        try {
          await supabase
            .from('users')
            .update({ last_sign_in: new Date().toISOString() })
            .eq('id', userData.id);
        } catch (updateError) {
          // Failed to update last sign in time
        }
        
        if (isAdmin) {
          try {
            await this.ensureAdminRecord(userData.id);
          } catch (ensureAdminError) {
            // Failed to ensure admin record
          }
        }
      }

      return {
        user: data.user,
        isAdmin,
        error: null
      };
    } catch (error: any) {
      return {
        user: null,
        isAdmin: false,
        error: error.message || 'שגיאה לא צפויה בתהליך ההתחברות'
      };
    }
  },
  
  async checkIsAdmin(userId: string): Promise<boolean> {
    try {
      // Try using RPC first (more reliable)
      try {
        const { data: isAdminResult, error: isAdminError } = await supabase
          .rpc('is_admin', { user_id: userId });
        
        if (!isAdminError && isAdminResult === true) {
          return true;
        }
      } catch (rpcError) {
        // RPC failed, trying direct table access
      }
      
      // Fallback to direct access with specific select
      const { data: adminData, error: adminError } = await supabase
        .from('admins')
        .select('id')
        .eq('user_id', userId)
        .maybeSingle();
      
      if (!adminError && adminData) {
        return true;
      }
      
      // Check user metadata as final fallback
      const { data: userData } = await supabase.auth.getUser();
      const isAdminFromMetadata = userData?.user?.user_metadata?.role === 'admin';
      
      return !!isAdminFromMetadata;
    } catch (err) {
      return false;
    }
  },
  
  async ensureAdminRecord(userId: string): Promise<void> {
    try {
      const { data: existingRecord } = await supabase
        .from('admins')
        .select('id')
        .eq('user_id', userId)
        .maybeSingle();
        
      if (existingRecord) {
        return;
      }
      
      await supabase.rpc('promote_to_admin', { user_id: userId });
    } catch (error) {
      // RPC failed, trying direct insert
      try {
        const { error: insertError } = await supabase
          .from('admins')
          .insert({ 
            user_id: userId,
            permissions: ['read', 'write']
          });
          
        if (insertError && insertError.code !== '23505') {
          // Handle insert error (23505 = user already exists)
        }
      } catch (directError) {
        // Direct insert also failed
      }
    }
  },
  
  async resetPassword(email: string): Promise<{ error: string | null }> {
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`,
      });
      
      if (error) {
        return { error: error.message };
      }
      
      return { error: null };
    } catch (err: any) {
      return { error: err.message || 'Error sending password reset email' };
    }
  },
  
  async logout(): Promise<{ error: string | null }> {
    try {
      const { error } = await supabase.auth.signOut();
      return { error: error?.message || null };
    } catch (err: any) {
      return { error: err.message || 'Error during logout' };
    }
  },

  async getCurrentUser() {
    const { data, error } = await supabase.auth.getUser();
    if (error) {
      throw error;
    }
    return data.user;
  },

  async isAuthenticated(): Promise<boolean> {
    const { data } = await supabase.auth.getSession();
    return !!data.session;
  },

  async isAdmin(): Promise<boolean> {
    try {
      const { data: userData } = await supabase.auth.getUser();
      if (!userData.user) return false;
      
      const userMeta = userData.user.user_metadata;
      if (userMeta?.is_admin === true || userMeta?.role === 'admin') {
        return true;
      }
      
      // Try RPC first
      try {
        const { data: isAdminResult } = await supabase
          .rpc('is_admin', { user_id: userData.user.id });
        
        if (isAdminResult === true) {
          return true;
        }
      } catch (rpcError) {
        // RPC failed, using direct table access
      }
      
      const { data: adminData } = await supabase
        .from('admins')
        .select('id')
        .eq('user_id', userData.user.id)
        .maybeSingle();
        
      return !!adminData;
    } catch (error) {
      return false;
    }
  }
}; 