import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import ChatContainer from '../../../src/frontend/components/ChatContainer';

// Mock API calls
jest.mock('../../../src/frontend/services/api', () => ({
  sendMessage: jest.fn().mockImplementation((sessionId, message) => {
    return Promise.resolve({
      id: 'bot-response-id',
      content: `Response to: ${message}`,
      isUser: false,
      timestamp: new Date(),
      references: []
    });
  }),
  createSession: jest.fn().mockImplementation(() => {
    return Promise.resolve({ id: 'new-session-id', title: 'New Chat' });
  }),
  getSessions: jest.fn().mockResolvedValue([
    { id: 'session1', title: 'First Chat', lastMessageDate: new Date(), messageCount: 5 },
    { id: 'session2', title: 'Second Chat', lastMessageDate: new Date(), messageCount: 3 }
  ]),
  getMessages: jest.fn().mockImplementation((sessionId) => {
    return Promise.resolve([
      {
        id: 'msg1',
        content: 'Hello',
        isUser: true,
        timestamp: new Date('2023-05-10T10:00:00'),
        references: []
      },
      {
        id: 'msg2',
        content: 'How can I help you?',
        isUser: false,
        timestamp: new Date('2023-05-10T10:01:00'),
        references: []
      }
    ]);
  }),
  deleteSession: jest.fn().mockResolvedValue(true)
}));

// Mock router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    query: { sessionId: 'session1' }
  }),
  useParams: () => ({ sessionId: 'session1' }),
  usePathname: () => '/chat/session1'
}));

describe('ChatContainer Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders chat history and chat components', async () => {
    render(<ChatContainer />);
    
    // Wait for API calls to resolve
    await waitFor(() => {
      // Check if chat history is displayed
      expect(screen.getByText('First Chat')).toBeInTheDocument();
      expect(screen.getByText('Second Chat')).toBeInTheDocument();
      
      // Check if messages are displayed
      expect(screen.getByText('Hello')).toBeInTheDocument();
      expect(screen.getByText('How can I help you?')).toBeInTheDocument();
    });
  });

  it('sends a message and displays the response', async () => {
    render(<ChatContainer />);
    
    // Wait for initial rendering
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/type a message/i)).toBeInTheDocument();
    });
    
    // Send a message
    const inputElement = screen.getByPlaceholderText(/type a message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    await userEvent.type(inputElement, 'Test message');
    await userEvent.click(sendButton);
    
    // Check if the user message and bot response are displayed
    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument();
      expect(screen.getByText('Response to: Test message')).toBeInTheDocument();
    });
  });

  it('creates a new chat session', async () => {
    render(<ChatContainer />);
    
    // Wait for initial rendering
    await waitFor(() => {
      expect(screen.getByText(/new chat/i)).toBeInTheDocument();
    });
    
    // Click on New Chat button
    const newChatButton = screen.getByText(/new chat/i);
    await userEvent.click(newChatButton);
    
    // Check if API was called to create a new session
    await waitFor(() => {
      expect(require('../../../src/frontend/services/api').createSession).toHaveBeenCalled();
    });
  });

  it('switches between chat sessions', async () => {
    render(<ChatContainer />);
    
    // Wait for initial rendering
    await waitFor(() => {
      expect(screen.getByText('First Chat')).toBeInTheDocument();
      expect(screen.getByText('Second Chat')).toBeInTheDocument();
    });
    
    // Click on second chat session
    const secondChatElement = screen.getByText('Second Chat');
    await userEvent.click(secondChatElement);
    
    // Check if messages for the second session are loaded
    await waitFor(() => {
      expect(require('../../../src/frontend/services/api').getMessages).toHaveBeenCalledWith('session2');
    });
  });

  it('deletes a chat session', async () => {
    render(<ChatContainer />);
    
    // Wait for initial rendering
    await waitFor(() => {
      expect(screen.getAllByTestId('delete-session-button')[0]).toBeInTheDocument();
    });
    
    // Click on delete button for the first session
    const deleteButtons = screen.getAllByTestId('delete-session-button');
    await userEvent.click(deleteButtons[0]);
    
    // Check if API was called to delete the session
    await waitFor(() => {
      expect(require('../../../src/frontend/services/api').deleteSession).toHaveBeenCalledWith('session1');
    });
  });

  it('shows loading state while sending a message', async () => {
    // Mock API with delay
    require('../../../src/frontend/services/api').sendMessage.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({
        id: 'response-id',
        content: 'Delayed response',
        isUser: false,
        timestamp: new Date(),
        references: []
      }), 500))
    );
    
    render(<ChatContainer />);
    
    // Wait for initial rendering
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/type a message/i)).toBeInTheDocument();
    });
    
    // Send a message
    const inputElement = screen.getByPlaceholderText(/type a message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    await userEvent.type(inputElement, 'Test message');
    await userEvent.click(sendButton);
    
    // Check if loading indicator is displayed
    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
    
    // Wait for response to resolve
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    }, { timeout: 1000 });
  });

  it('handles errors gracefully', async () => {
    // Mock API with error
    require('../../../src/frontend/services/api').sendMessage.mockRejectedValueOnce(new Error('API Error'));
    
    render(<ChatContainer />);
    
    // Wait for initial rendering
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/type a message/i)).toBeInTheDocument();
    });
    
    // Send a message
    const inputElement = screen.getByPlaceholderText(/type a message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    await userEvent.type(inputElement, 'Test message');
    await userEvent.click(sendButton);
    
    // Check if error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    });
  });

  it('displays empty state when no messages exist', async () => {
    // Mock empty messages
    require('../../../src/frontend/services/api').getMessages.mockResolvedValueOnce([]);
    
    render(<ChatContainer />);
    
    // Check if empty state is displayed
    await waitFor(() => {
      expect(screen.getByText(/start a conversation/i)).toBeInTheDocument();
    });
  });
}); 