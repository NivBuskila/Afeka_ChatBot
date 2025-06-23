import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock Supabase with factory function
vi.mock('../../src/config/supabase', () => ({
  supabase: {
    rpc: vi.fn(),
    from: vi.fn(() => ({
      select: vi.fn(() => ({
        order: vi.fn(() => ({
          limit: vi.fn(() => ({
            then: vi.fn()
          }))
        }))
      }))
    }))
  },
}));

// Mock userService
vi.mock('../../src/services/userService', () => ({
  userService: {
    getDashboardUsers: vi.fn(),
  },
}));

// Import after mocking
import { analyticsService } from '../../src/services/analyticsService';
import { supabase } from '../../src/config/supabase';
import { userService } from '../../src/services/userService';

// Get typed mocks
const mockSupabase = supabase as any;
const mockUserService = userService as any;

describe('analyticsService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getOverallAnalytics', () => {
    it('should fetch overall analytics successfully', async () => {
      const mockData = {
        totalDocuments: 100,
        totalUsers: 50,
        totalSessions: 200,
        averageSessionTime: 15.5
      };

      mockSupabase.rpc.mockResolvedValue({
        data: mockData,
        error: null
      });

      const result = await analyticsService.getOverallAnalytics(30);

      expect(result).toEqual(mockData);
      expect(mockSupabase.rpc).toHaveBeenCalledWith('get_overall_analytics', {
        days: 30
      });
    });

    it('should handle RPC errors', async () => {
      const mockError = new Error('RPC failed');
      mockSupabase.rpc.mockResolvedValue({
        data: null,
        error: mockError
      });

      await expect(analyticsService.getOverallAnalytics()).rejects.toThrow('RPC failed');
    });
  });

  describe('getDashboardAnalytics', () => {
    it('should fetch dashboard analytics successfully', async () => {
      const mockUsers = [
        { id: '1', email: 'user1@test.com', created_at: '2024-01-01' }
      ];
      const mockAdmins = [
        { id: '1', user_id: '2', email: 'admin@test.com', created_at: '2024-01-01' }
      ];
      const mockDocuments = [
        { id: 1, title: 'Doc 1', created_at: '2024-01-01' }
      ];

      mockUserService.getDashboardUsers.mockResolvedValue({
        users: mockUsers,
        admins: mockAdmins
      });

      mockSupabase.from.mockReturnValue({
        select: vi.fn().mockReturnValue({
          order: vi.fn().mockReturnValue({
            limit: vi.fn().mockResolvedValue({
              data: mockDocuments,
              error: null
            })
          })
        })
      });

      // Mock the count_rows RPC
      mockSupabase.rpc.mockResolvedValue({
        data: 1,
        error: null
      });

      const result = await analyticsService.getDashboardAnalytics();

      expect(result).toEqual({
        totalDocuments: 1,
        totalUsers: 2, // 1 user + 1 admin
        totalAdmins: 1,
        recentDocuments: mockDocuments,
        recentUsers: mockUsers,
        recentAdmins: mockAdmins
      });
    });

    it('should handle errors gracefully', async () => {
      mockUserService.getDashboardUsers.mockRejectedValue(new Error('User service error'));

      const result = await analyticsService.getDashboardAnalytics();

      expect(result).toEqual({
        totalDocuments: 0,
        totalUsers: 0,
        totalAdmins: 0,
        recentDocuments: [],
        recentUsers: [],
        recentAdmins: []
      });
    });
  });

  describe('getDailyAnalytics', () => {
    it('should fetch daily analytics successfully', async () => {
      const mockData = [
        { date: '2024-01-01', documents: 5, users: 3 },
        { date: '2024-01-02', documents: 8, users: 4 }
      ];

      mockSupabase.rpc.mockResolvedValue({
        data: mockData,
        error: null
      });

      const result = await analyticsService.getDailyAnalytics(7);

      expect(result).toEqual(mockData);
      expect(mockSupabase.rpc).toHaveBeenCalledWith('get_daily_analytics', {
        days: 7
      });
    });
  });

  describe('getPopularDocuments', () => {
    it('should fetch popular documents successfully', async () => {
      const mockData = [
        { document_id: 1, title: 'Popular Doc', access_count: 50 }
      ];

      mockSupabase.rpc.mockResolvedValue({
        data: mockData,
        error: null
      });

      const result = await analyticsService.getPopularDocuments(30, 5);

      expect(result).toEqual(mockData);
      expect(mockSupabase.rpc).toHaveBeenCalledWith('get_popular_documents', {
        days: 30,
        limit_count: 5
      });
    });
  });
}); 