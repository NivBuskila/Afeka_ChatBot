import React, { ReactElement, useState, useEffect } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { vi } from 'vitest'
import userEvent from '@testing-library/user-event'

// Mock react-i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'admin.sidebar.chatbotPreview': 'Chatbot Preview',
        'admin.sidebar.analytics': 'Analytics',
        'admin.sidebar.users': 'Users',
        'admin.sidebar.administrators': 'Administrators',
        'admin.sidebar.activeDocuments': 'Active Documents',
        'admin.sidebar.uploadDocuments': 'Upload Documents',
        'admin.sidebar.ragOverview': 'RAG Overview',
        'admin.sidebar.settings': 'Settings',
        'admin.loading': 'Loading Dashboard',
        'admin.loadingPermissions': 'Initializing admin permissions...',
        'analytics.overview': 'Analytics Overview',
        'analytics.users': 'Active Users',
        'analytics.activeAdmins': 'Active Administrators',
        'analytics.noUsers': 'No users found',
        'analytics.noAdmins': 'No administrators found',
        'documents.add': 'Add Document',
        'documents.confirmDelete': 'Confirm Delete',
        'documents.updateSuccess': 'Document updated successfully',
        'documents.updateError': 'Error updating document',
        'admin.documents.deleteSuccess': 'Document deleted successfully',
        'admin.documents.deleteError': 'Error deleting document',
        'settings.theme': 'Theme',
        'settings.language': 'Language',
        'common.cancel': 'Cancel',
        'common.delete': 'Delete',
        'common.save': 'Save',
        'common.upload': 'Upload',
        'users.confirmDelete': 'Confirm User Deletion',
        'users.deleteWarning': 'This action cannot be undone.',
        'users.deleteConfirmText': 'Are you sure you want to delete the user:'
      }
      return translations[key] || key
    },
    i18n: {
      language: 'en',
      changeLanguage: vi.fn()
    }
  })
}))

// Mock Supabase client for AdminDashboard
const mockSupabaseClient = {
  auth: {
    getSession: vi.fn().mockResolvedValue({
      data: {
        session: {
          user: {
            id: 'admin-user-id',
            email: 'admin@test.com',
            user_metadata: {
              is_admin: true,
              role: 'admin'
            }
          }
        }
      },
      error: null
    }),
    signOut: vi.fn().mockResolvedValue({ error: null })
  },
  from: vi.fn().mockReturnValue({
    select: vi.fn().mockReturnValue({
      eq: vi.fn().mockReturnValue({
        single: vi.fn().mockResolvedValue({ data: null, error: null })
      })
    }),
    insert: vi.fn().mockReturnValue({
      select: vi.fn().mockReturnValue({
        single: vi.fn().mockResolvedValue({ data: {}, error: null })
      })
    }),
    update: vi.fn().mockReturnValue({
      eq: vi.fn().mockReturnValue({
        select: vi.fn().mockReturnValue({
          single: vi.fn().mockResolvedValue({ data: {}, error: null })
        })
      })
    }),
    delete: vi.fn().mockReturnValue({
      eq: vi.fn().mockResolvedValue({ error: null })
    })
  }),
  storage: {
    from: vi.fn().mockReturnValue({
      upload: vi.fn().mockResolvedValue({ data: { path: 'test-path' }, error: null }),
      getPublicUrl: vi.fn().mockReturnValue({ 
        data: { publicUrl: 'https://test.com/file.pdf' } 
      }),
      remove: vi.fn().mockResolvedValue({ error: null })
    })
  }
}

// Mock the supabase module
vi.mock('@/config/supabase', () => ({
  supabase: mockSupabaseClient
}))

// Create dynamic theme and language contexts
let currentTheme = 'light'
let currentLanguage = 'en'

const updateDocumentTheme = (theme: string) => {
  currentTheme = theme
  if (theme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

const updateDocumentLanguage = (language: string) => {
  currentLanguage = language
  if (language === 'he') {
    document.documentElement.dir = 'rtl'
  } else {
    document.documentElement.dir = 'ltr'
  }
}

// Mock the contexts with dynamic functionality
vi.mock('@/contexts/ThemeContext', () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <div data-testid="theme-provider">{children}</div>,
  useTheme: () => ({
    theme: currentTheme,
    setTheme: (theme: string) => updateDocumentTheme(theme)
  })
}))

vi.mock('@/contexts/LanguageContext', () => ({
  LanguageProvider: ({ children }: { children: React.ReactNode }) => <div data-testid="language-provider">{children}</div>,
  useLanguage: () => ({
    language: currentLanguage,
    setLanguage: (language: string) => updateDocumentLanguage(language)
  })
}))

