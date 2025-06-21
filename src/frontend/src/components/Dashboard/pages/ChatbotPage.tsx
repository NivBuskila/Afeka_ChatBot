import React from "react";
import { useTranslation } from "react-i18next";
import ChatWindow from "../../Chat/ChatWindow";

interface ChatbotPageProps {
  onLogout: () => void;
}

export const ChatbotPage: React.FC<ChatbotPageProps> = ({ onLogout }) => {
  const { t } = useTranslation();

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-green-600 dark:text-green-400 mb-4">
        {t("admin.sidebar.chatbotPreview")}
      </h2>
      <div className="bg-gray-100/30 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300/20 dark:border-green-500/20 p-4 h-[calc(100vh-200px)] overflow-auto">
        <div className="h-full relative">
          <ChatWindow onLogout={onLogout} />
        </div>
      </div>
    </div>
  );
}; 