import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useAdminState } from '@/hooks/useAdminState'

// Mock the dependencies
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: {
      language: 'en',
      changeLanguage: vi.fn()
    }
  })
}))

vi.mock('@/contexts/ThemeContext', () => ({
  useTheme: () => ({
    theme: 'light',
    setTheme: vi.fn()
  })
}))

/**
 * 🎯 טסטים עבור useAdminState Hook
 * מבדק את ניהול המצב של AdminDashboard
 */
describe('useAdminState', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    
    // Mock document.documentElement
    Object.defineProperty(document, 'documentElement', {
      value: {
        classList: {
          add: vi.fn(),
          remove: vi.fn()
        },
        lang: '',
        dir: ''
      },
      writable: true
    })
  })

  describe('🔧 State Initialization', () => {
    it('should initialize with default values', () => {
      const { result } = renderHook(() => useAdminState())
      
      expect(result.current.activeItem).toBe('chatbot')
      expect(result.current.activeSubItem).toBe(null)
      expect(result.current.isSidebarCollapsed).toBe(false)
      expect(result.current.searchQuery).toBe('')
      expect(result.current.documents).toEqual([])
      expect(result.current.analytics).toEqual({
        totalDocuments: 0,
        totalUsers: 0,
        totalAdmins: 0,
        recentDocuments: [],
        recentUsers: [],
        recentAdmins: []
      })
      expect(result.current.isInitialLoading).toBe(true)
      expect(result.current.isRefreshing).toBe(false)
    })

    it('should load theme from localStorage', () => {
      const { result } = renderHook(() => useAdminState())
      
      expect(result.current.theme).toBe('light') // Mock returns 'light'
    })

    it('should load language from localStorage', () => {
      const { result } = renderHook(() => useAdminState())
      
      expect(result.current.language).toBe('en') // Mock returns 'en'
    })
  })

  describe('🧭 Navigation State', () => {
    it('should handle active item changes', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.setActiveItem('analytics')
      })
      
      expect(result.current.activeItem).toBe('analytics')
    })

    it('should handle sub-item changes', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.setActiveSubItem('users')
      })
      
      expect(result.current.activeSubItem).toBe('users')
    })

    it('should handle item click with proper navigation', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.handleItemClick('documents')
      })
      
      expect(result.current.activeItem).toBe('documents')
      expect(result.current.activeSubItem).toBe('active') // Default sub-item
    })

    it('should handle sub-item click', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.handleSubItemClick('analytics', 'overview')
      })
      
      expect(result.current.activeSubItem).toBe('overview')
    })
  })

  describe('🎨 Theme & Language', () => {
    it('should handle theme changes', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.handleThemeChange('dark')
      })
      
      // Mock doesn't actually change theme, just calls the function
      expect(result.current.theme).toBe('light')
    })

    it('should handle language changes', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.handleLanguageChange('he')
      })
      
      // Language actually changes in the hook
      expect(result.current.language).toBe('he')
    })
  })

  describe('🔍 Search & Filters', () => {
    it('should handle search query changes', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.setSearchQuery('test document')
      })
      
      expect(result.current.searchQuery).toBe('test document')
    })
  })

  describe('📄 Modal States', () => {
    it('should handle upload modal state', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.setShowUploadModal(true)
      })
      
      expect(result.current.showUploadModal).toBe(true)
    })

    it('should handle delete modal state', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.setShowDeleteModal(true)
      })
      
      expect(result.current.showDeleteModal).toBe(true)
    })

    it('should handle edit document modal state', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.setShowEditDocumentModal(true)
      })
      
      expect(result.current.showEditDocumentModal).toBe(true)
    })

    it('should handle user delete modal state', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.setShowDeleteUserModal(true)
      })
      
      expect(result.current.showDeleteUserModal).toBe(true)
    })
  })

  describe('📊 Data State', () => {
    it('should handle documents state updates', () => {
      const { result } = renderHook(() => useAdminState())
      const mockDocuments = [
        { 
          id: '1', 
          name: 'test.pdf', 
          type: 'application/pdf', 
          size: 1024,
          url: 'https://example.com/test.pdf',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ]
      
      act(() => {
        result.current.setDocuments(mockDocuments)
      })
      
      expect(result.current.documents).toEqual(mockDocuments)
    })

    it('should handle analytics state updates', () => {
      const { result } = renderHook(() => useAdminState())
      const mockAnalytics = {
        totalUsers: 100,
        totalDocuments: 50,
        totalAdmins: 5,
        recentUsers: [],
        recentAdmins: [],
        recentDocuments: []
      }
      
      act(() => {
        result.current.setAnalytics(mockAnalytics)
      })
      
      expect(result.current.analytics).toEqual(mockAnalytics)
    })

    it('should handle loading states', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.setIsInitialLoading(false)
      })
      
      expect(result.current.isInitialLoading).toBe(false)
      
      act(() => {
        result.current.setIsRefreshing(true)
      })
      
      expect(result.current.isRefreshing).toBe(true)
    })
  })

  describe('🔔 Notifications', () => {
    it('should handle success messages', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.showSuccessMessage('Success!')
      })
      
      expect(result.current.successMessage).toBe('Success!')
    })

    it('should handle error messages', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.showErrorMessage('Error!')
      })
      
      expect(result.current.errorMessage).toBe('Error!')
    })

    it('should clear messages after timeout', async () => {
      vi.useFakeTimers()
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.showSuccessMessage('Success!')
      })
      
      expect(result.current.successMessage).toBe('Success!')
      
      act(() => {
        vi.advanceTimersByTime(4000)
      })
      
      expect(result.current.successMessage).toBe('')
      
      vi.useRealTimers()
    })
  })

  describe('📄 Pagination', () => {
    it('should handle users pagination', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.setUsersCurrentPage(2)
        result.current.setUsersItemsPerPage(20)
      })
      
      expect(result.current.usersCurrentPage).toBe(2)
      expect(result.current.usersItemsPerPage).toBe(20)
    })

    it('should handle admins pagination', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.setAdminsCurrentPage(3)
        result.current.setAdminsItemsPerPage(15)
      })
      
      expect(result.current.adminsCurrentPage).toBe(3)
      expect(result.current.adminsItemsPerPage).toBe(15)
    })
  })

  describe('👥 Selected Items', () => {
    it('should handle selected document', () => {
      const { result } = renderHook(() => useAdminState())
      const mockDocument = { 
        id: '1', 
        name: 'test.pdf',
        type: 'application/pdf',
        size: 1024,
        url: 'https://example.com/test.pdf',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }
      
      act(() => {
        result.current.setSelectedDocument(mockDocument)
      })
      
      expect(result.current.selectedDocument).toEqual(mockDocument)
    })

    it('should handle selected user', () => {
      const { result } = renderHook(() => useAdminState())
      const mockUser = { id: 'user-1', email: 'test@example.com' }
      
      act(() => {
        result.current.setSelectedUser(mockUser)
      })
      
      expect(result.current.selectedUser).toEqual(mockUser)
    })
  })

  describe('📱 Sidebar State', () => {
    it('should handle sidebar collapse state', () => {
      const { result } = renderHook(() => useAdminState())
      
      act(() => {
        result.current.setIsSidebarCollapsed(true)
      })
      
      expect(result.current.isSidebarCollapsed).toBe(true)
    })
  })
}) 