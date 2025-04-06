import React, { useState, useRef, useEffect, useCallback } from 'react';
import { FiSend } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';

// Define the textarea resize hook locally to avoid import issues
const useTextareaResize = (
  textareaRef: React.RefObject<HTMLTextAreaElement>,
  maxHeight: number = 150
) => {
  // Handle resizing the textarea
  const handleResize = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    
    // Reset height to calculate the new scroll height
    textarea.style.height = 'auto';
    
    // Set the new height based on scroll height (with max height limit)
    const newHeight = Math.min(textarea.scrollHeight, maxHeight);
    textarea.style.height = `${newHeight}px`;
  }, [textareaRef, maxHeight]);

  return { handleResize };
};

// Define props interface for TypeScript type checking to match existing usage
interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  onSend: () => void;
  isLoading: boolean;
  isInitial?: boolean;
}

/**
 * ChatInput component that renders the message input field and send button
 * Follows SOLID principles with clear separation of concerns
 */
const ChatInput: React.FC<ChatInputProps> = ({ 
  input, 
  setInput, 
  onSend, 
  isLoading,
  isInitial = false 
}) => {
  const { t, i18n } = useTranslation();
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  // Use custom hook for textarea resize when not in initial mode
  const { handleResize } = useTextareaResize(textareaRef, 150);
  
  // Auto-focus the input field when component mounts
  useEffect(() => {
    if (textareaRef.current && !isInitial) {
      textareaRef.current.focus();
    }
  }, [isInitial]);

  // Handle message input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setInput(e.target.value);
    
    // Only apply resize if using textarea (non-initial mode)
    if (!isInitial && textareaRef.current) {
      handleResize();
    }
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate message is not empty or just whitespace
    const trimmedMessage = input.trim();
    if (!trimmedMessage || isLoading) {
      return;
    }
    
    // Send message
    onSend();
    
    // Reset textarea height if not in initial mode
    if (!isInitial && textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    
    // Re-focus input after sending
    setTimeout(() => {
      if (textareaRef.current && !isInitial) {
        textareaRef.current.focus();
      }
    }, 0);
  };

  // Handle Enter key (send message) 
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Use different UI for initial vs chat modes
  if (isInitial) {
    return (
      <div className="relative max-w-4xl mx-auto">
        <input
          type="text"
          value={input}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          placeholder={i18n.language === 'he' ? 'שאל כל שאלה...' : 'Ask anything...'}
          disabled={isLoading}
          className="w-full bg-white dark:bg-gray-800 text-gray-800 dark:text-white rounded-lg p-4 pr-12 border border-gray-200 dark:border-gray-700
                     focus:outline-none focus:ring-2 focus:ring-green-500
                     placeholder-gray-400 dark:placeholder-gray-500
                     shadow-sm"
        />
        <button
          onClick={onSend}
          disabled={isLoading || !input.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-2 
                     hover:bg-gray-100 dark:hover:bg-gray-700
                     rounded-lg transition-colors"
          aria-label={t('chat.sendMessage') || "Send message"}
        >
          <FiSend className="w-5 h-5 text-green-700 dark:text-green-500" />
        </button>
      </div>
    );
  }

  // Regular chat input with textarea
  return (
    <div className="p-4 bg-gray-100 dark:bg-black/20 border-t border-gray-200 dark:border-green-500/10">
      <div className="relative max-w-4xl mx-auto">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyPress}
          placeholder={i18n.language === 'he' ? 'שאל כל שאלה...' : 'Ask anything...'}
          disabled={isLoading}
          rows={1}
          className="w-full p-4 pr-12 bg-white dark:bg-gray-800 text-gray-800 dark:text-white rounded-lg border border-gray-300 dark:border-gray-700
                   focus:outline-none focus:ring-2 focus:ring-green-500
                   resize-none
                   placeholder-gray-400 dark:placeholder-gray-500
                   shadow-sm"
        />
        <button
          onClick={onSend}
          disabled={isLoading || !input.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-2 
                     hover:bg-gray-100 dark:hover:bg-gray-700
                     rounded-lg transition-colors"
          aria-label={t('chat.sendMessage') || "Send message"}
        >
          <FiSend className="w-5 h-5 text-green-700 dark:text-green-500" />
        </button>
      </div>
    </div>
  );
};

export default ChatInput;
