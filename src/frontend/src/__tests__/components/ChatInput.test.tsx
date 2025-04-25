import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import ChatInput from '../../components/ChatInput';

// Mock the useTranslation hook
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations = {
        'chat.inputPlaceholder': 'Type a message...',
        'chat.messageInput': 'Message input',
        'chat.sendMessage': 'Send message'
      };
      return translations[key] || key;
    }
  })
}));

describe('ChatInput Component', () => {
  const mockSendMessage = vi.fn();
  
  beforeEach(() => {
    // Reset mock before each test
    mockSendMessage.mockClear();
  });
  
  test('renders input and submit button', () => {
    render(<ChatInput onSendMessage={mockSendMessage} isLoading={false} />);
    
    expect(screen.getByPlaceholderText('Type a message...')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });
  
  test('updates message state when typing', () => {
    render(<ChatInput onSendMessage={mockSendMessage} isLoading={false} />);
    
    const input = screen.getByPlaceholderText('Type a message...');
    fireEvent.change(input, { target: { value: 'Test message' } });
    
    expect(input).toHaveValue('Test message');
  });
  
  test('calls onSendMessage when form is submitted', () => {
    render(<ChatInput onSendMessage={mockSendMessage} isLoading={false} />);
    
    const input = screen.getByPlaceholderText('Type a message...');
    const button = screen.getByRole('button');
    
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(button);
    
    expect(mockSendMessage).toHaveBeenCalledWith('Test message');
    expect(input).toHaveValue(''); // Input should be cleared after send
  });
  
  test('does not send empty messages', () => {
    render(<ChatInput onSendMessage={mockSendMessage} isLoading={false} />);
    
    const button = screen.getByRole('button');
    
    fireEvent.click(button);
    
    expect(mockSendMessage).not.toHaveBeenCalled();
  });
  
  test('disables input and button when isLoading is true', () => {
    render(<ChatInput onSendMessage={mockSendMessage} isLoading={true} />);
    
    const input = screen.getByPlaceholderText('Type a message...');
    const button = screen.getByRole('button');
    
    expect(input).toBeDisabled();
    expect(button).toBeDisabled();
  });
  
  test('sends message when Enter key is pressed', () => {
    render(<ChatInput onSendMessage={mockSendMessage} isLoading={false} />);
    
    const input = screen.getByPlaceholderText('Type a message...');
    
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    
    expect(mockSendMessage).toHaveBeenCalledWith('Test message');
  });
  
  test('does not send message when Shift+Enter is pressed', () => {
    render(<ChatInput onSendMessage={mockSendMessage} isLoading={false} />);
    
    const input = screen.getByPlaceholderText('Type a message...');
    
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: true });
    
    expect(mockSendMessage).not.toHaveBeenCalled();
  });
}); 