import { supabase, Database } from '../config/supabase';
import { userService } from './userService';

export interface DashboardAnalytics {
  totalDocuments: number;
  totalUsers: number;
  totalAdmins: number;
  recentDocuments: Database['public']['Tables']['documents']['Row'][];
  recentUsers: Database['public']['Tables']['users']['Row'][];
  recentAdmins: any[];
}

// Helper function to count rows in a table
async function getTableCount(tableName: string): Promise<number> {
  try {
    // Try using count_rows function to bypass RLS limitations
    const { data, error } = await supabase.rpc('count_rows', {
      table_name: tableName
    });
    
    if (error) {
      console.error(`Error using count_rows for ${tableName}:`, error);
      // If failed, try regular method
      return fallbackGetTableCount(tableName);
    }
    
    return data || 0;
  } catch (error) {
    console.error(`Error in getTableCount with RPC for ${tableName}:`, error);
    // If failed, try regular method
    return fallbackGetTableCount(tableName);
  }
}

// Backup function to count rows using regular method
async function fallbackGetTableCount(tableName: string): Promise<number> {
  const { count, error } = await supabase
    .from(tableName)
    .select('*', { count: 'exact', head: true });
    
  if (error) {
    console.error(`Error counting ${tableName} with fallback:`, error);
    return 0;
  }
  
  return count || 0;
}

export const analyticsService = {
  async getOverallAnalytics(days: number = 30) {
    const { data, error } = await supabase.rpc('get_overall_analytics', {
      days
    });

    if (error) throw error;
    return data;
  },

  async getDashboardAnalytics() {
    try {
      // Use the new function to get users and admins
      const { users: regularUsers, admins: recentAdmins } = await userService.getDashboardUsers();
      
      // Get recent documents
      const { data: recentDocuments, error: docsError } = await supabase
        .from('documents')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(5);
        
      if (docsError) {
        console.error('Error fetching documents:', docsError);
      }
      
      // Count rows in each table (important to sync numbers from service)
      let totalDocuments = await getTableCount('documents');
      let totalUsers = regularUsers.length + recentAdmins.length; // Total users
      let totalAdmins = recentAdmins.length; // Admin count
      
      // If document count failed, try counting from array
      if (totalDocuments === 0 && recentDocuments) {
        totalDocuments = recentDocuments.length;
      }

      return {
        totalDocuments,
        totalUsers,
        totalAdmins,
        recentDocuments: recentDocuments || [],
        recentUsers: regularUsers || [], // Pass all regular users
        recentAdmins: recentAdmins || [] // Pass all admins
      };
    } catch (error) {
      console.error('Error in getDashboardAnalytics:', error);
      return {
        totalDocuments: 0,
        totalUsers: 0,
        totalAdmins: 0,
        recentDocuments: [],
        recentUsers: [],
        recentAdmins: []
      };
    }
  },

  async getDailyAnalytics(days: number = 30) {
    const { data, error } = await supabase.rpc('get_daily_analytics', {
      days
    });

    if (error) throw error;
    return data;
  },

  async getPopularDocuments(days: number = 30, limit: number = 10) {
    const { data, error } = await supabase.rpc('get_popular_documents', {
      days,
      limit_count: limit
    });

    if (error) throw error;
    return data;
  },

  async getActiveUsers(days: number = 30, limit: number = 10, includeAdmins: boolean = false) {
    try {
      const { data: allUsers, error: usersError } = await supabase
        .from('users')
        .select('*')
        .order('created_at', { ascending: false });
      
      if (usersError) {
        console.error('Error fetching users in getActiveUsers:', usersError);
        return [];
      }
      
      if (!includeAdmins) {
        const { data: admins, error: adminsError } = await supabase
          .from('admins')
          .select('user_id');
          
        if (adminsError) {
          console.error('Error fetching admin IDs in getActiveUsers:', adminsError);
          return allUsers ? allUsers.slice(0, limit) : [];
        }
        
        const adminIds = admins ? admins.map(a => a.user_id) : [];
        
        const filteredUsers = allUsers ? allUsers.filter(user => 
          !adminIds.includes(user.id)
        ) : [];
        
        return filteredUsers.slice(0, limit);
      }
      
      return allUsers ? allUsers.slice(0, limit) : [];
    } catch (error) {
      console.error('Error in getActiveUsers:', error);
      return [];
    }
  },

  async getActiveAdmins(days: number = 30, limit: number = 10) {
    try {
      const { data, error } = await supabase
        .from('admins')
        .select('*, users!inner(*)')
        .order('created_at', { ascending: false })
        .limit(limit);
      
      if (error) {
        console.error('Error fetching admins in getActiveAdmins:', error);
        return [];
      }
      
      return data ? data.map(admin => {
        const userInfo = admin.users;
        return {
          id: admin.id,
          user_id: admin.user_id,
          email: userInfo ? userInfo.email : 'unknown',
          department: admin.department || '',
          created_at: admin.created_at
        };
      }) : [];
    } catch (error) {
      console.error('Error in getActiveAdmins:', error);
      return [];
    }
  },

  async getDocumentTypeDistribution() {
    const { data, error } = await supabase.rpc('get_document_type_distribution');

    if (error) throw error;
    return data;
  },

  async getUserEngagementMetrics(days: number = 30) {
    const { data, error } = await supabase.rpc('get_user_engagement_metrics', {
      days
    });

    if (error) throw error;
    return data;
  },

  async getRetentionMetrics(cohortDays: number = 30, retentionDays: number = 7) {
    const { data, error } = await supabase.rpc('get_retention_metrics', {
      cohort_days: cohortDays,
      retention_days: retentionDays
    });

    if (error) throw error;
    return data;
  },

  async getDocumentDetails(documentId: number) {
    const { data, error } = await supabase.rpc('get_document_details', {
      document_id: documentId
    });

    if (error) throw error;
    return data;
  },

  async getDocumentAccessHistory(documentId: number, limit: number = 10) {
    const { data, error } = await supabase.rpc('get_document_access_history', {
      document_id: documentId,
      limit_count: limit
    });

    if (error) throw error;
    return data;
  },

  async getDocumentUsageTrends(documentId: number, days: number = 30) {
    const { data, error } = await supabase.rpc('get_document_usage_trends', {
      document_id: documentId,
      days
    });

    if (error) throw error;
    return data;
  },

  async getUserProfile(userId: string) {
    const { data, error } = await supabase.rpc('get_user_profile', {
      user_id: userId
    });

    if (error) throw error;
    return data;
  },

  async getUserActivitySummary(userId: string, days: number = 30) {
    const { data, error } = await supabase.rpc('get_user_activity_summary', {
      user_id: userId,
      days
    });

    if (error) throw error;
    return data;
  },

  async getUserSecurityStatus(userId: string) {
    const { data, error } = await supabase.rpc('get_user_security_status', {
      user_id: userId
    });

    if (error) throw error;
    return data;
  },

  async getUserSecurityEvents(userId: string, limit: number = 10) {
    const { data, error } = await supabase.rpc('get_user_security_events', {
      user_id: userId,
      limit_count: limit
    });

    if (error) throw error;
    return data;
  }
}; 