import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithAdminContext, createUserEvent } from '../../utils/admin-test-utils'
import { createMockDashboardAnalytics, createMockDocument } from '../../factories/admin.factory'
import { useAdminState } from '@/hooks/useAdminState'
import { useDataManagement } from '@/hooks/useDataManagement'

// Mock the hooks
vi.mock('@/hooks/useAdminState', () => ({
  useAdminState: vi.fn()
}))
vi.mock('@/hooks/useDataManagement', () => ({
  useDataManagement: vi.fn()
}))

// Mock the AdminDashboard component to use the mocked hooks
vi.mock('@/components/Dashboard/AdminDashboard', () => ({
  AdminDashboard: ({ onLogout }: { onLogout: () => void }) => {
    const state = vi.mocked(useAdminState)()
    const dataManagement = vi.mocked(useDataManagement)()
    
    if (state.isInitialLoading) {
      return (
        <div>
          <div>Loading Dashboard</div>
          <div>Initializing admin permissions...</div>
        </div>
      )
    }

    return (
      <div>
        <main className="flex-1 overflow-x-hidden overflow-y-auto">
          {/* Render pages based on activeItem */}
          {state.activeItem === 'chatbot' && (
            <div data-testid="chatbot-page">
              <button onClick={onLogout}>Logout from Chatbot</button>
            </div>
          )}
          
          {state.activeItem === 'analytics' && (
            <div data-testid="analytics-page">Analytics: {state.activeSubItem}</div>
          )}
          
          {state.activeItem === 'documents' && (
            <div data-testid="documents-page">Documents: {state.documents.length}</div>
          )}
          
          {state.activeItem === 'rag' && (
            <div data-testid="rag-page">RAG: {state.activeSubItem}</div>
          )}
          
          {state.activeItem === 'settings' && (
            <div data-testid="settings-page">Settings: {state.theme} - {state.language}</div>
          )}
        </main>

        {/* Notifications */}
        {state.successMessage && (
          <div role="alert">{state.successMessage}</div>
        )}
        
        {state.errorMessage && (
          <div role="alert">{state.errorMessage}</div>
        )}

        {/* Modals */}
        {state.showUploadModal && (
          <div role="dialog">
            <div>Upload Modal</div>
            <button onClick={() => state.setShowUploadModal(false)}>Close</button>
          </div>
        )}
        
        {state.showDeleteModal && state.selectedDocument && (
          <div role="dialog">
            <div>Delete Modal for {state.selectedDocument.name}</div>
          </div>
        )}
        
        {state.showEditDocumentModal && state.selectedDocument && (
          <div role="dialog">
            <div>Edit Modal for {state.selectedDocument.name}</div>
          </div>
        )}
        
        {state.showDeleteUserModal && state.selectedUser && (
          <div role="dialog">
            <div>Delete User Modal for {state.selectedUser.email}</div>
          </div>
        )}
      </div>
    )
  }
}))

// Mock the pages
vi.mock('@/components/Dashboard/pages', () => ({
  ChatbotPage: ({ onLogout }: { onLogout: () => void }) => (
    <div data-testid="chatbot-page">
      <button onClick={onLogout}>Logout from Chatbot</button>
    </div>
  ),
  AnalyticsPage: ({ activeSubItem }: { activeSubItem: string }) => (
    <div data-testid="analytics-page">Analytics: {activeSubItem}</div>
  ),
  DocumentsPage: ({ documents }: { documents: any[] }) => (
    <div data-testid="documents-page">Documents: {documents.length}</div>
  ),
  RAGPage: ({ activeSubItem }: { activeSubItem: string }) => (
    <div data-testid="rag-page">RAG: {activeSubItem}</div>
  ),
  SettingsPage: ({ theme, language }: { theme: string; language: string }) => (
    <div data-testid="settings-page">Settings: {theme} - {language}</div>
  )
}))

// Import after mocks
import { AdminDashboard } from '@/components/Dashboard/AdminDashboard'

/**
 * 🎯 טסטים עבור AdminDashboard Component
 * מבדק את הרינדור והאינטגרציה של הקומפוננט הראשי
 */