// Mock AdminDashboard component with state simulation
const MockAdminDashboard = ({ onLogout }: { onLogout: () => void }) => {
  const [loading, setLoading] = useState(true)
  const [activeSection, setActiveSection] = useState('chatbot')
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [subSection, setSubSection] = useState('')

  useEffect(() => {
    // Simulate loading completion and data fetching
    const timer = setTimeout(async () => {
      // Simulate API calls during initialization
      mockSupabaseClient.from('analytics').select('*')
      mockSupabaseClient.from('documents').select('*')
      setLoading(false)
    }, 100)
    return () => clearTimeout(timer)
  }, [])

  const handleSectionChange = (section: string) => {
    setActiveSection(section)
    if (section === 'analytics') {
      setSubSection('overview')
    } else {
      setSubSection('')
    }
  }

  const handleThemeChange = () => {
    updateDocumentTheme(currentTheme === 'light' ? 'dark' : 'light')
  }

  const handleLanguageChange = () => {
    updateDocumentLanguage(currentLanguage === 'en' ? 'he' : 'en')
  }

  return (
    <div data-testid="admin-dashboard">
      <button onClick={onLogout}>Logout</button>
      <div>Chatbot Preview</div>
      
      {loading && <div>Loading Dashboard</div>}
      
      <button onClick={() => handleSectionChange('analytics')}>Analytics</button>
      <button onClick={() => handleSectionChange('documents')}>Active Documents</button>
      <button onClick={() => handleSectionChange('settings')}>Settings</button>
      <button onClick={() => setShowUploadModal(true)}>Add Document</button>
      
      {activeSection === 'analytics' && (
        <>
          <div>Analytics Overview</div>
          <button onClick={() => setSubSection('users')}>Users</button>
          <button onClick={() => setSubSection('admins')}>Administrators</button>
          {subSection === 'users' && <div>Active Users</div>}
          {subSection === 'admins' && <div>Active Administrators</div>}
        </>
      )}
      
      {activeSection === 'documents' && (
        <div>
          <div>Active Documents</div>
          <button onClick={() => setShowUploadModal(true)}>Upload Document</button>
          {showUploadModal && (
            <div role="dialog">
              <div>Upload Modal</div>
              <button onClick={() => setShowUploadModal(false)}>Close</button>
              <button onClick={() => setShowUploadModal(false)}>Cancel</button>
            </div>
          )}
        </div>
      )}
      
      {activeSection === 'settings' && (
        <div>
          <div>Theme</div>
          <div>Language</div>
          <button onClick={handleThemeChange}>
            {currentTheme === 'light' ? 'Dark' : 'Light'}
          </button>
          <button onClick={handleLanguageChange}>
            {currentLanguage === 'en' ? 'עברית' : 'English'}
          </button>
        </div>
      )}
    </div>
  )
}

// Export MockAdminDashboard for use in tests
export { MockAdminDashboard }

interface AdminTestWrapperProps {
  children: React.ReactNode
  theme?: 'light' | 'dark'
  language?: 'en' | 'he'
}

const AdminTestWrapper: React.FC<AdminTestWrapperProps> = ({ 
  children, 
  theme = 'light', 
  language = 'en' 
}) => {
  // Initialize theme and language
  useEffect(() => {
    updateDocumentTheme(theme)
    updateDocumentLanguage(language)
  }, [theme, language])

  // Mock localStorage for theme and language
  Object.defineProperty(window, 'localStorage', {
    value: {
      getItem: vi.fn((key: string) => {
        if (key === 'theme') return currentTheme
        if (key === 'language') return currentLanguage
        return null
      }),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn()
    },
    writable: true
  })

  return (
    <div data-testid="theme-provider">
      <div data-testid="language-provider">
        {children}
      </div>
    </div>
  )
}

interface AdminRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  theme?: 'light' | 'dark'
  language?: 'en' | 'he'
}

export const renderAdminDashboard = (
  props: { onLogout: () => void } = { onLogout: vi.fn() },
  options: AdminRenderOptions = {}
) => {
  const { theme, language, ...renderOptions } = options

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <AdminTestWrapper theme={theme} language={language}>
      {children}
    </AdminTestWrapper>
  )

  return render(<MockAdminDashboard {...props} />, { wrapper: Wrapper, ...renderOptions })
}

export const renderWithAdminContext = (
  ui: ReactElement,
  options: AdminRenderOptions = {}
) => {
  const { theme, language, ...renderOptions } = options

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <AdminTestWrapper theme={theme} language={language}>
      {children}
    </AdminTestWrapper>
  )

  return render(ui, { wrapper: Wrapper, ...renderOptions })
}

// Export the mock clients for use in tests
export { mockSupabaseClient }

// Helper function to create common user events
export const createUserEvent = () => {
  return userEvent.setup()
}

// Helper function to wait for async operations
export const waitForAsync = async (callback: () => void | Promise<void>) => {
  const { waitFor } = await import('@testing-library/react')
  await waitFor(callback)
}

// Helper function to reset test state
export const resetTestState = () => {
  currentTheme = 'light'
  currentLanguage = 'en'
  document.documentElement.classList.remove('dark')
  document.documentElement.dir = ''
}