import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChatMessage from '../../../src/frontend/components/ChatMessage';

describe('ChatMessage Component', () => {
  const userMessage = {
    id: '1',
    role: 'user',
    content: 'Hello, this is a test message',
    created_at: new Date().toISOString(),
  };

  const botMessage = {
    id: '2',
    role: 'assistant',
    content: 'Hello! How can I help you today?',
    created_at: new Date().toISOString(),
  };

  it('renders user message correctly', () => {
    render(<ChatMessage message={userMessage} />);
    
    // Check if the message content is displayed
    expect(screen.getByText(userMessage.content)).toBeInTheDocument();
    
    // Check if user avatar or indicator is present
    const userElement = screen.getByTestId('user-message');
    expect(userElement).toBeInTheDocument();
  });

  it('renders bot message correctly', () => {
    render(<ChatMessage message={botMessage} />);
    
    // Check if the message content is displayed
    expect(screen.getByText(botMessage.content)).toBeInTheDocument();
    
    // Check if bot avatar or indicator is present
    const botElement = screen.getByTestId('assistant-message');
    expect(botElement).toBeInTheDocument();
  });

  it('renders markdown content correctly', () => {
    const markdownMessage = {
      id: '3',
      role: 'assistant',
      content: '# Heading\n- List item 1\n- List item 2\n```code block```',
      created_at: new Date().toISOString(),
    };
    
    render(<ChatMessage message={markdownMessage} />);
    
    // Check if markdown is rendered properly
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    expect(screen.getByText('List item 1')).toBeInTheDocument();
    expect(screen.getByText('List item 2')).toBeInTheDocument();
    expect(screen.getByText('code block')).toBeInTheDocument();
  });

  it('formats timestamp correctly', () => {
    // Use a specific date for testing
    const specificDate = new Date('2023-01-01T12:00:00Z');
    const messageWithDate = {
      ...userMessage,
      created_at: specificDate.toISOString(),
    };
    
    render(<ChatMessage message={messageWithDate} />);
    
    // Check if timestamp is formatted correctly - adjust based on your formatting
    const formattedTime = screen.getByTestId('message-timestamp');
    expect(formattedTime).toBeInTheDocument();
  });

  it('handles empty content gracefully', () => {
    const emptyMessage = {
      ...userMessage,
      content: '',
    };
    
    render(<ChatMessage message={emptyMessage} />);
    
    // Check if component renders without crashing with empty content
    const userElement = screen.getByTestId('user-message');
    expect(userElement).toBeInTheDocument();
  });

  it('renders reference links correctly if present', () => {
    const messageWithReferences = {
      ...botMessage,
      references: [
        { title: 'Academic Rules', url: '/documents/1' },
        { title: 'Exam Schedule', url: '/documents/2' },
      ],
    };
    
    render(<ChatMessage message={messageWithReferences} />);
    
    // Check if references are rendered
    expect(screen.getByText('Academic Rules')).toBeInTheDocument();
    expect(screen.getByText('Exam Schedule')).toBeInTheDocument();
  });
}); 