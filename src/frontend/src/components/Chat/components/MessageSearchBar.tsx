import React from 'react';
import { useTranslation } from 'react-i18next';
import { X } from 'lucide-react';

interface MessageSearchBarProps {
  searchQuery: string;
  searchResults: number[];
  currentSearchIndex: number;
  onSearchChange: (query: string) => void;
  onNavigateSearch: (direction: 'next' | 'prev') => void;
  onCloseSearch: () => void;
}

const MessageSearchBar: React.FC<MessageSearchBarProps> = ({
  searchQuery,
  searchResults,
  currentSearchIndex,
  onSearchChange,
  onNavigateSearch,
  onCloseSearch,
}) => {
  const { t } = useTranslation();

  return (
    <div className="p-2 bg-gray-100 dark:bg-black flex items-center flex-shrink-0">
      <div className="relative flex-1 max-w-md mx-auto">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder={
            (t("chat.searchMessages") as string) || "Search messages..."
          }
          className="w-full py-1 px-3 pr-20 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent"
          autoFocus
        />
        <div className="absolute right-1 top-1/2 transform -translate-y-1/2 flex items-center">
          {searchResults.length > 0 && (
            <span className="text-xs text-gray-500 dark:text-gray-400 mr-1">
              {currentSearchIndex + 1}/{searchResults.length}
            </span>
          )}
          <button
            onClick={() => onNavigateSearch("prev")}
            disabled={searchResults.length === 0}
            className="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 disabled:opacity-50"
            title={(t("chat.previous") as string) || "Previous"}
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 15l7-7 7 7"
              />
            </svg>
          </button>
          <button
            onClick={() => onNavigateSearch("next")}
            disabled={searchResults.length === 0}
            className="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 disabled:opacity-50"
            title={(t("chat.next") as string) || "Next"}
          >
            <svg
              className="w-4 h-4"
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
          </button>
          <button
            onClick={onCloseSearch}
            className="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
            title={(t("chat.close") as string) || "Close"}
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default MessageSearchBar; 