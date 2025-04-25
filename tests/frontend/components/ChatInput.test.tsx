import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import ChatInput from '../../../src/frontend/components/ChatInput';

describe('ChatInput Component', () => {
  const mockOnSendMessage = jest.fn();
  
  beforeEach(() => {
    mockOnSendMessage.mockClear();
  });

  it('renders input field and send button', () => {
    render(<ChatInput onSendMessage={mockOnSendMessage} isLoading={false} />);
    
    // Check if input is present
    const inputElement = screen.getByPlaceholderText(/type a message/i);
    expect(inputElement).toBeInTheDocument();
    
    // Check if send button is present
    const sendButton = screen.getByRole('button', { name: /send/i });
    expect(sendButton).toBeInTheDocument();
  });

  it('allows typing in the input field', async () => {
    render(<ChatInput onSendMessage={mockOnSendMessage} isLoading={false} />);
    
    const inputElement = screen.getByPlaceholderText(/type a message/i);
    await userEvent.type(inputElement, 'Hello, world!');
    
    expect(inputElement).toHaveValue('Hello, world!');
  });

  it('sends message when button is clicked', async () => {
    render(<ChatInput onSendMessage={mockOnSendMessage} isLoading={false} />);
    
    const inputElement = screen.getByPlaceholderText(/type a message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    await userEvent.type(inputElement, 'Test message');
    await userEvent.click(sendButton);
    
    // Check if onSendMessage was called with the correct text
    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
    
    // Check if input field was cleared
    expect(inputElement).toHaveValue('');
  });

  it('sends message when Enter is pressed', async () => {
    render(<ChatInput onSendMessage={mockOnSendMessage} isLoading={false} />);
    
    const inputElement = screen.getByPlaceholderText(/type a message/i);
    
    await userEvent.type(inputElement, 'Test message{enter}');
    
    // Check if onSendMessage was called with the correct text
    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
    
    // Check if input field was cleared
    expect(inputElement).toHaveValue('');
  });

  it('does not send empty messages', async () => {
    render(<ChatInput onSendMessage={mockOnSendMessage} isLoading={false} />);
    
    const inputElement = screen.getByPlaceholderText(/type a message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    // Try to send an empty message
    await userEvent.click(sendButton);
    
    // Check that onSendMessage was not called
    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  it('disables input and button when loading', () => {
    render(<ChatInput onSendMessage={mockOnSendMessage} isLoading={true} />);
    
    const inputElement = screen.getByPlaceholderText(/type a message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    // Check if input and button are disabled
    expect(inputElement).toBeDisabled();
    expect(sendButton).toBeDisabled();
  });

  it('displays loading indicator when loading', () => {
    render(<ChatInput onSendMessage={mockOnSendMessage} isLoading={true} />);
    
    // Check if loading indicator is visible
    const loadingIndicator = screen.getByTestId('loading-indicator');
    expect(loadingIndicator).toBeInTheDocument();
  });

  it('trims whitespace from messages', async () => {
    render(<ChatInput onSendMessage={mockOnSendMessage} isLoading={false} />);
    
    const inputElement = screen.getByPlaceholderText(/type a message/i);
    
    await userEvent.type(inputElement, '  Hello world!  ');
    await userEvent.keyboard('{Enter}');
    
    // Check if whitespace was trimmed
    expect(mockOnSendMessage).toHaveBeenCalledWith('Hello world!');
  });
}); 