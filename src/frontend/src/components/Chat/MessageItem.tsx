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
  const isUser = message.type === 'user';
  
  return (
    <div
      className={`flex items-start gap-3 ${
        isUser ? 'flex-row-reverse' : ''
      }`}
    >
      <div
        className={`relative p-3 rounded-lg ${
          isUser
            ? 'bg-green-100 dark:bg-green-500/10 border border-green-200 dark:border-green-500/20'
            : 'bg-gray-200 dark:bg-gray-800 border border-gray-300 dark:border-gray-700'
        } max-w-2xl`}
      >
        <div className="flex items-center gap-2 mb-1">
          {isUser ? (
            <User className="w-3 h-3 text-green-600 dark:text-green-400" />
          ) : (
            <Bot className="w-3 h-3 text-green-600 dark:text-green-400" />
          )}
          <span className="text-xs text-green-700/70 dark:text-green-400/60">
            {message.timestamp}
          </span>
        </div>
        <p className="text-sm text-gray-700 dark:text-gray-100">
          {message.content}
        </p>
      </div>
    </div>
  );
};

export default MessageItem;
