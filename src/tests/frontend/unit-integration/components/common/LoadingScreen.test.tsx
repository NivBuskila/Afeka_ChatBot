import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '../../utils/test-utils'
import LoadingScreen from '../../../src/components/LoadingScreen'

// Mock react-i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'loading': 'Loading...',
        'loadingPermissions': 'Please wait...'
      }
      return translations[key] || key
    }
  })
}))

// Mock ThemeContext
const mockThemeContext = {
  theme: 'light' as const,
  toggleTheme: vi.fn()
}

vi.mock('../../../src/contexts/ThemeContext', () => ({
  useTheme: () => mockThemeContext
}))

describe('LoadingScreen Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockThemeContext.theme = 'light'
  })

  describe('Rendering', () => {
    it('should render with default messages', () => {
      render(<LoadingScreen />)
      
      expect(screen.getByText('APEX')).toBeInTheDocument()
      expect(screen.getByText('Loading...')).toBeInTheDocument()
      expect(screen.getByText('Please wait...')).toBeInTheDocument()
    })

    it('should render with custom message', () => {
      render(<LoadingScreen message="Initializing..." />)
      
      expect(screen.getByText('APEX')).toBeInTheDocument()
      expect(screen.getByText('Initializing...')).toBeInTheDocument()
      expect(screen.getByText('Please wait...')).toBeInTheDocument()
    })
  })

  describe('Theme Support', () => {
    it('should render light theme correctly', () => {
      mockThemeContext.theme = 'light'
      
      render(<LoadingScreen />)
      
      const title = screen.getByText('APEX')
      expect(title).toHaveClass('text-green-600')
    })

    it('should render dark theme correctly', () => {
      mockThemeContext.theme = 'dark'
      
      render(<LoadingScreen />)
      
      const title = screen.getByText('APEX')
      expect(title).toHaveClass('text-green-400')
    })
  })

  describe('Accessibility', () => {
    it('should have proper semantic structure', () => {
      render(<LoadingScreen />)
      
      const mainHeading = screen.getByText('APEX')
      expect(mainHeading.tagName).toBe('H1')
      
      const loadingHeading = screen.getByText('Loading...')
      expect(loadingHeading.tagName).toBe('H2')
    })
  })
})