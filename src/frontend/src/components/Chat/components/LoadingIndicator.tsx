import React from "react";
import { useTranslation } from "react-i18next";
import { useRTL, useTextDirection } from "../../../hooks";
import { Message } from "../utils/messageFormatter";

interface LoadingIndicatorProps {
  messages: Message[];
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ messages }) => {
  const { t } = useTranslation();
  const { direction, textAlignClass, marginLeft } = useRTL();

  // Check if the last message is a bot message with content (streaming has started)
  const lastMessage = messages[messages.length - 1];
  const isBotStreaming =
    lastMessage && lastMessage.type === "bot" && lastMessage.content.length > 0;

  // Only show preparing response if no bot message is streaming yet
  if (isBotStreaming) {
    return null;
  }

  return (
    <div
      className="max-w-3xl mx-auto px-8 py-4"
      data-testid="typing-indicator"
      dir={direction}
    >
      <div className="w-full">
        <div className="mb-6">
          <div className={`flex items-center gap-2 ${marginLeft}-auto w-fit`}>
            <div className="flex gap-1">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"
                  style={{ animationDelay: `${i * 0.2}s` }}
                />
              ))}
            </div>
            <div
              className={`text-xs text-gray-500 dark:text-gray-500 opacity-60 ${textAlignClass}`}
            >
              {(t("chat.preparingResponse") as string) || "מכין תשובה..."}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;
