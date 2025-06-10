import React, { useRef, useState, useEffect } from 'react';
import { Send } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface ChatInputProps {
  onSend?: () => void;
  isLoading?: boolean;
  isInitial?: boolean;
  input?: string;
  setInput?: (value: string) => void;
  onSendMessage?: (message: string) => void;
  isWaiting?: boolean;
  placeholder?: string;
}

/**
 * ChatInput component with modern floating design
 * Features centered layout, integrated send button, and smooth animations
 */
const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  isLoading = false,
  isInitial = false,
  input,
  setInput,
  onSendMessage,
  isWaiting = false,
  placeholder,
}) => {
  const { t } = useTranslation();
  const [localMessage, setLocalMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  // Determine if we're using props.input or internal state
  const message = input !== undefined ? input : localMessage;
  const updateMessage = setInput || setLocalMessage;
  const handleSend = onSend || (() => onSendMessage && onSendMessage(message));
  const isDisabled = isLoading || isWaiting;
  
  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = '24px'; // Reset height
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = `${Math.min(scrollHeight, 120)}px`;
    }
  }, [message]);
  
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (message.trim() && !isDisabled) {
        handleSend();
      }
    }
  };

  const handleSubmit = () => {
    if (message.trim() && !isDisabled) {
      handleSend();
      // Clear message after sending
      updateMessage('');
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = '24px';
      }
    }
  };

  return (
    <div className="flex justify-center w-full px-6 py-6">
      <div className="w-full max-w-2xl">
        <div className="relative group">
          {/* Main input container with floating design */}
          <div className="relative flex items-end bg-gray-50 dark:bg-gray-800 rounded-3xl shadow-lg hover:shadow-xl transition-all duration-200 ease-in-out border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => updateMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder || (t('chat.inputPlaceholder') as string) || "Type your message here..."}
              disabled={isDisabled}
              rows={1}
              className="flex-1 bg-transparent text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 border-0 outline-none resize-none py-4 px-6 pr-14 min-h-[24px] max-h-[120px] leading-6 chat-input-textarea"
              aria-label={(t('chat.messageInput') as string) || "Message input"}
            />
            
            {/* Integrated send button */}
            <button
              type="button"
              onClick={handleSubmit}
              disabled={!message.trim() || isDisabled}
              className={`absolute right-3 bottom-3 p-2.5 rounded-xl transition-all duration-200 ease-in-out transform ${
                !message.trim() || isDisabled
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed dark:bg-gray-700 dark:text-gray-500'
                  : 'bg-green-500 text-white hover:bg-green-600 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-green-300 focus:ring-offset-2 dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-400 shadow-md hover:shadow-lg'
              }`}
              aria-label={(t('chat.sendMessage') as string) || "Send message"}
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          
          {/* Subtle gradient overlay for enhanced depth */}
          <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-transparent via-white/5 to-transparent pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
        </div>
      </div>
    </div>
  );
};

export default ChatInput;
