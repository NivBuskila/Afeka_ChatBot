import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useRTL, useTextDirection } from "../../hooks";

import ThemeButton from "../ui/ThemeButton";
import AIResponseRenderer from "../common/AIResponseRenderer";

interface Message {
  id: string;
  type: "user" | "bot";
  content: string;
  timestamp: string;
  sessionId?: string;
  chunkText?: string;
}

interface MessageItemProps {
  message: Message;
  searchTerm?: string;
  showChunkText?: boolean;
  fontSize?: number;
}

// Utility function to highlight search terms - for user messages only
const highlightText = (text: string, searchTerm: string) => {
  if (!searchTerm.trim()) return text;

  const regex = new RegExp(
    `(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`,
    "gi"
  );
  const parts = text.split(regex);

  return parts.map((part, index) =>
    regex.test(part) ? (
      <span
        key={index}
        className="bg-yellow-200 dark:bg-yellow-600 px-1 rounded"
      >
        {part}
      </span>
    ) : (
      part
    )
  );
};

const MessageItem: React.FC<MessageItemProps> = ({
  message,
  searchTerm = "",
  showChunkText = false,
  fontSize = 16,
}) => {
  const { t } = useTranslation();

  // Auto-detect text direction for this specific message
  const { direction: messageDirection, textAlign: messageTextAlign } =
    useTextDirection(message.content);
  const { direction: chunkDirection } = useTextDirection(
    message.chunkText || ""
  );

  const isUser = message.type === "user";
  const [showFullChunk, setShowFullChunk] = useState(false);

  return (
    <div
      className={`w-full ${messageTextAlign}`}
      data-testid={isUser ? "user-message" : "bot-message"}
    >
      {/* Message content */}
      <div className={`mb-6 ${isUser ? messageTextAlign : ""}`}>
        {isUser ? (
          // User message with bubble - positioned based on text direction
          <div
            className={`bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 inline-block max-w-sm border border-gray-200 dark:border-gray-600 shadow-lg hover:shadow-xl transition-shadow duration-200 leading-relaxed ${
              messageDirection === "rtl" ? "ml-auto" : "mr-auto"
            }`}
            dir={messageDirection}
            style={{
              fontSize: `${fontSize}px`,
              fontFamily: "inherit",
              lineHeight: "1.6",
              borderRadius:
                messageDirection === "rtl"
                  ? "20px 20px 20px 4px"
                  : "20px 20px 4px 20px",
            }}
          >
            {searchTerm
              ? highlightText(message.content, searchTerm)
              : message.content}
          </div>
        ) : (
          // Bot message - completely clean like ChatGPT
          <div className="w-full max-w-4xl">
            <div
              className="text-gray-800 dark:text-gray-200 leading-relaxed"
              style={{
                fontSize: `${fontSize}px`,
                fontFamily: "inherit",
                lineHeight: "1.7",
              }}
              dir={messageDirection}
            >
              <AIResponseRenderer
                content={message.content}
                searchTerm={searchTerm}
                className="ai-response-content"
                dir={messageDirection}
              />
            </div>
          </div>
        )}

        {/* Timestamp - subtle and small - only show if timestamp exists */}
        {message.timestamp && (
          <div
            className={`mt-2 text-xs text-gray-500 dark:text-gray-500 opacity-60`}
          >
            {message.timestamp}
          </div>
        )}

        {/* Show chunk text for bot messages if available and enabled */}
        {!isUser && message.chunkText && showChunkText && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
              {t("rag.chunkSource") || "מקור הטקסט (צ'אנק):"}
            </p>
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              <div
                className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed"
                dir={chunkDirection}
                style={{
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-word",
                  fontFamily: "inherit",
                }}
              >
                {showFullChunk
                  ? message.chunkText
                  : `${message.chunkText.substring(0, 200)}${
                      message.chunkText.length > 200 ? "..." : ""
                    }`}
              </div>

              {message.chunkText.length > 200 && (
                <div className="mt-3">
                  <ThemeButton
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowFullChunk(!showFullChunk)}
                    className="text-xs font-medium"
                    icon={
                      <svg
                        className={`w-3 h-3 ${
                          showFullChunk ? "transform rotate-180" : ""
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                    }
                  >
                    {showFullChunk
                      ? t("rag.showLess") || "הצג פחות"
                      : t("rag.viewMore") || "הצג עוד"}
                  </ThemeButton>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageItem;