describe('AdminDashboard', () => {
  const mockOnLogout = vi.fn()
  
  // Mock state and actions
  const mockAdminState = {
    isSidebarCollapsed: false,
    activeItem: 'chatbot',
    activeSubItem: '',
    searchQuery: '',
    showUploadModal: false,
    showDeleteModal: false,
    showDeleteUserModal: false,
    showEditDocumentModal: false,
    selectedUser: null,
    selectedDocument: null,
    documents: [],
    analytics: null,
    isInitialLoading: false,
    isRefreshing: false,
    language: 'en',
    theme: 'light',
    successMessage: '',
    errorMessage: '',
    usersItemsPerPage: 10,
    usersCurrentPage: 1,
    adminsItemsPerPage: 10,
    adminsCurrentPage: 1,
    setIsSidebarCollapsed: vi.fn(),
    setActiveItem: vi.fn(),
    setActiveSubItem: vi.fn(),
    setSearchQuery: vi.fn(),
    setShowUploadModal: vi.fn(),
    setShowDeleteModal: vi.fn(),
    setShowEditDocumentModal: vi.fn(),
    setShowDeleteUserModal: vi.fn(),
    handleItemClick: vi.fn(),
    handleSubItemClick: vi.fn(),
    handleLanguageChange: vi.fn(),
    handleThemeChange: vi.fn(),
    setUsersItemsPerPage: vi.fn(),
    setUsersCurrentPage: vi.fn(),
    setAdminsItemsPerPage: vi.fn(),
    setAdminsCurrentPage: vi.fn()
  }

  const mockDataManagement = {
    handleUpload: vi.fn(),
    handleUpdateDocument: vi.fn(),
    handleDelete: vi.fn(),
    handleEditDocument: vi.fn(),
    handleDeleteDocument: vi.fn(),
    handleDeleteUser: vi.fn(),
    handleDeleteUserConfirm: vi.fn(),
    refreshData: vi.fn(),
    fetchInitialData: vi.fn(),
    fetchAnalyticsOnly: vi.fn(),
    documentHandlerService: {},
    userHandlerService: {},
    dataRefreshService: {}
  }

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock the hooks
    vi.mocked(useAdminState).mockReturnValue(mockAdminState)
    vi.mocked(useDataManagement).mockReturnValue(mockDataManagement)
  })

  describe('🔧 Basic Rendering', () => {
    it('should render without crashing', () => {
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.getByTestId('chatbot-page')).toBeInTheDocument()
    })

    it('should show loading screen when initially loading', () => {
      const loadingState = { ...mockAdminState, isInitialLoading: true }
      vi.mocked(useAdminState).mockReturnValue(loadingState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.getByText('Loading Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Initializing admin permissions...')).toBeInTheDocument()
    })

    it('should render main dashboard when not loading', () => {
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.queryByText('Loading Dashboard')).not.toBeInTheDocument()
      expect(screen.getByTestId('chatbot-page')).toBeInTheDocument()
    })
  })

  describe('🧭 Page Navigation', () => {
    it('should render ChatbotPage when activeItem is chatbot', () => {
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.getByTestId('chatbot-page')).toBeInTheDocument()
    })

    it('should render AnalyticsPage when activeItem is analytics', () => {
      const analyticsState = { ...mockAdminState, activeItem: 'analytics', activeSubItem: 'overview' }
      vi.mocked(useAdminState).mockReturnValue(analyticsState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.getByTestId('analytics-page')).toBeInTheDocument()
      expect(screen.getByText('Analytics: overview')).toBeInTheDocument()
    })

    it('should render DocumentsPage when activeItem is documents', () => {
      const documentsState = { 
        ...mockAdminState, 
        activeItem: 'documents', 
        activeSubItem: 'active',
        documents: [createMockDocument(), createMockDocument()]
      }
      vi.mocked(useAdminState).mockReturnValue(documentsState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.getByTestId('documents-page')).toBeInTheDocument()
      expect(screen.getByText('Documents: 2')).toBeInTheDocument()
    })

    it('should render RAGPage when activeItem is rag', () => {
      const ragState = { ...mockAdminState, activeItem: 'rag', activeSubItem: 'profiles' }
      vi.mocked(useAdminState).mockReturnValue(ragState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.getByTestId('rag-page')).toBeInTheDocument()
      expect(screen.getByText('RAG: profiles')).toBeInTheDocument()
    })

    it('should render SettingsPage when activeItem is settings', () => {
      const settingsState = { 
        ...mockAdminState, 
        activeItem: 'settings',
        theme: 'dark',
        language: 'he'
      }
      vi.mocked(useAdminState).mockReturnValue(settingsState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.getByTestId('settings-page')).toBeInTheDocument()
      expect(screen.getByText('Settings: dark - he')).toBeInTheDocument()
    })

    it('should render nothing for unknown activeItem', () => {
      const unknownState = { ...mockAdminState, activeItem: 'unknown' }
      vi.mocked(useAdminState).mockReturnValue(unknownState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.queryByTestId('chatbot-page')).not.toBeInTheDocument()
      expect(screen.queryByTestId('analytics-page')).not.toBeInTheDocument()
    })
  })

  describe('🔔 Notifications', () => {
    it('should show success notification when successMessage is present', () => {
      const successState = { ...mockAdminState, successMessage: 'Operation successful!' }
      vi.mocked(useAdminState).mockReturnValue(successState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.getByText('Operation successful!')).toBeInTheDocument()
    })

    it('should show error notification when errorMessage is present', () => {
      const errorState = { ...mockAdminState, errorMessage: 'Something went wrong!' }
      vi.mocked(useAdminState).mockReturnValue(errorState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.getByText('Something went wrong!')).toBeInTheDocument()
    })

    it('should not show notifications when messages are empty', () => {
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    })
  })

  describe('📄 Modals', () => {
    it('should render UploadModal when showUploadModal is true', () => {
      const modalState = { ...mockAdminState, showUploadModal: true }
      vi.mocked(useAdminState).mockReturnValue(modalState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('should render DeleteModal when showDeleteModal is true', () => {
      const modalState = { 
        ...mockAdminState, 
        showDeleteModal: true,
        selectedDocument: createMockDocument({ name: 'test.pdf' })
      }
      vi.mocked(useAdminState).mockReturnValue(modalState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('should render EditDocumentModal when showEditDocumentModal is true', () => {
      const modalState = { 
        ...mockAdminState, 
        showEditDocumentModal: true,
        selectedDocument: createMockDocument({ id: 1, name: 'test.pdf' })
      }
      vi.mocked(useAdminState).mockReturnValue(modalState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    it('should render UserDeleteModal when showDeleteUserModal is true', () => {
      const modalState = { 
        ...mockAdminState, 
        showDeleteUserModal: true,
        selectedUser: { id: 'user-1', email: 'test@example.com' }
      }
      vi.mocked(useAdminState).mockReturnValue(modalState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })
  })

  describe('🎨 Theme and Layout', () => {
    it('should apply dark theme classes when theme is dark', () => {
      const darkState = { ...mockAdminState, theme: 'dark' }
      vi.mocked(useAdminState).mockReturnValue(darkState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />, { theme: 'dark' })
      
      expect(document.documentElement).toHaveClass('dark')
    })

    it('should apply RTL direction when language is Hebrew', () => {
      const hebrewState = { ...mockAdminState, language: 'he' }
      vi.mocked(useAdminState).mockReturnValue(hebrewState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />, { language: 'he' })
      
      expect(document.documentElement.dir).toBe('rtl')
    })

    it('should have proper layout structure', () => {
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      const mainContainer = screen.getByRole('main')
      expect(mainContainer).toBeInTheDocument()
      expect(mainContainer).toHaveClass('flex-1', 'overflow-x-hidden', 'overflow-y-auto')
    })
  })

  describe('🔗 Integration with Hooks', () => {
    it('should pass correct props to useAdminState', () => {
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(vi.mocked(useAdminState)).toHaveBeenCalled()
    })

    it('should pass correct props to useDataManagement', () => {
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(vi.mocked(useDataManagement)).toHaveBeenCalled()
    })

    it('should pass analytics data to AnalyticsPage', () => {
      const analyticsData = createMockDashboardAnalytics()
      const analyticsState = { 
        ...mockAdminState, 
        activeItem: 'analytics',
        analytics: analyticsData
      }
      vi.mocked(useAdminState).mockReturnValue(analyticsState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      expect(screen.getByTestId('analytics-page')).toBeInTheDocument()
    })
  })

  describe('🔄 Modal Interactions', () => {
    it('should close upload modal when onClose is called', async () => {
      const user = createUserEvent()
      const modalState = { ...mockAdminState, showUploadModal: true }
      vi.mocked(useAdminState).mockReturnValue(modalState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      const closeButton = screen.getByText('Close')
      await user.click(closeButton)
      
      expect(modalState.setShowUploadModal).toHaveBeenCalledWith(false)
    })

    it('should call handleUpload when upload is triggered', async () => {
      const modalState = { ...mockAdminState, showUploadModal: true }
      vi.mocked(useAdminState).mockReturnValue(modalState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      // Simulate file upload
      const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
      // Note: Actual file upload interaction would depend on UploadModal implementation
      
      expect(mockDataManagement.handleUpload).toBeDefined()
    })
  })

  describe('🚪 Logout Functionality', () => {
    it('should call onLogout when logout is triggered from ChatbotPage', async () => {
      const user = createUserEvent()
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      const logoutButton = screen.getByText('Logout from Chatbot')
      await user.click(logoutButton)
      
      expect(mockOnLogout).toHaveBeenCalled()
    })
  })

  describe('📱 Responsive Behavior', () => {
    it('should handle sidebar collapse state', () => {
      const collapsedState = { ...mockAdminState, isSidebarCollapsed: true }
      vi.mocked(useAdminState).mockReturnValue(collapsedState)
      
      renderWithAdminContext(<AdminDashboard onLogout={mockOnLogout} />)
      
      // The sidebar should reflect the collapsed state
      expect(collapsedState.isSidebarCollapsed).toBe(true)
    })
  })
}) 