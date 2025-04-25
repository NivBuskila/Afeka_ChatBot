import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import Chat from '../../../src/frontend/components/Chat';

// Mock the ChatMessage component to simplify testing
jest.mock('../../../src/frontend/components/ChatMessage', () => {
  return function MockChatMessage({ content, isUser, timestamp, references }) {
    return (
      <div data-testid="chat-message" data-is-user={isUser}>
        <div data-testid="message-content">{content}</div>
        {references && references.length > 0 && (
          <div data-testid="message-references">
            {references.map((ref, i) => (
              <div key={i} data-testid="reference">{ref.title}</div>
            ))}
          </div>
        )}
      </div>
    );
  };
});

describe('Chat Component', () => {
  const mockSendMessage = jest.fn();
  const mockMessages = [
    {
      id: '1',
      content: 'Hello, how can I help you?',
      isUser: false,
      timestamp: new Date('2023-05-10T10:00:00'),
      references: []
    },
    {
      id: '2',
      content: 'I have a question about React',
      isUser: true,
      timestamp: new Date('2023-05-10T10:01:00'),
      references: []
    },
    {
      id: '3',
      content: 'React is a JavaScript library for building user interfaces',
      isUser: false,
      timestamp: new Date('2023-05-10T10:02:00'),
      references: [{ title: 'React Docs', url: 'https://reactjs.org' }]
    }
  ];

  beforeEach(() => {
    mockSendMessage.mockClear();
  });

  it('renders the chat component with messages', () => {
    render(
      <Chat 
        messages={mockMessages} 
        sendMessage={mockSendMessage}
        isLoading={false}
      />
    );
    
    // Check if all messages are rendered
    const messageElements = screen.getAllByTestId('chat-message');
    expect(messageElements).toHaveLength(3);
    
    // Check message content
    const contentElements = screen.getAllByTestId('message-content');
    expect(contentElements[0]).toHaveTextContent('Hello, how can I help you?');
    expect(contentElements[1]).toHaveTextContent('I have a question about React');
    expect(contentElements[2]).toHaveTextContent('React is a JavaScript library for building user interfaces');
  });

  it('displays user and bot messages with correct styles', () => {
    render(
      <Chat 
        messages={mockMessages} 
        sendMessage={mockSendMessage}
        isLoading={false} 
      />
    );
    
    const messageElements = screen.getAllByTestId('chat-message');
    
    // Check if user/bot messages have correct data attributes
    expect(messageElements[0]).toHaveAttribute('data-is-user', 'false');
    expect(messageElements[1]).toHaveAttribute('data-is-user', 'true');
    expect(messageElements[2]).toHaveAttribute('data-is-user', 'false');
  });

  it('renders message references correctly', () => {
    render(
      <Chat 
        messages={mockMessages} 
        sendMessage={mockSendMessage}
        isLoading={false} 
      />
    );
    
    // Check if reference is displayed for the third message
    const references = screen.getAllByTestId('reference');
    expect(references).toHaveLength(1);
    expect(references[0]).toHaveTextContent('React Docs');
  });

  it('scrolls to bottom when new messages are added', async () => {
    // Mock scrollIntoView
    const scrollIntoViewMock = jest.fn();
    Element.prototype.scrollIntoView = scrollIntoViewMock;
    
    render(
      <Chat 
        messages={mockMessages} 
        sendMessage={mockSendMessage}
        isLoading={false} 
      />
    );
    
    // Check if scrollIntoView was called
    await waitFor(() => {
      expect(scrollIntoViewMock).toHaveBeenCalled();
    });
  });

  it('contains a chat input component', () => {
    render(
      <Chat 
        messages={mockMessages} 
        sendMessage={mockSendMessage}
        isLoading={false} 
      />
    );
    
    // Check if chat input is present
    const inputElement = screen.getByPlaceholderText(/type a message/i);
    expect(inputElement).toBeInTheDocument();
  });

  it('passes the loading state to chat input', () => {
    render(
      <Chat 
        messages={mockMessages} 
        sendMessage={mockSendMessage}
        isLoading={true} 
      />
    );
    
    // Check if input is disabled when loading
    const inputElement = screen.getByPlaceholderText(/type a message/i);
    expect(inputElement).toBeDisabled();
  });

  it('calls sendMessage when a new message is submitted', async () => {
    render(
      <Chat 
        messages={mockMessages} 
        sendMessage={mockSendMessage}
        isLoading={false} 
      />
    );
    
    const inputElement = screen.getByPlaceholderText(/type a message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    // Type and send a message
    await userEvent.type(inputElement, 'New test message');
    await userEvent.click(sendButton);
    
    // Check if sendMessage was called with the correct text
    expect(mockSendMessage).toHaveBeenCalledWith('New test message');
  });

  it('displays empty state when no messages exist', () => {
    render(
      <Chat 
        messages={[]} 
        sendMessage={mockSendMessage}
        isLoading={false} 
      />
    );
    
    // Check if empty state message is displayed
    const emptyStateElement = screen.getByText(/start a conversation/i);
    expect(emptyStateElement).toBeInTheDocument();
  });
}); 