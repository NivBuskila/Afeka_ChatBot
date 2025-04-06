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
        email: email.trim(),
        password,
      });
      
      if (error) {
        return { user: null, isAdmin: false, error: error.message };
      }
      
      if (!data.user) {
        return { user: null, isAdmin: false, error: 'Could not authenticate user' };
      }
      
      // Check if user is admin
      const isAdmin = await this.checkIsAdmin(data.user.id);
      
      return { user: data.user, isAdmin, error: null };
    } catch (err: any) {
      return { user: null, isAdmin: false, error: err.message || 'Authentication error' };
    }
  },
  
  async checkIsAdmin(userId: string): Promise<boolean> {
    try {
      // Try direct access to admins table
      const { data: adminData, error: adminError } = await supabase
        .from('admins')
        .select('*')
        .eq('user_id', userId)
        .maybeSingle();
      
      if (!adminError && adminData) {
        return true;
      }
      
      // If direct access failed, try using RPC
      try {
        const { data: isAdminResult, error: isAdminError } = await supabase
          .rpc('is_admin', { user_id: userId });
        
        if (!isAdminError && isAdminResult === true) {
          return true;
        }
      } catch (rpcError) {
        console.error('Error calling is_admin RPC:', rpcError);
      }
      
      // Check user metadata as fallback
      const { data: userData } = await supabase.auth.getUser();
      const isAdminFromMetadata = userData?.user?.user_metadata?.role === 'admin';
      
      return !!isAdminFromMetadata;
    } catch (err) {
      console.error('Error checking admin status:', err);
      return false;
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
      return { error: error ? error.message : null };
    } catch (err: any) {
      return { error: err.message || 'Error logging out' };
    }
  }
}; 