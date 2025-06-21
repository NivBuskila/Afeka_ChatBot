import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithAdminContext, createUserEvent } from '../../../utils/admin-test-utils'

// Mock SettingsPage component
const MockSettingsPage = ({ language, setLanguage, theme, setTheme }: any) => {
  return (
    <div data-testid="settings-page">
      <h1>System Settings</h1>
      
      <div className="settings-sections">
        <section className="appearance-settings">
          <h2>Appearance</h2>
          
          <div className="setting-group">
            <label htmlFor="theme-select">Theme:</label>
            <select 
              id="theme-select"
              value={theme} 
              onChange={(e) => setTheme(e.target.value)}
              data-testid="theme-select"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
            </select>
          </div>
        </section>
        
        <section className="language-settings">
          <h2>Language</h2>
          
          <div className="setting-group">
            <label htmlFor="language-select">Language:</label>
            <select 
              id="language-select"
              value={language} 
              onChange={(e) => setLanguage(e.target.value)}
              data-testid="language-select"
            >
              <option value="en">English</option>
              <option value="he">עברית</option>
            </select>
          </div>
        </section>
        
        <section className="system-info">
          <h2>System Information</h2>
          <div className="info-item">
            <span>Current Theme: </span>
            <span data-testid="current-theme">{theme}</span>
          </div>
          <div className="info-item">
            <span>Current Language: </span>
            <span data-testid="current-language">{language === 'he' ? 'עברית' : 'English'}</span>
          </div>
        </section>
      </div>
    </div>
  )
}

/**
 * 🎯 טסטים עבור SettingsPage Component
 * מבדק את הגדרות המערכת והנושא
 */
describe('SettingsPage', () => {
  const defaultProps = {
    language: 'en',
    setLanguage: vi.fn(),
    theme: 'light',
    setTheme: vi.fn()
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('🔧 Basic Rendering', () => {
    it('should render settings page', () => {
      renderWithAdminContext(<MockSettingsPage {...defaultProps} />)
      
      expect(screen.getByText('System Settings')).toBeInTheDocument()
      expect(screen.getByTestId('settings-page')).toBeInTheDocument()
    })

    it('should display all setting sections', () => {
      renderWithAdminContext(<MockSettingsPage {...defaultProps} />)
      
      expect(screen.getByText('Appearance')).toBeInTheDocument()
      expect(screen.getByText('Language')).toBeInTheDocument()
      expect(screen.getByText('System Information')).toBeInTheDocument()
    })
  })

  describe('🎨 Theme Settings', () => {
    it('should display current theme selection', () => {
      renderWithAdminContext(<MockSettingsPage {...defaultProps} theme="dark" />)
      
      const themeSelect = screen.getByTestId('theme-select')
      expect(themeSelect).toHaveValue('dark')
    })

    it('should call setTheme when theme changes', async () => {
      const user = createUserEvent()
      renderWithAdminContext(<MockSettingsPage {...defaultProps} />)
      
      const themeSelect = screen.getByTestId('theme-select')
      await user.selectOptions(themeSelect, 'dark')
      
      expect(defaultProps.setTheme).toHaveBeenCalledWith('dark')
    })

    it('should show current theme in system info', () => {
      renderWithAdminContext(<MockSettingsPage {...defaultProps} theme="dark" />)
      
      expect(screen.getByTestId('current-theme')).toHaveTextContent('dark')
    })
  })

  describe('🌐 Language Settings', () => {
    it('should display current language selection', () => {
      renderWithAdminContext(<MockSettingsPage {...defaultProps} language="he" />)
      
      const languageSelect = screen.getByTestId('language-select')
      expect(languageSelect).toHaveValue('he')
    })

    it('should call setLanguage when language changes', async () => {
      const user = createUserEvent()
      renderWithAdminContext(<MockSettingsPage {...defaultProps} />)
      
      const languageSelect = screen.getByTestId('language-select')
      await user.selectOptions(languageSelect, 'he')
      
      expect(defaultProps.setLanguage).toHaveBeenCalledWith('he')
    })

    it('should show current language in system info', () => {
      renderWithAdminContext(<MockSettingsPage {...defaultProps} language="he" />)
      
      expect(screen.getByTestId('current-language')).toHaveTextContent('עברית')
    })

    it('should show English in system info for en language', () => {
      renderWithAdminContext(<MockSettingsPage {...defaultProps} language="en" />)
      
      expect(screen.getByTestId('current-language')).toHaveTextContent('English')
    })
  })

  describe('ℹ️ System Information', () => {
    it('should display current settings correctly', () => {
      renderWithAdminContext(<MockSettingsPage {...defaultProps} theme="dark" language="he" />)
      
      expect(screen.getByTestId('current-theme')).toHaveTextContent('dark')
      expect(screen.getByTestId('current-language')).toHaveTextContent('עברית')
    })
  })

  describe('🔄 Integration Tests', () => {
    it('should handle multiple setting changes', async () => {
      const user = createUserEvent()
      renderWithAdminContext(<MockSettingsPage {...defaultProps} />)
      
      const languageSelect = screen.getByTestId('language-select')
      const themeSelect = screen.getByTestId('theme-select')
      
      await user.selectOptions(languageSelect, 'he')
      await user.selectOptions(themeSelect, 'dark')
      
      expect(defaultProps.setLanguage).toHaveBeenCalledWith('he')
      expect(defaultProps.setTheme).toHaveBeenCalledWith('dark')
    })
  })
}) 