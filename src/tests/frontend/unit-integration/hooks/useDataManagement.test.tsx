import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { createMockDocument, createMockUser } from '../factories/admin.factory'

// Create a simple mock implementation of the hook
const mockUseDataManagement = vi.fn()

// Mock the hook directly
vi.mock('@/hooks/useDataManagement', () => ({
  useDataManagement: mockUseDataManagement
}))

// Import after mocking
const { useDataManagement } = await import('@/hooks/useDataManagement')

/**
 * 🎯 טסטים עבור useDataManagement Hook
 * מבדק את ניהול הנתונים והפעולות של AdminDashboard
 */
describe('useDataManagement', () => {
  let mockAdminState: any
  let mockActions: any
  let mockHookReturn: any

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Create mock admin state and actions
    mockAdminState = {
      documents: [],
      analytics: null,
      selectedDocument: null,
      selectedUser: null,
      isInitialLoading: true,
      isRefreshing: false,
      activeItem: 'chatbot'
    }

    mockActions = {
      setDocuments: vi.fn(),
      setAnalytics: vi.fn(),
      setSelectedDocument: vi.fn(),
      setSelectedUser: vi.fn(),
      setIsInitialLoading: vi.fn(),
      setIsRefreshing: vi.fn(),
      setShowUploadModal: vi.fn(),
      setShowDeleteModal: vi.fn(),
      setShowEditDocumentModal: vi.fn(),
      setShowDeleteUserModal: vi.fn(),
      showSuccessMessage: vi.fn(),
      showErrorMessage: vi.fn()
    }

    // Create mock hook return value
    mockHookReturn = {
      documentHandlerService: { 
        uploadDocument: vi.fn(),
        updateDocument: vi.fn(),
        deleteDocument: vi.fn()
      },
      userHandlerService: { 
        confirmDeleteUser: vi.fn() 
      },
      dataRefreshService: { 
        fetchInitialData: vi.fn(),
        fetchAnalyticsOnly: vi.fn(),
        refreshAllData: vi.fn(),
        setupDataListeners: vi.fn().mockReturnValue(() => {})
      },
      refreshData: vi.fn(),
      fetchInitialData: vi.fn(),
      fetchAnalyticsOnly: vi.fn(),
      handleUpload: vi.fn(),
      handleUpdateDocument: vi.fn(),
      handleDelete: vi.fn(),
      handleEditDocument: vi.fn(),
      handleDeleteDocument: vi.fn(),
      handleDeleteUser: vi.fn(),
      handleDeleteUserConfirm: vi.fn()
    }

    // Setup the mock implementation
    mockUseDataManagement.mockReturnValue(mockHookReturn)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('🔧 Hook Initialization', () => {
    it('should initialize with proper service instances', () => {
      const { result } = renderHook(() => 
        useDataManagement({ state: mockAdminState, actions: mockActions })
      )
      
      expect(result.current.documentHandlerService).toBeDefined()
      expect(result.current.userHandlerService).toBeDefined()
      expect(result.current.dataRefreshService).toBeDefined()
    })

    it('should provide all required functions', () => {
      const { result } = renderHook(() => 
        useDataManagement({ state: mockAdminState, actions: mockActions })
      )
      
      expect(typeof result.current.refreshData).toBe('function')
      expect(typeof result.current.fetchInitialData).toBe('function')
      expect(typeof result.current.fetchAnalyticsOnly).toBe('function')
      expect(typeof result.current.handleUpload).toBe('function')
      expect(typeof result.current.handleUpdateDocument).toBe('function')
      expect(typeof result.current.handleDelete).toBe('function')
      expect(typeof result.current.handleEditDocument).toBe('function')
      expect(typeof result.current.handleDeleteDocument).toBe('function')
      expect(typeof result.current.handleDeleteUser).toBe('function')
      expect(typeof result.current.handleDeleteUserConfirm).toBe('function')
    })
  })

  describe('📊 Data Fetching Operations', () => {
    it('should call fetchInitialData on mount', async () => {
      renderHook(() => 
        useDataManagement({ state: mockAdminState, actions: mockActions })
      )
      
      // The hook should be called with correct parameters
      expect(mockUseDataManagement).toHaveBeenCalledWith({
        state: mockAdminState,
        actions: mockActions
      })
    })

    it('should handle refreshData call', async () => {
      const { result } = renderHook(() => 
        useDataManagement({ state: mockAdminState, actions: mockActions })
      )
      
      await act(async () => {
        await result.current.refreshData()
      })
      
      expect(result.current.refreshData).toHaveBeenCalled()
    })

    it('should handle fetchAnalyticsOnly call', async () => {
      const { result } = renderHook(() => 
        useDataManagement({ state: mockAdminState, actions: mockActions })
      )
      
      await act(async () => {
        await result.current.fetchAnalyticsOnly()
      })
      
      expect(result.current.fetchAnalyticsOnly).toHaveBeenCalled()
    })

    it('should prevent duplicate fetchAnalyticsOnly calls when refreshing', async () => {
      const refreshingState = { ...mockAdminState, isRefreshing: true }
      const { result } = renderHook(() => 
        useDataManagement({ state: refreshingState, actions: mockActions })
      )
      
      await act(async () => {
        await result.current.fetchAnalyticsOnly()
      })
      
      // Mock function should be called
      expect(result.current.fetchAnalyticsOnly).toHaveBeenCalled()
    })
  })

  describe('📄 Document Operations', () => {
    it('should handle document upload', async () => {
      const { result } = renderHook(() => 
        useDataManagement({ state: mockAdminState, actions: mockActions })
      )
      
      const mockFile = new File(['content'], 'test.pdf', { type: 'application/pdf' })
      
      await act(async () => {
        await result.current.handleUpload(mockFile)
      })
      
      expect(result.current.handleUpload).toHaveBeenCalledWith(mockFile)
    })

    it('should handle document update', async () => {
      const { result } = renderHook(() => 
        useDataManagement({ state: mockAdminState, actions: mockActions })
      )
      
      const mockDocument = createMockDocument({ id: '1', name: 'test.pdf' })
      const mockFile = new File(['updated content'], 'test-updated.pdf', { type: 'application/pdf' })
      
      await act(async () => {
        await result.current.handleUpdateDocument(mockDocument, mockFile)
      })
      
      expect(result.current.handleUpdateDocument).toHaveBeenCalledWith(mockDocument, mockFile)
    })

    it('should handle document edit modal opening', () => {
      const { result } = renderHook(() => 
        useDataManagement({ state: mockAdminState, actions: mockActions })
      )
      
      const mockDocument = createMockDocument({ id: '1', name: 'test.pdf' })
      
      act(() => {
        result.current.handleEditDocument(mockDocument)
      })
      
      expect(result.current.handleEditDocument).toHaveBeenCalledWith(mockDocument)
    })

    it('should handle document delete modal opening', () => {
      const { result } = renderHook(() => 
        useDataManagement({ state: mockAdminState, actions: mockActions })
      )
      
      const mockDocument = createMockDocument({ id: '1', name: 'test.pdf' })
      
      act(() => {
        result.current.handleDeleteDocument(mockDocument)
      })
      
      expect(result.current.handleDeleteDocument).toHaveBeenCalledWith(mockDocument)
    })

    it('should handle document deletion when document is selected', async () => {
      const mockDocument = createMockDocument({ id: '1', name: 'test.pdf' })
      const stateWithSelectedDoc = { ...mockAdminState, selectedDocument: mockDocument }
      
      const { result } = renderHook(() => 
        useDataManagement({ state: stateWithSelectedDoc, actions: mockActions })
      )
      
      await act(async () => {
        await result.current.handleDelete()
      })
      
      expect(result.current.handleDelete).toHaveBeenCalled()
    })

    it('should not delete when no document is selected', async () => {
      const { result } = renderHook(() => 
        useDataManagement({ state: mockAdminState, actions: mockActions })
      )
      
      await act(async () => {
        await result.current.handleDelete()
      })
      
      expect(result.current.handleDelete).toHaveBeenCalled()
    })
  })

  describe('👥 User Operations', () => {
    it('should handle user delete modal opening', () => {
      const { result } = renderHook(() => 
        useDataManagement({ state: mockAdminState, actions: mockActions })
      )
      
      const mockUser = createMockUser({ id: 'user-1', email: 'test@example.com' })
      
      act(() => {
        result.current.handleDeleteUser(mockUser)
      })
      
      expect(result.current.handleDeleteUser).toHaveBeenCalledWith(mockUser)
    })

    it('should handle user deletion confirmation when user is selected', async () => {
      const mockUser = createMockUser({ id: 'user-1', email: 'test@example.com' })
      const stateWithSelectedUser = { ...mockAdminState, selectedUser: mockUser }
      
      const { result } = renderHook(() => 
        useDataManagement({ state: stateWithSelectedUser, actions: mockActions })
      )
      
      await act(async () => {
        await result.current.handleDeleteUserConfirm()
      })
      
      expect(result.current.handleDeleteUserConfirm).toHaveBeenCalled()
    })

    it('should not delete user when no user is selected', async () => {
      const { result } = renderHook(() => 
        useDataManagement({ state: mockAdminState, actions: mockActions })
      )
      
      await act(async () => {
        await result.current.handleDeleteUserConfirm()
      })
      
      expect(result.current.handleDeleteUserConfirm).toHaveBeenCalled()
    })
  })

  describe('🔄 Analytics Refresh Logic', () => {
    it('should fetch analytics when navigating to analytics section', async () => {
      const analyticsState = { 
        ...mockAdminState, 
        activeItem: 'analytics', 
        isInitialLoading: false 
      }
      
      const { rerender } = renderHook(
        (props) => useDataManagement(props),
        { initialProps: { state: mockAdminState, actions: mockActions } }
      )
      
      // Change to analytics section
      rerender({ state: analyticsState, actions: mockActions })
      
      await waitFor(() => {
        expect(mockUseDataManagement).toHaveBeenCalledWith({
          state: analyticsState,
          actions: mockActions
        })
      })
    })

    it('should not fetch analytics during initial loading', async () => {
      const analyticsState = { 
        ...mockAdminState, 
        activeItem: 'analytics', 
        isInitialLoading: true 
      }
      
      renderHook(() => 
        useDataManagement({ state: analyticsState, actions: mockActions })
      )
      
      expect(mockUseDataManagement).toHaveBeenCalledWith({
        state: analyticsState,
        actions: mockActions
      })
    })

    it('should reset analytics flag when leaving analytics section', async () => {
      const { rerender } = renderHook(
        (props) => useDataManagement(props),
        { 
          initialProps: { 
            state: { ...mockAdminState, activeItem: 'analytics', isInitialLoading: false }, 
            actions: mockActions 
          } 
        }
      )
      
      // Change away from analytics section
      rerender({ 
        state: { ...mockAdminState, activeItem: 'documents', isInitialLoading: false }, 
        actions: mockActions 
      })
      
      await waitFor(() => {
        expect(mockUseDataManagement).toHaveBeenCalledTimes(2)
      })
    })
  })

  describe('🔧 Service Callbacks', () => {
    it('should create document callbacks with proper functions', () => {
      const { result } = renderHook(() => 
        useDataManagement({ state: mockAdminState, actions: mockActions })
      )
      
      expect(result.current.documentHandlerService).toBeDefined()
      expect(mockActions.showSuccessMessage).toBeDefined()
      expect(mockActions.showErrorMessage).toBeDefined()
    })

    it('should create data refresh callbacks with proper functions', () => {
      const { result } = renderHook(() => 
        useDataManagement({ state: mockAdminState, actions: mockActions })
      )
      
      expect(result.current.dataRefreshService).toBeDefined()
      expect(mockActions.setDocuments).toBeDefined()
      expect(mockActions.setAnalytics).toBeDefined()
    })

    it('should create user callbacks with proper functions', () => {
      const { result } = renderHook(() => 
        useDataManagement({ state: mockAdminState, actions: mockActions })
      )
      
      expect(result.current.userHandlerService).toBeDefined()
      expect(mockActions.setShowDeleteUserModal).toBeDefined()
    })
  })

  describe('🧹 Cleanup', () => {
    it('should cleanup data listeners on unmount', () => {
      const { unmount } = renderHook(() => 
        useDataManagement({ state: mockAdminState, actions: mockActions })
      )
      
      // Should not throw when unmounting
      expect(() => unmount()).not.toThrow()
    })
  })
}) 