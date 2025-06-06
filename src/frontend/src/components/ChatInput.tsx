import React, { useState, useRef, useEffect } from 'react';
import { FiSend } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';

// Define props interface for TypeScript type checking
interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

/**
 * ChatInput component that renders the message input field and send button
 * Handles user input, validation, and submission of messages
 */
const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const { t } = useTranslation();
  const [message, setMessage] = useState<string>('');
  const inputRef = useRef<HTMLTextAreaElement>(null);
  
  // Auto-focus the input field when component mounts
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  // Auto-resize textarea as content grows
  useEffect(() => {
    const textarea = inputRef.current;
    if (textarea) {
      // Reset height to calculate new scroll height
      textarea.style.height = '40px';
      const newHeight = Math.min(textarea.scrollHeight, 150);
      textarea.style.height = `${newHeight}px`;
    }
  }, [message]);

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate message is not empty or just whitespace
    const trimmedMessage = message.trim();
    if (!trimmedMessage || isLoading) {
      return;
    }
    
    // Send message and reset input
    onSendMessage(trimmedMessage);
    setMessage('');
    
    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = '40px';
    }
    
    // Re-focus input after sending
    setTimeout(() => {
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }, 0);
  };

  // Handle Enter key (send message) 
  // Shift+Enter creates a new line
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form 
      onSubmit={handleSubmit}
      className="flex items-end w-full max-w-4xl mx-auto p-4 bg-white border-t border-gray-200 dark:bg-gray-800 dark:border-gray-700"
    >
      <div className="relative flex-grow">
        <textarea
          ref={inputRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t('chat.inputPlaceholder')}
          disabled={isLoading}
          rows={1}
          className="w-full p-3 pr-12 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none min-h-[40px] max-h-[150px] bg-white dark:bg-gray-700 text-gray-900 dark:text-white dark:border-gray-600"
          aria-label={t('chat.messageInput')}
        />
      </div>
      
      <button
        type="submit"
        disabled={!message.trim() || isLoading}
        className={`ml-2 p-3 rounded-full ${
          !message.trim() || isLoading
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed dark:bg-gray-700 dark:text-gray-400'
            : 'bg-green-500 text-white hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-300 dark:bg-green-600 dark:hover:bg-green-700'
        } transition-colors`}
        aria-label={t('chat.sendMessage')}
      >
        <FiSend className="w-5 h-5" />
      </button>
    </form>
  );
};

export default ChatInput; 