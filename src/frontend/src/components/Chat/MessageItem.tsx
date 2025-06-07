import React from 'react';
import { User, Bot, BookOpen, Brain, MessageCircle } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: string;
  sessionId?: string;
  sourceInfo?: {
    type: string;
    description: string;
    sourcesCount: number;
    chunksCount: number;
    sources: string[];
  };
}

interface MessageItemProps {
  message: Message;
  searchTerm?: string;
}

// Function to highlight search term in text
const highlightText = (text: string, searchTerm: string) => {
  if (!searchTerm.trim()) return text;
  
  const parts = text.split(new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'));
  
  return (
    <>
      {parts.map((part, i) => 
        part.toLowerCase() === searchTerm.toLowerCase() ? (
          <mark key={i} className="bg-yellow-200 dark:bg-yellow-800 px-1 rounded">
            {part}
          </mark>
        ) : (
          part
        )
      )}
    </>
  );
};

// Function to get source indicator
const getSourceIndicator = (sourceInfo?: Message['sourceInfo']) => {
  if (!sourceInfo) return null;

  const { type, description, sourcesCount, chunksCount } = sourceInfo;

  let icon, bgColor, textColor, borderColor;

  switch (type) {
    case 'rag':
      icon = <BookOpen className="w-3 h-3" />;
      bgColor = 'bg-blue-50 dark:bg-blue-900/20';
      textColor = 'text-blue-700 dark:text-blue-300';
      borderColor = 'border-blue-200 dark:border-blue-700';
      break;
    case 'llm':
      icon = <Brain className="w-3 h-3" />;
      bgColor = 'bg-purple-50 dark:bg-purple-900/20';
      textColor = 'text-purple-700 dark:text-purple-300';
      borderColor = 'border-purple-200 dark:border-purple-700';
      break;
    case 'conversation':
      icon = <MessageCircle className="w-3 h-3" />;
      bgColor = 'bg-orange-50 dark:bg-orange-900/20';
      textColor = 'text-orange-700 dark:text-orange-300';
      borderColor = 'border-orange-200 dark:border-orange-700';
      break;
    default:
      return null;
  }

  return (
    <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs border ${bgColor} ${textColor} ${borderColor} mt-2`}>
      {icon}
      <span className="font-medium">
        {type === 'rag' && `📚 ${sourcesCount} מקורות`}
        {type === 'llm' && '🧠 תשובה כללית'}
        {type === 'conversation' && '💬 שיחה'}
      </span>
      {description && (
        <span className="text-xs opacity-75 mr-1">
          • {description}
        </span>
      )}
    </div>
  );
};

const MessageItem: React.FC<MessageItemProps> = ({ message, searchTerm = '' }) => {
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
          {searchTerm ? highlightText(message.content, searchTerm) : message.content}
        </p>
        
        {/* Source indicator for bot messages */}
        {!isUser && message.sourceInfo && (
          <div className="mt-2">
            {getSourceIndicator(message.sourceInfo)}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageItem;
