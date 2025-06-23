import React from 'react';
import { useTranslation } from 'react-i18next';
import { Search } from 'lucide-react';

interface ChatHeaderProps {
  sessionTitle?: string;
  onToggleSearch: () => void;
}

const ChatHeader: React.FC<ChatHeaderProps> = ({ sessionTitle, onToggleSearch }) => {
  const { t } = useTranslation();

  return (
    <div className="flex justify-center items-center py-4 flex-shrink-0">
      <div className="flex items-center space-x-4">
        <h1 className="text-lg font-medium text-gray-700 dark:text-gray-300">
          {sessionTitle || (t("chat.newChat") as string) || "ChatGPT"}
        </h1>

        {/* Search button - minimal style */}
        <button
          onClick={onToggleSearch}
          className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          title={(t("chat.search") as string) || "Search"}
        >
          <Search className="h-4 w-4 text-gray-500 dark:text-gray-400" />
        </button>
      </div>
    </div>
  );
};

export default ChatHeader; 