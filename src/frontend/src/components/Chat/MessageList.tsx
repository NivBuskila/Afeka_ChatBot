import React from "react";
import MessageItem from "./MessageItem";


interface Message {
  id: string;
  type: "user" | "bot";
  content: string;
  timestamp: string;
  sessionId?: string;
}

interface MessageListProps {
  messages: Message[];
  fontSize: number;
  highlightIndices?: number[];
  searchTerm?: string;
  showChunkText?: boolean;
}

const MessageList: React.FC<MessageListProps> = ({
  messages,
  fontSize,
  highlightIndices = [],
  searchTerm = "",
  showChunkText = false,
}) => {

  
  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar">
      {/* Simple centered container like Grok */}
      <div className="max-w-3xl mx-auto px-8 py-8">
        <div className="space-y-8">
          {messages.map((msg, index) => (
            <div
              id={`message-${index}`}
              key={msg.id}
              className={`transition-colors duration-300 ${
                highlightIndices.includes(index)
                  ? `ring-2 ring-yellow-400 rounded-lg p-2`
                  : ""
              }`}
            >
              <MessageItem
                message={msg}
                searchTerm={searchTerm}
                showChunkText={showChunkText}
                fontSize={fontSize}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MessageList;
