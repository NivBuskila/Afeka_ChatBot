import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock Supabase
vi.mock('../../../src/config/supabase', () => ({
  supabase: {
    rpc: vi.fn(),
    from: vi.fn(() => ({
      select: vi.fn(() => ({
        order: vi.fn(() => ({
          limit: vi.fn(() => Promise.resolve({ data: [], error: null }))
        }))
      }))
    }))
  },
}));

// Mock userService
vi.mock('../../../src/services/userService', () => ({
  userService: {
    getDashboardUsers: vi.fn(),
  },
}));

// Import after mocking
import { analyticsService } from '../../../src/services/analyticsService';
import { supabase } from '../../../src/config/supabase';
import { userService } from '../../../src/services/userService';

// Get typed mocks
const mockSupabase = supabase as any;
const mockUserService = userService as any;

describe('analyticsService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getOverallAnalytics', () => {
    it('should fetch overall analytics data successfully', async () => {
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

    it('should use default days parameter', async () => {
      const mockData = { totalDocuments: 50 };

      mockSupabase.rpc.mockResolvedValue({
        data: mockData,
        error: null
      });

      const result = await analyticsService.getOverallAnalytics();

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

      // Mock the count_rows RPC for document count
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

    it('should handle count_rows RPC failure gracefully', async () => {
      const mockUsers = [];
      const mockAdmins = [];
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

      // Mock count_rows RPC failure
      mockSupabase.rpc.mockResolvedValue({
        data: null,
        error: new Error('RPC failed')
      });

      const result = await analyticsService.getDashboardAnalytics();

      // Should still return some data, using document array length as fallback
      expect(result.totalDocuments).toBe(1);
      expect(result.recentDocuments).toEqual(mockDocuments);
    });

    it('should handle complete failure gracefully', async () => {
      mockUserService.getDashboardUsers.mockRejectedValue(new Error('Service error'));

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

  describe('getPopularDocuments', () => {
    it('should fetch popular documents successfully', async () => {
      const mockData = [
        { document_id: 1, title: 'Popular Doc', access_count: 50 },
        { document_id: 2, title: 'Another Doc', access_count: 30 }
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

    it('should use default parameters', async () => {
      const mockData = [];

      mockSupabase.rpc.mockResolvedValue({
        data: mockData,
        error: null
      });

      const result = await analyticsService.getPopularDocuments();

      expect(result).toEqual(mockData);
      expect(mockSupabase.rpc).toHaveBeenCalledWith('get_popular_documents', {
        days: 30,
        limit_count: 10
      });
    });
  });

  describe('getActiveUsers', () => {
    it('should fetch active users successfully', async () => {
      const mockUsers = [
        { id: '1', email: 'user1@test.com', created_at: '2024-01-01' },
        { id: '2', email: 'user2@test.com', created_at: '2024-01-02' }
      ];

      mockSupabase.from.mockReturnValue({
        select: vi.fn().mockReturnValue({
          order: vi.fn().mockResolvedValue({
            data: mockUsers,
            error: null
          })
        })
      });

      const result = await analyticsService.getActiveUsers(30, 10, true);

      expect(result).toEqual(mockUsers);
    });

    it('should filter out admins when includeAdmins is false', async () => {
      const mockUsers = [
        { id: '1', email: 'user1@test.com', created_at: '2024-01-01' },
        { id: '2', email: 'admin@test.com', created_at: '2024-01-02' }
      ];
      const mockAdmins = [{ user_id: '2' }];

      // Mock users query
      let callCount = 0;
      mockSupabase.from.mockImplementation((table) => {
        if (table === 'users') {
          return {
            select: vi.fn().mockReturnValue({
              order: vi.fn().mockResolvedValue({
                data: mockUsers,
                error: null
              })
            })
          };
        } else if (table === 'admins') {
          return {
            select: vi.fn().mockResolvedValue({
              data: mockAdmins,
              error: null
            })
          };
        }
      });

      const result = await analyticsService.getActiveUsers(30, 10, false);

      expect(result).toEqual([mockUsers[0]]); // Only non-admin user
    });
  });
}); 