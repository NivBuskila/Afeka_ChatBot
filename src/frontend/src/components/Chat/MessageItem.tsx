import React, { useState } from "react";
import { User, Bot } from "lucide-react";
import { useTranslation } from "react-i18next";

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
  showChunkText?: boolean; // New prop to control chunk text display
}

// Function to highlight search term in text
const highlightText = (text: string, searchTerm: string) => {
  if (!searchTerm.trim()) return text;

  const parts = text.split(
    new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi")
  );

  return (
    <>
      {parts.map((part, i) =>
        part.toLowerCase() === searchTerm.toLowerCase() ? (
          <mark
            key={i}
            className="bg-yellow-200 dark:bg-yellow-800 px-1 rounded"
          >
            {part}
          </mark>
        ) : (
          part
        )
      )}
    </>
  );
};

const MessageItem: React.FC<MessageItemProps> = ({
  message,
  searchTerm = "",
  showChunkText = false, // Default to false
}) => {
  const { t } = useTranslation();
  const isUser = message.type === "user";
  const [showFullChunk, setShowFullChunk] = useState(false);

  return (
    <div
      className={`flex items-start gap-3 ${isUser ? "flex-row-reverse" : ""}`}
    >
      <div
        className={`relative p-3 rounded-lg ${
          isUser
            ? "bg-green-100 dark:bg-green-500/10 border border-green-200 dark:border-green-500/20"
            : "bg-gray-200 dark:bg-gray-800 border border-gray-300 dark:border-gray-700"
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
        <div
          className="text-sm text-gray-700 dark:text-gray-100"
          dir="rtl"
          style={{
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            fontFamily: "inherit",
          }}
        >
          {searchTerm
            ? highlightText(message.content, searchTerm)
            : message.content}
        </div>

        {/* Show chunk text for bot messages if available and enabled */}
        {!isUser && message.chunkText && showChunkText && (
          <div className="mt-3 pt-3 border-t border-gray-300 dark:border-gray-600">
            <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
              {t("rag.chunkSource") || "מקור הטקסט (צ'אנק):"}
            </p>
            <div className="bg-white dark:bg-black/30 border border-gray-300 dark:border-green-500/30 rounded-lg p-3">
              <div
                className="text-gray-800 dark:text-green-300 text-xs leading-relaxed"
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
                <button
                  onClick={() => setShowFullChunk(!showFullChunk)}
                  className="mt-2 text-green-600 dark:text-green-400 hover:text-green-800 dark:hover:text-green-300 text-xs font-medium flex items-center gap-1 transition-colors"
                >
                  {showFullChunk ? (
                    <>
                      <span>{t("rag.showLess") || "הצג פחות"}</span>
                      <svg
                        className="w-3 h-3 transform rotate-180"
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
                    </>
                  ) : (
                    <>
                      <span>{t("rag.viewMore") || "הצג עוד"}</span>
                      <svg
                        className="w-3 h-3"
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
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageItem;
