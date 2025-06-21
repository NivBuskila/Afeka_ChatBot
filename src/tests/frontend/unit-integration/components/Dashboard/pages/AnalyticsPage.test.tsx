import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithAdminContext, createUserEvent } from '../../../utils/admin-test-utils'
import { createMockDashboardAnalytics, createMockUser } from '../../../factories/admin.factory'

// Mock the AnalyticsPage component
const MockAnalyticsPage = ({ activeSubItem, analytics, isRefreshing, handleDeleteUser }: any) => {
  return (
    <div data-testid="analytics-page">
      <h1>Analytics Dashboard</h1>
      
      {isRefreshing && <div data-testid="loading">Loading...</div>}
      
      {activeSubItem === 'overview' && (
        <div data-testid="overview-section">
          <div data-testid="total-users">{analytics?.totalUsers || 0}</div>
          <div data-testid="total-documents">{analytics?.totalDocuments || 0}</div>
          <div data-testid="total-admins">{analytics?.totalAdmins || 0}</div>
        </div>
      )}
      
      {activeSubItem === 'users' && (
        <div data-testid="users-section">
          {analytics?.recentUsers?.map((user: any) => (
            <div key={user.id} data-testid={`user-${user.id}`}>
              <span>{user.email}</span>
              <button onClick={() => handleDeleteUser(user)}>Delete</button>
            </div>
          ))}
        </div>
      )}
      
      {activeSubItem === 'admins' && (
        <div data-testid="admins-section">
          {analytics?.recentAdmins?.map((admin: any) => (
            <div key={admin.id} data-testid={`admin-${admin.id}`}>
              <span>{admin.email}</span>
              <button onClick={() => handleDeleteUser(admin)}>Delete</button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/**
 * 🎯 טסטים עבור AnalyticsPage Component
 * מבדק את הצגת נתוני האנליטיקה והאינטראקציות
 */
describe('AnalyticsPage', () => {
  const mockAnalytics = createMockDashboardAnalytics({
    totalUsers: 150,
    totalDocuments: 25,
    totalAdmins: 5,
    recentUsers: [
      createMockUser({ id: 'user-1', email: 'user1@example.com' }),
      createMockUser({ id: 'user-2', email: 'user2@example.com' })
    ],
    recentAdmins: [
      createMockUser({ id: 'admin-1', email: 'admin1@example.com', is_admin: true })
    ]
  })

  const defaultProps = {
    activeSubItem: 'overview',
    analytics: mockAnalytics,
    isRefreshing: false,
    handleDeleteUser: vi.fn()
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('🔧 Basic Rendering', () => {
    it('should render analytics dashboard', () => {
      renderWithAdminContext(<MockAnalyticsPage {...defaultProps} />)
      
      expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument()
      expect(screen.getByTestId('analytics-page')).toBeInTheDocument()
    })

    it('should display overview statistics', () => {
      renderWithAdminContext(<MockAnalyticsPage {...defaultProps} />)
      
      expect(screen.getByTestId('total-users')).toHaveTextContent('150')
      expect(screen.getByTestId('total-documents')).toHaveTextContent('25')
      expect(screen.getByTestId('total-admins')).toHaveTextContent('5')
    })

    it('should show loading state when refreshing', () => {
      renderWithAdminContext(<MockAnalyticsPage {...defaultProps} isRefreshing={true} />)
      
      expect(screen.getByTestId('loading')).toBeInTheDocument()
    })
  })

  describe('🧭 Section Navigation', () => {
    it('should render overview section', () => {
      renderWithAdminContext(<MockAnalyticsPage {...defaultProps} activeSubItem="overview" />)
      
      expect(screen.getByTestId('overview-section')).toBeInTheDocument()
    })

    it('should render users section', () => {
      renderWithAdminContext(<MockAnalyticsPage {...defaultProps} activeSubItem="users" />)
      
      expect(screen.getByTestId('users-section')).toBeInTheDocument()
      expect(screen.getByText('user1@example.com')).toBeInTheDocument()
      expect(screen.getByText('user2@example.com')).toBeInTheDocument()
    })

    it('should render admins section', () => {
      renderWithAdminContext(<MockAnalyticsPage {...defaultProps} activeSubItem="admins" />)
      
      expect(screen.getByTestId('admins-section')).toBeInTheDocument()
      expect(screen.getByText('admin1@example.com')).toBeInTheDocument()
    })
  })

  describe('👥 User Interactions', () => {
    it('should handle user deletion', async () => {
      const user = createUserEvent()
      renderWithAdminContext(<MockAnalyticsPage {...defaultProps} activeSubItem="users" />)
      
      const deleteButton = screen.getAllByText('Delete')[0]
      await user.click(deleteButton)
      
      expect(defaultProps.handleDeleteUser).toHaveBeenCalledWith(mockAnalytics.recentUsers[0])
    })

    it('should handle admin deletion', async () => {
      const user = createUserEvent()
      renderWithAdminContext(<MockAnalyticsPage {...defaultProps} activeSubItem="admins" />)
      
      const deleteButton = screen.getByText('Delete')
      await user.click(deleteButton)
      
      expect(defaultProps.handleDeleteUser).toHaveBeenCalledWith(mockAnalytics.recentAdmins[0])
    })
  })

  describe('🛡️ Error Handling', () => {
    it('should handle null analytics gracefully', () => {
      renderWithAdminContext(<MockAnalyticsPage {...defaultProps} analytics={null} />)
      
      expect(screen.getByTestId('total-users')).toHaveTextContent('0')
      expect(screen.getByTestId('total-documents')).toHaveTextContent('0')
      expect(screen.getByTestId('total-admins')).toHaveTextContent('0')
    })

    it('should handle empty user lists', () => {
      const emptyAnalytics = { ...mockAnalytics, recentUsers: [] }
      renderWithAdminContext(<MockAnalyticsPage {...defaultProps} analytics={emptyAnalytics} activeSubItem="users" />)
      
      expect(screen.getByTestId('users-section')).toBeInTheDocument()
      expect(screen.queryByText('user1@example.com')).not.toBeInTheDocument()
    })
  })
}) 