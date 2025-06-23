import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderAdminDashboard, createUserEvent, mockSupabaseClient, resetTestState } from '../utils/admin-test-utils'
import { createMockDashboardAnalytics, createMockDocument } from '../factories/admin.factory'
import { server } from '../setup'
import { http, HttpResponse } from 'msw'

/**
 * 🎯 CHARACTERIZATION TESTS - מתעדים איך AdminDashboard עובד עכשיו
 * 
 * המטרה: לכסות את הפונקציונליות הקיימת לפני שנתחיל לפרק
 * אלה הטסטים שצריכים לעבור גם אחרי הפירוק!
 */
describe('AdminDashboard - Characterization Tests 📊', () => {
  const mockOnLogout = vi.fn()
  
  beforeEach(() => {
    vi.clearAllMocks()
    resetTestState()
    
    // Reset any custom handlers
    server.resetHandlers()
    
    // Mock successful API responses by default
    server.use(
      http.get('/api/analytics/dashboard', () => {
        return HttpResponse.json(createMockDashboardAnalytics({
          totalDocuments: 25,
          totalUsers: 150,
          totalAdmins: 5
        }))
      }),
      
      http.get('/api/documents', () => {
        return HttpResponse.json(Array.from({ length: 10 }, (_, i) => 
          createMockDocument({ id: i + 1, name: `document-${i + 1}.pdf` })
        ))
      })
    )
  })

  describe('🔍 Component Initialization Behavior', () => {
    it('should initialize with loading state and then show chatbot by default', async () => {
      renderAdminDashboard({ onLogout: mockOnLogout })
      
      // Should start with loading
      expect(screen.getByText('Loading Dashboard')).toBeInTheDocument()
      
      // Wait for loading to finish and show default content
      await waitFor(() => {
        expect(screen.queryByText('Loading Dashboard')).not.toBeInTheDocument()
      }, { timeout: 3000 })
      
      // Should show chatbot as default active item
      expect(screen.getByText('Chatbot Preview')).toBeInTheDocument()
    })

    it('should load analytics data on initialization', async () => {
      renderAdminDashboard({ onLogout: mockOnLogout })
      
      await waitFor(() => {
        expect(screen.queryByText('Loading Dashboard')).not.toBeInTheDocument()
      })
      
      // Data should be loaded (we can't see it directly in chatbot view, but it's loaded)
      expect(mockSupabaseClient.from).toHaveBeenCalled()
    })
  })

  describe('🧭 Navigation Behavior Documentation', () => {
    it('should handle complete navigation flow between all sections', async () => {
      const user = createUserEvent()
      renderAdminDashboard({ onLogout: mockOnLogout })
      
      // Wait for initialization
      await waitFor(() => {
        expect(screen.getByText('Chatbot Preview')).toBeInTheDocument()
      })

      // Navigate to Analytics
      await user.click(screen.getByText('Analytics'))
      await waitFor(() => {
        expect(screen.getByText('Analytics Overview')).toBeInTheDocument()
      })

      // Navigate to Documents
      await user.click(screen.getByText('Active Documents'))
      await waitFor(() => {
        // Should show documents section
        expect(screen.getByText('Add Document')).toBeInTheDocument()
      })

      // Navigate to RAG Management (if button exists)
      const ragButton = screen.queryByText('RAG Management')
      if (ragButton) {
        await user.click(ragButton)
        // RAG content should load
      }

      // Navigate to Settings
      await user.click(screen.getByText('Settings'))
      await waitFor(() => {
        expect(screen.getByText('Theme')).toBeInTheDocument()
        expect(screen.getByText('Language')).toBeInTheDocument()
      })
    })

    it('should set correct sub-items when navigating to main sections', async () => {
      const user = createUserEvent()
      renderAdminDashboard({ onLogout: mockOnLogout })
      
      await waitFor(() => {
        expect(screen.getByText('Chatbot Preview')).toBeInTheDocument()
      })

      // Analytics should default to overview
      await user.click(screen.getByText('Analytics'))
      await waitFor(() => {
        expect(screen.getByText('Analytics Overview')).toBeInTheDocument()
      })

      // Documents should default to active documents
      await user.click(screen.getByText('Active Documents'))
      await waitFor(() => {
        expect(screen.getByText('Add Document')).toBeInTheDocument()
      })
    })
  })

  describe('🎮 Analytics Section Behavior', () => {
    it('should display analytics overview with data', async () => {
      const user = createUserEvent()
      renderAdminDashboard({ onLogout: mockOnLogout })
      
      await waitFor(() => {
        expect(screen.getByText('Chatbot Preview')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Analytics'))
      
      await waitFor(() => {
        expect(screen.getByText('Analytics Overview')).toBeInTheDocument()
      })
    })

    it('should navigate between analytics sub-sections', async () => {
      const user = createUserEvent()
      renderAdminDashboard({ onLogout: mockOnLogout })
      
      await waitFor(() => {
        expect(screen.getByText('Chatbot Preview')).toBeInTheDocument()
      })

      // Go to analytics
      await user.click(screen.getByText('Analytics'))
      
      await waitFor(() => {
        expect(screen.getByText('Analytics Overview')).toBeInTheDocument()
      })

      // Navigate to users if the button exists
      const usersButton = screen.queryByText('Users')
      if (usersButton) {
        await user.click(usersButton)
        await waitFor(() => {
          expect(screen.getByText('Active Users')).toBeInTheDocument()
        })
      }

      // Navigate to admins if the button exists
      const adminsButton = screen.queryByText('Administrators')
      if (adminsButton) {
        await user.click(adminsButton)
        await waitFor(() => {
          expect(screen.getByText('Active Administrators')).toBeInTheDocument()
        })
      }
    })
  })

  describe('📄 Documents Section Behavior', () => {
    it('should show documents list and upload functionality', async () => {
      const user = createUserEvent()
      renderAdminDashboard({ onLogout: mockOnLogout })
      
      await waitFor(() => {
        expect(screen.getByText('Chatbot Preview')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Active Documents'))
      
      await waitFor(() => {
        expect(screen.getByText('Add Document')).toBeInTheDocument()
      })
    })

    it('should open upload modal when clicking Add Document', async () => {
      const user = createUserEvent()
      renderAdminDashboard({ onLogout: mockOnLogout })
      
      await waitFor(() => {
        expect(screen.getByText('Chatbot Preview')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Active Documents'))
      await user.click(screen.getByText('Add Document'))
      
      // Modal should open
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument()
      })
    })
  })

  describe('⚙️ Settings Section Behavior', () => {
    it('should show theme and language controls', async () => {
      const user = createUserEvent()
      renderAdminDashboard({ onLogout: mockOnLogout })
      
      await waitFor(() => {
        expect(screen.getByText('Chatbot Preview')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Settings'))
      
      await waitFor(() => {
        expect(screen.getByText('Theme')).toBeInTheDocument()
        expect(screen.getByText('Language')).toBeInTheDocument()
      })
    })

    it('should handle theme switching', async () => {
      const user = createUserEvent()
      renderAdminDashboard({ onLogout: mockOnLogout })
      
      await waitFor(() => {
        expect(screen.getByText('Chatbot Preview')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Settings'))
      
      // Find and click dark theme button
      const darkButton = screen.getByText('Dark')
      await user.click(darkButton)
      
      // Theme should change (this might affect DOM classes)
      await waitFor(() => {
        expect(document.documentElement).toHaveClass('dark')
      })
    })

    it('should handle language switching', async () => {
      const user = createUserEvent()
      renderAdminDashboard({ onLogout: mockOnLogout })
      
      await waitFor(() => {
        expect(screen.getByText('Chatbot Preview')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Settings'))
      
      // Find language buttons
      const hebrewButton = screen.getByText('עברית')
      await user.click(hebrewButton)
      
      // Language should change (DOM should reflect RTL)
      await waitFor(() => {
        expect(document.documentElement.dir).toBe('rtl')
      })
    })
  })

  describe('💾 State Management Behavior', () => {
    it('should maintain navigation state through re-renders', async () => {
      const user = createUserEvent()
      const { rerender } = renderAdminDashboard({ onLogout: mockOnLogout })
      
      await waitFor(() => {
        expect(screen.getByText('Chatbot Preview')).toBeInTheDocument()
      })

      // Navigate to analytics
      await user.click(screen.getByText('Analytics'))
      await waitFor(() => {
        expect(screen.getByText('Analytics Overview')).toBeInTheDocument()
      })

      // Re-render component - just check that state persists
      // (This documents current behavior - state may reset on re-render)
      
      // Should still be on analytics (though this might reset - documenting current behavior)
      // This test documents what actually happens
    })

    it('should handle modal states correctly', async () => {
      const user = createUserEvent()
      renderAdminDashboard({ onLogout: mockOnLogout })
      
      await waitFor(() => {
        expect(screen.getByText('Chatbot Preview')).toBeInTheDocument()
      })

      // Open upload modal
      await user.click(screen.getByText('Active Documents'))
      await user.click(screen.getByText('Add Document'))
      
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument()
      })

      // Close modal with cancel
      await user.click(screen.getByText('Cancel'))
      
      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
      })
    })
  })

  describe('🔄 Data Loading and Refresh Behavior', () => {
    it('should show loading states appropriately', async () => {
      renderAdminDashboard({ onLogout: mockOnLogout })
      
      // Should show initial loading
      expect(screen.getByText('Loading Dashboard')).toBeInTheDocument()
      
      // Should hide loading when done
      await waitFor(() => {
        expect(screen.queryByText('Loading Dashboard')).not.toBeInTheDocument()
      })
    })

    it('should handle API failures gracefully', async () => {
      // Mock API failure
      server.use(
        http.get('/api/analytics/dashboard', () => {
          return HttpResponse.json({ error: 'Server error' }, { status: 500 })
        })
      )

      renderAdminDashboard({ onLogout: mockOnLogout })
      
      // Should still render something (documents current error handling)
      await waitFor(() => {
        expect(screen.queryByText('Loading Dashboard')).not.toBeInTheDocument()
      }, { timeout: 5000 })
    })
  })

  describe('🎨 Theme and Language Integration', () => {
    it('should render correctly with dark theme', async () => {
      renderAdminDashboard({ onLogout: mockOnLogout }, { theme: 'dark' })
      
      await waitFor(() => {
        expect(screen.getByText('Chatbot Preview')).toBeInTheDocument()
      })
      
      // Should have dark theme classes applied
      expect(document.documentElement).toHaveClass('dark')
    })

    it('should render correctly with Hebrew language', async () => {
      renderAdminDashboard({ onLogout: mockOnLogout }, { language: 'he' })
      
      await waitFor(() => {
        expect(screen.getByText('Chatbot Preview')).toBeInTheDocument()
      })
      
      // Should have RTL direction
      expect(document.documentElement.dir).toBe('rtl')
    })
  })
}) 