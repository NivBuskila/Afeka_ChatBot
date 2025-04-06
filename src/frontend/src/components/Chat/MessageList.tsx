import React from 'react';
import MessageItem from './MessageItem';
import { Message } from './types';

interface MessageListProps {
  messages: Message[];
  fontSize: number; 
}

const MessageList: React.FC<MessageListProps> = ({ messages, fontSize }) => {
  return (
    <div
      className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar"
      style={{ fontSize: `${fontSize}px` }}
    >
      {messages.map((msg) => (
        <MessageItem key={msg.id} message={msg} />
      ))}
    </div>
  );
};

export default MessageList;
