import React from 'react';
import { useTranslation } from 'react-i18next';
import MessageList from '../MessageList';
import ChatInput from '../ChatInput';
import LoadingIndicator from './LoadingIndicator';
import { Message } from '../utils/messageFormatter';

interface ChatContentProps {
  messages: Message[];
  input: string;
  isLoading: boolean;
  hasStarted: boolean;
  fontSize: number;
  searchResults: number[];
  searchQuery: string;
  messagesEndRef: React.RefObject<HTMLDivElement>;
  setInput: (value: string) => void;
  onSend: () => void;
}

const ChatContent: React.FC<ChatContentProps> = ({
  messages,
  input,
  isLoading,
  hasStarted,
  fontSize,
  searchResults,
  searchQuery,
  messagesEndRef,
  setInput,
  onSend,
}) => {
  const { t } = useTranslation();

  return (
    <>
      <div className="flex-1 overflow-y-auto">
        {!hasStarted ? (
          <div className="h-full flex flex-col items-center justify-center">
            <h1 className="text-4xl font-bold mb-8 text-gray-800 dark:text-white">
              {(t("chat.startPrompt") as string) || "Start chatting..."}
            </h1>
            {/* Input in the center for new chat */}
            <div className="w-full max-w-md">
              <ChatInput
                input={input}
                setInput={setInput}
                onSend={onSend}
                isLoading={isLoading}
              />
            </div>
          </div>
        ) : (
          <>
            <MessageList
              messages={messages}
              fontSize={fontSize}
              highlightIndices={searchResults}
              searchTerm={searchQuery}
              showChunkText={false}
            />
            <div ref={messagesEndRef} />
            {isLoading && <LoadingIndicator messages={messages} />}
          </>
        )}
      </div>

      {/* Input at the bottom only when conversation has started */}
      {hasStarted && (
        <div className="p-4 flex-shrink-0">
          <ChatInput
            input={input}
            setInput={setInput}
            onSend={onSend}
            isLoading={isLoading}
          />
        </div>
      )}
    </>
  );
};

export default ChatContent; 