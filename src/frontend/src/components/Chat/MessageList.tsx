import React from 'react';
import MessageItem from './MessageItem';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: string;
  sessionId?: string;
}

interface MessageListProps {
  messages: Message[];
  fontSize: number; 
  highlightIndices?: number[];
  searchTerm?: string;
}

const MessageList: React.FC<MessageListProps> = ({ 
  messages, 
  fontSize, 
  highlightIndices = [],
  searchTerm = ''
}) => {
  return (
    <div
      className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar"
      style={{ 
        fontSize: `${fontSize}px`,
        overscrollBehavior: 'contain' 
      }}
    >
      {messages.map((msg, index) => (
        <div
          id={`message-${index}`}
          key={msg.id}
          className={`transition-colors duration-300 rounded-lg ${
            highlightIndices.includes(index) ? 'ring-2 ring-green-500 dark:ring-green-600' : ''
          }`}
        >
          <MessageItem message={msg} searchTerm={searchTerm} />
        </div>
      ))}
    </div>
  );
};

export default MessageList;
