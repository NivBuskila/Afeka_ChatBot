import React from 'react';
import { User, Bot } from 'lucide-react';

interface Message {
  id: number;
  type: 'user' | 'bot';
  content: string;
  timestamp: string;
}

interface MessageItemProps {
  message: Message;
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  return (
    <div
      className={`flex items-start gap-3 ${
        message.type === 'user' ? 'flex-row-reverse' : ''
      }`}
    >
      <div
        className={`relative p-3 rounded-lg ${
          message.type === 'user'
            ? 'bg-green-500/10 border border-green-500/20'
            : 'bg-black/20 dark:bg-gray-700 border border-green-500/10'
        } max-w-2xl`}
      >
        <div className="flex items-center gap-2 mb-1">
          {message.type === 'user' ? (
            <User className="w-3 h-3 text-green-400/80" />
          ) : (
            <Bot className="w-3 h-3 text-green-400/80" />
          )}
          <span className="text-xs text-green-400/60">{message.timestamp}</span>
        </div>
        <p className="text-sm text-white/90">{message.content}</p>
      </div>
    </div>
  );
};

export default MessageItem;
