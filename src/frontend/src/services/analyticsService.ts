import { supabase, Database } from '../config/supabase';

export interface DashboardAnalytics {
  totalDocuments: number;
  totalUsers: number;
  recentDocuments: Database['public']['Tables']['documents']['Row'][];
  recentUsers: Database['public']['Tables']['users']['Row'][];
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
      // Using existing data until SQL functions are available
      const [
        { count: totalDocuments },
        { count: totalUsers },
        { data: recentDocuments },
        { data: recentUsers }
      ] = await Promise.all([
        supabase.from('documents').select('*', { count: 'exact', head: true }),
        supabase.from('users').select('*', { count: 'exact', head: true }),
        supabase.from('documents').select('*').order('created_at', { ascending: false }).limit(5),
        supabase.from('users').select('*').order('created_at', { ascending: false }).limit(5)
      ]);

      return {
        totalDocuments: totalDocuments || 0,
        totalUsers: totalUsers || 0,
        recentDocuments: recentDocuments || [],
        recentUsers: recentUsers || []
      };
    } catch (error) {
      console.error('Error in getDashboardAnalytics:', error);
      // Return empty data in case of error
      return {
        totalDocuments: 0,
        totalUsers: 0,
        recentDocuments: [],
        recentUsers: []
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

  async getActiveUsers(days: number = 30, limit: number = 10) {
    const { data, error } = await supabase.rpc('get_active_users', {
      days,
      limit_count: limit
    });

    if (error) throw error;
    return data;
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