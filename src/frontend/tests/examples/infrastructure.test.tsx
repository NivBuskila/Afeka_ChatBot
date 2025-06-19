import React from 'react'
import { describe, it, expect } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { render, renderWithAuth } from '../utils/test-utils'
import { server } from '../setup'
import { http, HttpResponse } from 'msw'
import { createMockUser } from '../factories/auth.factory'

// Simple test component
const TestComponent: React.FC = () => {
  const [userData, setUserData] = React.useState(null)
  const [loading, setLoading] = React.useState(false)

  const fetchUserData = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/user/profile')
      const data = await response.json()
      setUserData(data)
    } catch (error) {
      console.error('Failed to fetch user data:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1>Test Infrastructure Demo</h1>
      <button onClick={fetchUserData} data-testid="fetch-user-btn">
        Fetch User Data
      </button>
      {loading && <div data-testid="loading">Loading...</div>}
      {userData && (
        <div data-testid="user-data">
          User: {JSON.stringify(userData)}
        </div>
      )}
    </div>
  )
}

describe('Test Infrastructure Demo', () => {
  it('should render components with test utilities', () => {
    render(<TestComponent />)
    
    expect(screen.getByText('Test Infrastructure Demo')).toBeInTheDocument()
    expect(screen.getByTestId('fetch-user-btn')).toBeInTheDocument()
  })

  it('should mock API calls successfully', async () => {
    const user = userEvent.setup()
    const mockUser = createMockUser({ name: 'Test User', email: 'test@example.com' })

    // Override the default handler for this test
    server.use(
      http.get('/api/user/profile', () => {
        return HttpResponse.json({ data: mockUser })
      })
    )

    render(<TestComponent />)
    
    await user.click(screen.getByTestId('fetch-user-btn'))
    
    await waitFor(() => {
      expect(screen.getByTestId('user-data')).toBeInTheDocument()
    })
    
    expect(screen.getByTestId('user-data')).toHaveTextContent('Test User')
  })

  it('should render with authentication context', () => {
    renderWithAuth(<TestComponent />, { isAdmin: true })
    
    expect(screen.getByText('Test Infrastructure Demo')).toBeInTheDocument()
  })
})
