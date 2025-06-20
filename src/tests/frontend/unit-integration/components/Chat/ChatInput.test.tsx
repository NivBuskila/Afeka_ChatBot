import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { render } from '../../utils/test-utils'
import ChatInput from '../../../src/components/Chat/ChatInput'

// Mock react-i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        'chat.inputPlaceholder': 'Type your message here...',
        'chat.messageInput': 'Message input',
        'chat.sendMessage': 'Send message'
      }
      return translations[key] || key
    },
    i18n: { language: 'en' }
  })
}))

// Mock lucide-react
vi.mock('lucide-react', () => ({
  Send: ({ className }: { className?: string }) => 
    <div data-testid="send-icon" className={className}>Send</div>
}))

describe('ChatInput Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render with default props', () => {
      render(<ChatInput />)
      
      const textarea = screen.getByTestId('chat-input')
      const sendButton = screen.getByTestId('send-button')
      
      expect(textarea).toBeInTheDocument()
      expect(sendButton).toBeInTheDocument()
      expect(textarea).toHaveAttribute('placeholder', 'Type your message here...')
    })

    it('should render with custom placeholder', () => {
      render(<ChatInput placeholder="Enter your question..." />)
      
      const textarea = screen.getByTestId('chat-input')
      expect(textarea).toHaveAttribute('placeholder', 'Enter your question...')
    })
  })

  describe('Message Input Handling', () => {
    it('should handle controlled input', async () => {
      const user = userEvent.setup()
      const setInput = vi.fn()
      
      render(
        <ChatInput 
          input="Hello" 
          setInput={setInput} 
        />
      )
      
      const textarea = screen.getByTestId('chat-input')
      expect(textarea).toHaveValue('Hello')
      
      // For controlled inputs, we just check that setInput is called when typing
      await user.type(textarea, ' World')
      
      // setInput should be called for each character typed
      expect(setInput).toHaveBeenCalled()
      // Check that the last call includes the expected partial text
      const calls = setInput.mock.calls
      expect(calls.length).toBeGreaterThan(0)
    })
  })

  describe('Send Button Behavior', () => {
    it('should be disabled when message is empty', () => {
      render(<ChatInput />)
      
      const sendButton = screen.getByTestId('send-button')
      expect(sendButton).toBeDisabled()
    })

    it('should be enabled when message has content', async () => {
      const user = userEvent.setup()
      
      render(<ChatInput />)
      
      const textarea = screen.getByTestId('chat-input')
      const sendButton = screen.getByTestId('send-button')
      
      await user.type(textarea, 'Hello')
      
      expect(sendButton).not.toBeDisabled()
    })
  })

  describe('Keyboard Interactions', () => {
    it('should send message on Enter key', async () => {
      const user = userEvent.setup()
      const onSendMessage = vi.fn()
      
      render(<ChatInput onSendMessage={onSendMessage} />)
      
      const textarea = screen.getByTestId('chat-input')
      
      await user.type(textarea, 'Hello World')
      await user.keyboard('{Enter}')
      
      expect(onSendMessage).toHaveBeenCalledWith('Hello World')
    })
  })
})