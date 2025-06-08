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
      textareaRef.current.style.height = '40px'; // Reset height
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = `${Math.min(scrollHeight, 150)}px`;
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

  return (
    <div className={`w-full relative ${isInitial ? 'max-w-xl mx-auto' : ''}`}>
      <div className="relative flex items-center">
        <textarea
          ref={textareaRef}
          className="w-full py-2 px-4 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 pr-10 min-h-[40px] max-h-[150px] resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white border-gray-300 dark:border-gray-600"
          value={message}
          onChange={(e) => updateMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder || t('chat.inputPlaceholder')}
          disabled={isDisabled}
          rows={1}
        />
        <button
          onClick={() => {
            if (message.trim() && !isDisabled) {
              handleSend();
            }
          }}
          disabled={!message.trim() || isDisabled}
          className={`absolute right-3 top-1/2 transform -translate-y-1/2 ${
            !message.trim() || isDisabled 
              ? 'text-gray-400 cursor-not-allowed' 
              : 'text-green-500 hover:text-green-700 focus:outline-none'
          } transition-colors`}
          aria-label={t('chat.sendMessage')}
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
};

export default ChatInput;
