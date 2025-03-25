import React, { KeyboardEvent } from 'react';
import { Send } from 'lucide-react';

interface ChatInputProps {
  input: string;
  setInput: (val: string) => void;
  onSend: () => void;
  isLoading: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ input, setInput, onSend, isLoading }) => {
  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSend();
    }
  };

  return (
    <div className="p-4 bg-black/20 border-t border-green-500/10">
      <div className="relative">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={isLoading}
          className="w-full bg-black/40 text-white rounded-lg p-3 pr-12 text-sm
                     focus:outline-none focus:ring-1 focus:ring-green-500/30
                     placeholder-gray-500"
        />
        <button
          onClick={onSend}
          disabled={isLoading}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-2 hover:bg-green-500/10
                     rounded-lg transition-colors"
        >
          <Send className="w-4 h-4 text-green-400/80" />
        </button>
      </div>
    </div>
  );
};

export default ChatInput;
