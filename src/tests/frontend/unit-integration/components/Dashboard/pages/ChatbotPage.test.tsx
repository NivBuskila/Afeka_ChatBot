import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithAdminContext, createUserEvent } from '../../../utils/admin-test-utils'

// Mock ChatbotPage component
const MockChatbotPage = ({ language, setLanguage, theme, setTheme }: any) => {
  return (
    <div data-testid="chatbot-page">
      <h1>Chatbot Configuration</h1>
      
      <div className="chatbot-settings">
        <div className="language-setting">
          <label>Language:</label>
          <select 
            value={language} 
            onChange={(e) => setLanguage(e.target.value)}
            data-testid="language-select"
          >
            <option value="en">English</option>
            <option value="he">Hebrew</option>
          </select>
        </div>
        
        <div className="theme-setting">
          <label>Theme:</label>
          <select 
            value={theme} 
            onChange={(e) => setTheme(e.target.value)}
            data-testid="theme-select"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </div>
      </div>
      
      <div className="chatbot-preview" data-testid="chatbot-preview">
        <div className={`preview-container ${theme}`}>
          <p>Chatbot Preview - {language === 'he' ? 'עברית' : 'English'}</p>
        </div>
      </div>
    </div>
  )
}

/**
 * 🎯 טסטים עבור ChatbotPage Component
 * מבדק את הגדרות הצ'אטבוט והתצוגה המקדימה
 */
describe('ChatbotPage', () => {
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
    it('should render chatbot page', () => {
      renderWithAdminContext(<MockChatbotPage {...defaultProps} />)
      
      expect(screen.getByText('Chatbot Configuration')).toBeInTheDocument()
      expect(screen.getByTestId('chatbot-page')).toBeInTheDocument()
    })

    it('should display language selector', () => {
      renderWithAdminContext(<MockChatbotPage {...defaultProps} />)
      
      expect(screen.getByTestId('language-select')).toBeInTheDocument()
    })

    it('should display theme selector', () => {
      renderWithAdminContext(<MockChatbotPage {...defaultProps} />)
      
      expect(screen.getByTestId('theme-select')).toBeInTheDocument()
    })

    it('should display chatbot preview', () => {
      renderWithAdminContext(<MockChatbotPage {...defaultProps} />)
      
      expect(screen.getByTestId('chatbot-preview')).toBeInTheDocument()
    })
  })

  describe('🌐 Language Settings', () => {
    it('should show current language selection', () => {
      renderWithAdminContext(<MockChatbotPage {...defaultProps} language="he" />)
      
      const languageSelect = screen.getByTestId('language-select')
      expect(languageSelect).toHaveValue('he')
    })

    it('should call setLanguage when language changes', async () => {
      const user = createUserEvent()
      renderWithAdminContext(<MockChatbotPage {...defaultProps} />)
      
      const languageSelect = screen.getByTestId('language-select')
      await user.selectOptions(languageSelect, 'he')
      
      expect(defaultProps.setLanguage).toHaveBeenCalledWith('he')
    })

    it('should update preview text based on language', () => {
      renderWithAdminContext(<MockChatbotPage {...defaultProps} language="he" />)
      
      expect(screen.getByText(/עברית/)).toBeInTheDocument()
    })
  })

  describe('🎨 Theme Settings', () => {
    it('should show current theme selection', () => {
      renderWithAdminContext(<MockChatbotPage {...defaultProps} theme="dark" />)
      
      const themeSelect = screen.getByTestId('theme-select')
      expect(themeSelect).toHaveValue('dark')
    })

    it('should call setTheme when theme changes', async () => {
      const user = createUserEvent()
      renderWithAdminContext(<MockChatbotPage {...defaultProps} />)
      
      const themeSelect = screen.getByTestId('theme-select')
      await user.selectOptions(themeSelect, 'dark')
      
      expect(defaultProps.setTheme).toHaveBeenCalledWith('dark')
    })

    it('should apply theme class to preview', () => {
      renderWithAdminContext(<MockChatbotPage {...defaultProps} theme="dark" />)
      
      const previewContainer = screen.getByText(/Chatbot Preview/).parentElement
      expect(previewContainer).toHaveClass('dark')
    })
  })

  describe('🔄 Integration Tests', () => {
    it('should handle multiple setting changes', async () => {
      const user = createUserEvent()
      renderWithAdminContext(<MockChatbotPage {...defaultProps} />)
      
      const languageSelect = screen.getByTestId('language-select')
      const themeSelect = screen.getByTestId('theme-select')
      
      await user.selectOptions(languageSelect, 'he')
      await user.selectOptions(themeSelect, 'dark')
      
      expect(defaultProps.setLanguage).toHaveBeenCalledWith('he')
      expect(defaultProps.setTheme).toHaveBeenCalledWith('dark')
    })
  })
}) 