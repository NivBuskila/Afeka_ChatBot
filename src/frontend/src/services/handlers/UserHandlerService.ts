import { supabase } from '../../config/supabase';

export interface UserHandlerCallbacks {
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
  onLoadingChange: (loading: boolean) => void;
  onModalClose: (modalType: 'deleteUser') => void;
  onSelectedUserChange: (user: any | null) => void;
  onAnalyticsRefresh: () => Promise<void>;
}

export class UserHandlerService {
  constructor(private callbacks: UserHandlerCallbacks) {}

  /**
   * Initiates user deletion by setting selected user and showing modal
   */
  async initiateDeleteUser(user: any): Promise<void> {
    this.callbacks.onSelectedUserChange(user);
    this.callbacks.onModalClose = (modalType) => {
      if (modalType === 'deleteUser') {
        // This will be handled by the modal component
      }
    };
  }

  /**
   * Confirms and executes user deletion
   */
  async confirmDeleteUser(selectedUser: any): Promise<void> {
    if (!selectedUser) return;

    try {
      this.callbacks.onLoadingChange(true);

      const { error } = await supabase
        .from('users')
        .delete()
        .eq('id', selectedUser.id);

      if (error) {
        console.error('Error deleting user:', error);
        this.callbacks.onError(`שגיאה במחיקת המשתמש: ${error.message}`);
        return;
      }

      this.callbacks.onModalClose('deleteUser');
      this.callbacks.onSelectedUserChange(null);
      this.callbacks.onSuccess('המשתמש נמחק בהצלחה');

      // Refresh analytics to update user lists
      await this.callbacks.onAnalyticsRefresh();
    } catch (error) {
      console.error('Error deleting user:', error);
      this.callbacks.onError('אירעה שגיאה במחיקת המשתמש');
    } finally {
      this.callbacks.onLoadingChange(false);
    }
  }

  /**
   * Validates user permissions for admin operations
   */
  async validateUserPermissions(userId: string): Promise<boolean> {
    try {
      const { data: adminData, error } = await supabase
        .from('admins')
        .select('id')
        .eq('user_id', userId)
        .single();

      if (error) {
        console.error('Error checking admin permissions:', error);
        return false;
      }

      return !!adminData;
    } catch (error) {
      console.error('Error validating user permissions:', error);
      return false;
    }
  }

  /**
   * Gets user role information
   */
  async getUserRole(userId: string): Promise<'admin' | 'user' | null> {
    try {
      const { data: adminData } = await supabase
        .from('admins')
        .select('id')
        .eq('user_id', userId)
        .single();

      return adminData ? 'admin' : 'user';
    } catch (error) {
      console.error('Error getting user role:', error);
      return null;
    }
  }

  /**
   * Creates a new user record if needed (for authentication flow)
   */
  async createUserIfNeeded(authUser: any): Promise<boolean> {
    try {
      // Check if user already exists
      const { data: existingUser } = await supabase
        .from('users')
        .select('id')
        .eq('id', authUser.id)
        .single();

      if (existingUser) {
        return true; // User already exists
      }

      // Create new user
      const { error: insertError } = await supabase.from('users').insert({
        id: authUser.id,
        email: authUser.email || '',
        name: authUser.email?.split('@')[0] || 'User',
        status: 'active',
      });

      if (insertError) {
        console.error('Failed to insert user record:', insertError);
        return false;
      }

      // Check if user should be admin
      if (authUser.user_metadata?.is_admin || authUser.user_metadata?.role === 'admin') {
        await this.createAdminRecord(authUser.id);
      }

      return true;
    } catch (error) {
      console.error('Error creating user record:', error);
      return false;
    }
  }

  /**
   * Private helper methods
   */
  private async createAdminRecord(userId: string): Promise<void> {
    try {
      const { error: adminError } = await supabase
        .from('admins')
        .insert({ user_id: userId });

      if (adminError) {
        console.error('Failed to insert admin record:', adminError);
      }
    } catch (adminError) {
      console.error('Error creating admin record:', adminError);
    }
  }
} 