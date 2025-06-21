import React from "react";
import ChatWindow from "../../Chat/ChatWindow";
import { translations } from "../translations";

interface ChatbotPageProps {
  onLogout: () => void;
}

export const ChatbotPage: React.FC<ChatbotPageProps> = ({ onLogout }) => {
  // Get current language from HTML document
  const isRTL = document.documentElement.dir === 'rtl';
  const language = isRTL ? 'he' : 'en';
  const t = (key: string) => translations[key]?.[language] || key;

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">
          {t("chatbot.preview")}
        </h2>
      </div>
      <div className="bg-gray-100/30 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300/20 dark:border-green-500/20 p-4 h-[calc(100vh-200px)] overflow-auto">
        <div className="h-full relative">
          <ChatWindow onLogout={onLogout} />
        </div>
      </div>
    </div>
  );
}; 