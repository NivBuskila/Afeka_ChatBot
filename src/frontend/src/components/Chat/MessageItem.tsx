import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useThemeClasses } from '../../hooks/useThemeClasses';
import ThemeButton from '../ui/ThemeButton';

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

// Utility function to highlight search terms
const highlightText = (text: string, searchTerm: string) => {
  if (!searchTerm.trim()) return text;

  const regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  const parts = text.split(regex);

  return parts.map((part, index) =>
    regex.test(part) ? (
      <span key={index} className="bg-yellow-200 dark:bg-yellow-600 px-1 rounded">
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
  const { classes } = useThemeClasses();
  const isUser = message.type === "user";
  const [showFullChunk, setShowFullChunk] = useState(false);

          return (
      <div className={`w-full ${isUser ? "text-right" : "text-right"}`}>
        {/* Message content */}
        <div className={`mb-6 ${isUser ? "text-right" : "text-right"}`}>
          <div
            className={`${
              isUser 
                ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 inline-block max-w-sm border border-gray-200 dark:border-gray-600 shadow-lg hover:shadow-xl transition-shadow duration-200' 
                : 'text-gray-800 dark:text-gray-200'
            } leading-relaxed`}
          dir="rtl"
          style={{
            fontSize: `${fontSize}px`,
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            fontFamily: "inherit",
            lineHeight: "1.6",
            borderRadius: isUser ? '20px 20px 4px 20px' : '20px 20px 20px 4px'
          }}
        >
          {searchTerm
            ? highlightText(message.content, searchTerm)
            : message.content}
        </div>

        {/* Timestamp - subtle and small */}
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-500 opacity-60">
          {message.timestamp}
        </div>

        {/* Show chunk text for bot messages if available and enabled */}
        {!isUser && message.chunkText && showChunkText && (
          <div className="mt-4 pt-4 border-t border-gray-700 dark:border-gray-600">
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
              {t("rag.chunkSource") || "מקור הטקסט (צ'אנק):"}
            </p>
            <div className="bg-gray-800 dark:bg-gray-800 rounded-lg p-4 border border-gray-700 dark:border-gray-600">
              <div
                className="text-sm text-gray-300 dark:text-gray-300 leading-relaxed"
                dir="rtl"
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
                        className={`w-3 h-3 ${showFullChunk ? 'transform rotate-180' : ''}`}
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
                    {showFullChunk ? (t("rag.showLess") || "הצג פחות") : (t("rag.viewMore") || "הצג עוד")}
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
