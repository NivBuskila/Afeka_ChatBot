import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import MessageItem from '../../components/Chat/MessageItem';

describe('MessageItem Component', () => {
  const mockUserMessage = {
    id: '1',
    type: 'user',
    content: 'Hello, this is a test message',
    timestamp: '2023-05-10 10:00',
    sessionId: 'test-session'
  };

  const mockBotMessage = {
    id: '2',
    type: 'bot',
    content: 'I am a bot response',
    timestamp: '2023-05-10 10:01',
    sessionId: 'test-session'
  };

  it('renders user message correctly', () => {
    render(<MessageItem message={mockUserMessage} />);
    
    // Check message content
    expect(screen.getByText('Hello, this is a test message')).toBeInTheDocument();
    
    // Check timestamp
    expect(screen.getByText('2023-05-10 10:00')).toBeInTheDocument();
    
    // Check user icon is present
    const userIcon = document.querySelector('svg');
    expect(userIcon).toBeInTheDocument();
  });

  it('renders bot message correctly', () => {
    render(<MessageItem message={mockBotMessage} />);
    
    // Check message content
    expect(screen.getByText('I am a bot response')).toBeInTheDocument();
    
    // Check timestamp
    expect(screen.getByText('2023-05-10 10:01')).toBeInTheDocument();
    
    // Check bot icon is present
    const botIcon = document.querySelector('svg');
    expect(botIcon).toBeInTheDocument();
  });

  it('highlights search term in the message content', () => {
    render(<MessageItem message={mockUserMessage} searchTerm="test" />);
    
    // Check that the mark element exists
    const highlightedText = screen.getByText('test');
    expect(highlightedText.tagName).toBe('MARK');
  });

  it('renders multiple highlights when search term appears multiple times', () => {
    const messageWithRepeatedTerm = {
      ...mockUserMessage,
      content: 'test message with test repeated'
    };
    
    render(<MessageItem message={messageWithRepeatedTerm} searchTerm="test" />);
    
    // Check that multiple mark elements exist
    const highlightedTexts = screen.getAllByText('test');
    expect(highlightedTexts).toHaveLength(2);
    highlightedTexts.forEach(highlight => {
      expect(highlight.tagName).toBe('MARK');
    });
  });

  it('applies correct styling for user message', () => {
    const { container } = render(<MessageItem message={mockUserMessage} />);
    
    // Check for reverse flexbox direction for user messages
    const messageContainer = container.firstChild;
    expect(messageContainer).toHaveClass('flex-row-reverse');
    
    // Check for user-specific background color
    const messageBubble = container.querySelector('.relative');
    expect(messageBubble).toHaveClass('bg-green-100');
  });

  it('applies correct styling for bot message', () => {
    const { container } = render(<MessageItem message={mockBotMessage} />);
    
    // Check that bot messages don't have reverse flexbox
    const messageContainer = container.firstChild;
    expect(messageContainer).not.toHaveClass('flex-row-reverse');
    
    // Check for bot-specific background color
    const messageBubble = container.querySelector('.relative');
    expect(messageBubble).toHaveClass('bg-gray-200');
  });

  it('does not highlight when search term is empty', () => {
    render(<MessageItem message={mockUserMessage} searchTerm="" />);
    
    // Check that no mark elements exist
    const messageContent = screen.getByText('Hello, this is a test message');
    expect(messageContent.tagName).not.toBe('MARK');
  });
}); 