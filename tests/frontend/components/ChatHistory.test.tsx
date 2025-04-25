import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import ChatHistory from '../../../src/frontend/components/ChatHistory';

// Mock router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
  }),
}));

describe('ChatHistory Component', () => {
  const mockChatSessions = [
    {
      id: 'session1',
      title: 'First Chat Session',
      lastMessageDate: new Date('2023-05-10T10:00:00'),
      messageCount: 5
    },
    {
      id: 'session2',
      title: 'Second Chat Session',
      lastMessageDate: new Date('2023-05-11T11:00:00'),
      messageCount: 3
    },
    {
      id: 'session3',
      title: 'Third Chat Session',
      lastMessageDate: new Date('2023-05-12T12:00:00'),
      messageCount: 8
    }
  ];

  const mockOnSelectSession = jest.fn();
  const mockOnCreateSession = jest.fn();
  const mockOnDeleteSession = jest.fn();

  beforeEach(() => {
    mockOnSelectSession.mockClear();
    mockOnCreateSession.mockClear();
    mockOnDeleteSession.mockClear();
  });

  it('renders a list of chat sessions', () => {
    render(
      <ChatHistory 
        chatSessions={mockChatSessions}
        currentSessionId="session1"
        onSelectSession={mockOnSelectSession}
        onCreateSession={mockOnCreateSession}
        onDeleteSession={mockOnDeleteSession}
      />
    );
    
    // Check if session titles are displayed
    expect(screen.getByText('First Chat Session')).toBeInTheDocument();
    expect(screen.getByText('Second Chat Session')).toBeInTheDocument();
    expect(screen.getByText('Third Chat Session')).toBeInTheDocument();
  });

  it('highlights the current session', () => {
    render(
      <ChatHistory 
        chatSessions={mockChatSessions}
        currentSessionId="session2"
        onSelectSession={mockOnSelectSession}
        onCreateSession={mockOnCreateSession}
        onDeleteSession={mockOnDeleteSession}
      />
    );
    
    // Check if the current session has the selected class
    const currentSessionElement = screen.getByText('Second Chat Session').closest('div[data-testid="session-item"]');
    expect(currentSessionElement).toHaveClass('selected');
  });

  it('calls onSelectSession when a session is clicked', async () => {
    render(
      <ChatHistory 
        chatSessions={mockChatSessions}
        currentSessionId="session1"
        onSelectSession={mockOnSelectSession}
        onCreateSession={mockOnCreateSession}
        onDeleteSession={mockOnDeleteSession}
      />
    );
    
    // Click on a session
    const sessionElement = screen.getByText('Second Chat Session');
    await userEvent.click(sessionElement);
    
    // Check if onSelectSession was called with the correct session ID
    expect(mockOnSelectSession).toHaveBeenCalledWith('session2');
  });

  it('calls onCreateSession when new chat button is clicked', async () => {
    render(
      <ChatHistory 
        chatSessions={mockChatSessions}
        currentSessionId="session1"
        onSelectSession={mockOnSelectSession}
        onCreateSession={mockOnCreateSession}
        onDeleteSession={mockOnDeleteSession}
      />
    );
    
    // Click on the new chat button
    const newChatButton = screen.getByText(/new chat/i);
    await userEvent.click(newChatButton);
    
    // Check if onCreateSession was called
    expect(mockOnCreateSession).toHaveBeenCalled();
  });

  it('displays delete buttons for each session', () => {
    render(
      <ChatHistory 
        chatSessions={mockChatSessions}
        currentSessionId="session1"
        onSelectSession={mockOnSelectSession}
        onCreateSession={mockOnCreateSession}
        onDeleteSession={mockOnDeleteSession}
      />
    );
    
    // Check if delete buttons are present
    const deleteButtons = screen.getAllByTestId('delete-session-button');
    expect(deleteButtons).toHaveLength(mockChatSessions.length);
  });

  it('calls onDeleteSession when delete button is clicked', async () => {
    render(
      <ChatHistory 
        chatSessions={mockChatSessions}
        currentSessionId="session1"
        onSelectSession={mockOnSelectSession}
        onCreateSession={mockOnCreateSession}
        onDeleteSession={mockOnDeleteSession}
      />
    );
    
    // Click on a delete button
    const deleteButtons = screen.getAllByTestId('delete-session-button');
    await userEvent.click(deleteButtons[1]); // Delete second session
    
    // Check if onDeleteSession was called with the correct session ID
    expect(mockOnDeleteSession).toHaveBeenCalledWith('session2');
  });

  it('shows formatted date for each session', () => {
    render(
      <ChatHistory 
        chatSessions={mockChatSessions}
        currentSessionId="session1"
        onSelectSession={mockOnSelectSession}
        onCreateSession={mockOnCreateSession}
        onDeleteSession={mockOnDeleteSession}
      />
    );
    
    // Check if dates are formatted and displayed
    const dateElements = screen.getAllByTestId('session-date');
    expect(dateElements).toHaveLength(mockChatSessions.length);
    
    // Date format may vary based on implementation, so we check general presence
    expect(dateElements[0]).toHaveTextContent(/may 10|5\/10|10\/5/i);
  });

  it('displays message count for each session', () => {
    render(
      <ChatHistory 
        chatSessions={mockChatSessions}
        currentSessionId="session1"
        onSelectSession={mockOnSelectSession}
        onCreateSession={mockOnCreateSession}
        onDeleteSession={mockOnDeleteSession}
      />
    );
    
    // Check if message counts are displayed
    expect(screen.getByText('5 messages')).toBeInTheDocument();
    expect(screen.getByText('3 messages')).toBeInTheDocument();
    expect(screen.getByText('8 messages')).toBeInTheDocument();
  });

  it('shows a message when no chat sessions exist', () => {
    render(
      <ChatHistory 
        chatSessions={[]}
        currentSessionId=""
        onSelectSession={mockOnSelectSession}
        onCreateSession={mockOnCreateSession}
        onDeleteSession={mockOnDeleteSession}
      />
    );
    
    // Check if empty state message is displayed
    expect(screen.getByText(/no chat history/i)).toBeInTheDocument();
  });

  it('prevents event propagation when clicking delete button', async () => {
    render(
      <ChatHistory 
        chatSessions={mockChatSessions}
        currentSessionId="session1"
        onSelectSession={mockOnSelectSession}
        onCreateSession={mockOnCreateSession}
        onDeleteSession={mockOnDeleteSession}
      />
    );
    
    // Click on a delete button
    const deleteButtons = screen.getAllByTestId('delete-session-button');
    await userEvent.click(deleteButtons[1]); // Delete second session
    
    // Check if onDeleteSession was called but onSelectSession was not
    expect(mockOnDeleteSession).toHaveBeenCalledWith('session2');
    expect(mockOnSelectSession).not.toHaveBeenCalled();
  });
}); 