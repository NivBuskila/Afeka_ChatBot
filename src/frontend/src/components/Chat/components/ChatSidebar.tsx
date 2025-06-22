import React from 'react';
import { useTranslation } from 'react-i18next';
import { Settings, LogOut, Plus, Search, X } from 'lucide-react';
import ChatHistory from '../ChatHistory';
import ThemeButton from '../../ui/ThemeButton';
import { ChatSession } from '../../../services/chatService';
import { useThemeClasses } from '../../../hooks/useThemeClasses';

interface ChatSidebarProps {
  chatSessions: ChatSession[];
  filteredChatSessions: ChatSession[];
  activeSessionId?: string;
  isLoadingSessions: boolean;
  chatSearchQuery: string;
  onSearchChange: (query: string) => void;
  onSelectSession: (sessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
  onEditSessionTitle: (sessionId: string, title: string) => void;
  onNewChat: () => void;
  onOpenSettings: () => void;
  onLogout: () => void;
}

const ChatSidebar: React.FC<ChatSidebarProps> = ({
  chatSessions,
  filteredChatSessions,
  activeSessionId,
  isLoadingSessions,
  chatSearchQuery,
  onSearchChange,
  onSelectSession,
  onDeleteSession,
  onEditSessionTitle,
  onNewChat,
  onOpenSettings,
  onLogout,
}) => {
  const { t } = useTranslation();
  const { classes, chatSidebar } = useThemeClasses();

  return (
    <div className={`h-full flex flex-col ${chatSidebar} w-60 overflow-hidden flex-shrink-0`}>
      {/* Sidebar header with logo and main actions */}
      <div className={`p-3 border-b ${classes.border.primary} flex items-center justify-between`}>
        <div className={`${classes.text.success} font-bold text-lg tracking-wider`}>
          APEX
        </div>
        <div className="flex items-center space-x-2">
          <ThemeButton
            variant="success"
            size="sm"
            onClick={onNewChat}
            icon={<Plus className="w-3.5 h-3.5" />}
            title={(t("chat.history.newChat") as string) || "צ'אט חדש"}
          />
          <ThemeButton
            variant="ghost"
            size="sm"
            onClick={onOpenSettings}
            icon={<Settings className="w-4 h-4" />}
            title={(t("chat.sidebar.settings") as string) || "Settings"}
          />
        </div>
      </div>

      {/* Search input */}
      <div className="px-3 py-2 border-b border-gray-300 dark:border-gray-700">
        <div className="relative">
          <input
            type="text"
            placeholder={(t("chat.history.search") as string) || "Search..."}
            className="w-full px-2 py-1.5 pr-7 text-xs rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-black text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-green-500"
            value={chatSearchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
          />
          {chatSearchQuery ? (
            <button
              onClick={() => onSearchChange("")}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="w-3 h-3" />
            </button>
          ) : (
            <Search className="absolute right-2 top-1/2 transform -translate-y-1/2 w-3 h-3 text-gray-400" />
          )}
        </div>
      </div>

      {/* Chat history list */}
      <div className="flex-1 overflow-y-auto">
        <ChatHistory
          sessions={filteredChatSessions}
          onSelectSession={(session) => onSelectSession(session.id)}
          onCreateNewSession={onNewChat}
          onDeleteSession={onDeleteSession}
          onEditSessionTitle={onEditSessionTitle}
          activeSessionId={activeSessionId}
          isLoading={isLoadingSessions}
        />
      </div>

      {/* Logout Button */}
      <div className="p-3 border-t border-gray-300 dark:border-gray-700">
        <button
          onClick={onLogout}
          className="w-full flex items-center justify-center p-2 gap-2 rounded-md hover:bg-red-100 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400"
          title={(t("common.logout") as string) || "Logout"}
        >
          <LogOut className="w-4 h-4" />
          <span className="text-sm">
            {(t("common.logout") as string) || "Logout"}
          </span>
        </button>
      </div>
    </div>
  );
};

export default ChatSidebar; 