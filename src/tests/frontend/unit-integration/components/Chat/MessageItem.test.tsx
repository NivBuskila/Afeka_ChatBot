import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { render } from '../../utils/test-utils'
import MessageItem from '../../../src/components/Chat/MessageItem'
// Helper to create test messages
const createMessage = (overrides: any = {}) => ({
  id: 'test-id',
  type: 'user' as const,
  content: 'Test message',
  timestamp: '10:00 AM',
  sessionId: 'test-session',
  ...overrides
})

// Mock react-i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'rag.chunkSource': 'מקור הטקסט (צ\'אנק):',
        'rag.showLess': 'הצג פחות',
        'rag.viewMore': 'הצג עוד'
      }
      return translations[key] || key
    }
  })
}))

// Mock theme hooks
vi.mock('../../../src/hooks/useThemeClasses', () => ({
  useThemeClasses: () => ({
    classes: {
      button: 'theme-button-class',
      input: 'theme-input-class'
    }
  })
}))

// Mock AIResponseRenderer
vi.mock('../../../src/components/common/AIResponseRenderer', () => ({
  default: ({ content, searchTerm, className }: any) => (
    <div data-testid="ai-response-renderer" className={className}>
      {searchTerm ? `${content} [highlighted: ${searchTerm}]` : content}
    </div>
  )
}))

// Mock ThemeButton
vi.mock('../../../src/components/ui/ThemeButton', () => ({
  default: ({ children, onClick, variant, size, className, icon }: any) => (
    <button 
      onClick={onClick} 
      className={`theme-button ${variant} ${size} ${className}`}
      data-testid="theme-button"
    >
      {icon && <span data-testid="button-icon">{icon}</span>}
      {children}
    </button>
  )
}))

describe('MessageItem Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('User Messages', () => {
    it('should render user message correctly', () => {
      const userMessage = createMessage({
        type: 'user',
        content: 'Hello, how are you?',
        timestamp: '10:30 AM'
      })

      render(<MessageItem message={userMessage} />)

      const messageElement = screen.getByTestId('user-message')
      expect(messageElement).toBeInTheDocument()
      expect(screen.getByText('Hello, how are you?')).toBeInTheDocument()
      expect(screen.getByText('10:30 AM')).toBeInTheDocument()
    })

    it('should highlight search terms in user messages', () => {
      const userMessage = createMessage({
        type: 'user',
        content: 'Hello world, this is a test message'
      })

      render(<MessageItem message={userMessage} searchTerm="test" />)

      const highlighted = screen.getByText('test')
      expect(highlighted).toHaveClass('bg-yellow-200')
    })
  })

  describe('Bot Messages', () => {
    it('should render bot message correctly', () => {
      const botMessage = createMessage({
        type: 'bot',
        content: 'This is a bot response',
        timestamp: '10:31 AM'
      })

      render(<MessageItem message={botMessage} />)

      const messageElement = screen.getByTestId('bot-message')
      expect(messageElement).toBeInTheDocument()
      expect(screen.getByTestId('ai-response-renderer')).toBeInTheDocument()
      expect(screen.getByText('10:31 AM')).toBeInTheDocument()
    })

    it('should pass search term to AIResponseRenderer', () => {
      const botMessage = createMessage({
        type: 'bot',
        content: 'Bot response with searchable content'
      })

      render(<MessageItem message={botMessage} searchTerm="searchable" />)

      const aiRenderer = screen.getByTestId('ai-response-renderer')
      expect(aiRenderer).toHaveTextContent('[highlighted: searchable]')
    })
  })

  describe('Chunk Text Feature', () => {
    it('should not show chunk text by default', () => {
      const botMessage = createMessage({
        type: 'bot',
        content: 'Bot response',
        chunkText: 'This is the source chunk text from the document'
      })

      render(<MessageItem message={botMessage} />)

      expect(screen.queryByText('מקור הטקסט (צ\'אנק):')).not.toBeInTheDocument()
    })

    it('should show chunk text when showChunkText is true', () => {
      const botMessage = createMessage({
        type: 'bot',
        content: 'Bot response',
        chunkText: 'This is the source chunk text from the document'
      })

      render(<MessageItem message={botMessage} showChunkText={true} />)

      expect(screen.getByText('מקור הטקסט (צ\'אנק):')).toBeInTheDocument()
      expect(screen.getByText('This is the source chunk text from the document')).toBeInTheDocument()
    })
  })
})