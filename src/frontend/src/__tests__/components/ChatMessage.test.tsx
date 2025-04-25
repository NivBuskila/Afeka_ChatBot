import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import MessageItem from '../../components/Chat/MessageItem';

describe('MessageItem Component', () => {
  const userMessage = {
    id: '1',
    type: 'user',
    content: 'Hello, this is a test message',
    timestamp: '2023-05-10T10:00:00Z',
  };

  const botMessage = {
    id: '2',
    type: 'bot',
    content: 'Hello! How can I help you today?',
    timestamp: '2023-05-10T10:01:00Z',
  };

  it('renders user message correctly', () => {
    render(<MessageItem message={userMessage} />);
    
    // Check if the message content is displayed
    expect(screen.getByText(userMessage.content)).toBeInTheDocument();
    
    // Check if user icon is present
    const userIcon = screen.getByText((content, element) => {
      return element?.tagName.toLowerCase() === 'svg' && 
             element?.classList.contains('lucide-user');
    });
    expect(userIcon).toBeInTheDocument();
  });

  it('renders bot message correctly', () => {
    render(<MessageItem message={botMessage} />);
    
    // Check if the message content is displayed
    expect(screen.getByText(botMessage.content)).toBeInTheDocument();
    
    // Check if bot icon is present
    const botIcon = screen.getByText((content, element) => {
      return element?.tagName.toLowerCase() === 'svg' && 
             element?.classList.contains('lucide-bot');
    });
    expect(botIcon).toBeInTheDocument();
  });

  it('displays message content correctly', () => {
    render(<MessageItem message={userMessage} />);
    
    const contentElement = screen.getByText(userMessage.content);
    expect(contentElement).toBeInTheDocument();
  });

  it('displays timestamp correctly', () => {
    render(<MessageItem message={userMessage} />);
    
    // Check if timestamp is displayed
    const timestampElement = screen.getByText(userMessage.timestamp);
    expect(timestampElement).toBeInTheDocument();
  });

  it('applies correct styling for user messages', () => {
    const { container } = render(<MessageItem message={userMessage} />);
    
    // Check if flex-row-reverse class is applied for user messages
    const messageContainer = container.querySelector('div');
    expect(messageContainer).toHaveClass('flex-row-reverse');
    
    // Check if user message has the correct background classes
    // We need to select the message bubble div which is the second div in the component
    const messageBubble = container.querySelector('div > div.relative');
    expect(messageBubble).toHaveClass('bg-green-100');
    expect(messageBubble).toHaveClass('dark:bg-green-500/10');
  });

  it('applies correct styling for bot messages', () => {
    const { container } = render(<MessageItem message={botMessage} />);
    
    // Check if bot message has the correct background classes
    const messageBubble = container.querySelector('div > div.relative');
    expect(messageBubble).toHaveClass('bg-gray-200');
    expect(messageBubble).toHaveClass('dark:bg-gray-800');
  });

  it('highlights search terms when provided', () => {
    const messageWithSearchTerm = {
      ...botMessage,
      content: 'This is a highlighted message'
    };
    
    render(<MessageItem message={messageWithSearchTerm} searchTerm="highlighted" />);
    
    // Check if the highlighted term is wrapped in a mark element
    const highlightedText = screen.getByText('highlighted');
    expect(highlightedText.tagName).toBe('MARK');
    expect(highlightedText).toHaveClass('bg-yellow-200');
    expect(highlightedText).toHaveClass('dark:bg-yellow-800');
  });
}); 