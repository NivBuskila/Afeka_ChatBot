import React, { KeyboardEvent } from 'react';
import { Send } from 'lucide-react';

interface ChatInputProps {
  input: string;
  setInput: (val: string) => void;
  onSend: () => void;
  isLoading: boolean;
  isInitial?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ 
  input, 
  setInput, 
  onSend, 
  isLoading,
  isInitial = false 
}) => {
  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSend();
    }
  };

  return (
    <div className={`${isInitial ? '' : 'p-4 bg-gray-100 dark:bg-black/20 border-t border-gray-200 dark:border-green-500/10'}`}>
      <div className="relative max-w-4xl mx-auto">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask anything..."
          disabled={isLoading}
          className={`w-full bg-white dark:bg-gray-800 text-gray-800 dark:text-white rounded-lg ${isInitial ? 'p-4 border border-gray-200 dark:border-gray-700' : 'p-4 pr-12 border border-gray-300 dark:border-gray-700'}
                     focus:outline-none focus:ring-2 focus:ring-green-500
                     placeholder-gray-400 dark:placeholder-gray-500
                     shadow-sm`}
        />
        <button
          onClick={onSend}
          disabled={isLoading}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-2 
                     hover:bg-gray-100 dark:hover:bg-gray-700
                     rounded-lg transition-colors"
        >
          <Send className="w-5 h-5 text-green-700 dark:text-green-500" />
        </button>
      </div>
    </div>
  );
};

export default ChatInput;
