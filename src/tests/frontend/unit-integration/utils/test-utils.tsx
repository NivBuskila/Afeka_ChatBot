import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { vi } from 'vitest'

// Mock Supabase client
const mockSupabaseClient = {
  auth: {
    getSession: vi.fn().mockResolvedValue({ data: { session: null }, error: null }),
    signInWithPassword: vi.fn(),
    signUp: vi.fn(),
    signOut: vi.fn(),
    onAuthStateChange: vi.fn().mockReturnValue({ data: { subscription: { unsubscribe: vi.fn() } } })
  },
  from: vi.fn().mockReturnValue({
    select: vi.fn().mockReturnValue({
      eq: vi.fn().mockReturnValue({
        single: vi.fn().mockResolvedValue({ data: null, error: null })
      })
    })
  })
}

// Create a custom render function with all providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialEntries?: string[]
  user?: any
  theme?: 'light' | 'dark'
  language?: 'en' | 'he'
}

// All the providers wrapper
const AllTheProviders: React.FC<{
  children: React.ReactNode
  initialEntries?: string[]
  user?: any
  theme?: 'light' | 'dark'
  language?: 'en' | 'he'
}> = ({ children, theme = 'light', language = 'en' }) => {
  return (
    <div data-theme={theme} data-language={language}>
      {children}
    </div>
  )
}

const customRender = (
  ui: ReactElement,
  options: CustomRenderOptions = {}
) => {
  const { initialEntries, user, theme, language, ...renderOptions } = options

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <AllTheProviders
      user={user}
      theme={theme}
      language={language}
    >
      {children}
    </AllTheProviders>
  )

  return render(ui, { wrapper: Wrapper, ...renderOptions })
}

// Export utilities
export * from '@testing-library/react'
export { customRender as render }

// Helper function to create authenticated render
export const renderWithAuth = (
  ui: ReactElement,
  options: CustomRenderOptions & { isAdmin?: boolean } = {}
) => {
  const { isAdmin = false, ...renderOptions } = options
  
  const mockUser = {
    id: isAdmin ? 'admin-user-id' : 'regular-user-id',
    email: isAdmin ? 'admin@test.com' : 'user@test.com',
    role: isAdmin ? 'admin' : 'user'
  }

  return customRender(ui, {
    user: mockUser,
    ...renderOptions
  })
}

// Export the mock Supabase client for use in tests
export { mockSupabaseClient }
