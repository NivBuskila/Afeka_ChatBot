import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useThemeClasses } from "../../hooks/useThemeClasses";

// Custom hooks
import { useChatSessions } from "./hooks/useChatSessions";
import { useChatMessages } from "./hooks/useChatMessages";
import { useMessageSearch } from "./hooks/useMessageSearch";
import { useChatSearch } from "./hooks/useChatSearch";

// Components
import StatusToast from "./components/StatusToast";
import ChatSidebar from "./components/ChatSidebar";
import WelcomeScreen from "./components/WelcomeScreen";
import ChatHeader from "./components/ChatHeader";
import MessageSearchBar from "./components/MessageSearchBar";
import ChatContent from "./components/ChatContent";
import SettingsModal from "./components/SettingsModal";

interface ChatWindowProps {
  onLogout: () => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ onLogout }) => {
  const {} = useTranslation();
  const { chatContainer } = useThemeClasses();

  // UI state
  const [showSettings, setShowSettings] = useState(false);
  const [fontSize] = useState(16);

  // Custom hooks
  const chatSessions = useChatSessions();
  const chatMessages = useChatMessages({
    activeSession: chatSessions.activeSession,
    setChatSessions: chatSessions.setChatSessions,
    setActiveSession: chatSessions.setActiveSession,
    updateChatTitle: chatSessions.updateChatTitle,
  });
  const messageSearch = useMessageSearch(chatMessages.messages);
  const chatSearch = useChatSearch(chatSessions.chatSessions);

  // Initialize status message on mount
  useEffect(() => {
    const initializeStatus = async () => {
      const { statusMessage } = await chatSessions.initializeChat();
      if (statusMessage) {
        chatMessages.setStatusMessage(statusMessage);
        setTimeout(() => chatMessages.setStatusMessage(""), 5000);
      }
    };
    initializeStatus();
  }, []);

  // Handle session selection with message loading
  const handleSelectSession = async (sessionId: string) => {
    await chatSessions.handleSelectSession(sessionId);
    if (sessionId !== "new") {
      await chatMessages.loadSessionMessages(sessionId);
    } else {
      chatMessages.setMessages([]);
      chatMessages.setHasStarted(false);
    }
  };

  return (
    <div
      className={`relative h-full w-full ${chatContainer} flex`}
      data-testid="chat-container"
    >
      {/* Status message toast */}
      {chatMessages.statusMessage && (
        <StatusToast message={chatMessages.statusMessage} />
      )}

      {/* Sidebar */}
      <ChatSidebar
        filteredChatSessions={chatSearch.filteredChatSessions}
        activeSessionId={chatSessions.activeSession?.id}
        isLoadingSessions={chatSessions.isLoadingSessions}
        chatSearchQuery={chatSearch.chatSearchQuery}
        onSearchChange={chatSearch.searchChatSessions}
        onSelectSession={handleSelectSession}
        onDeleteSession={chatSessions.handleDeleteSession}
        onEditSessionTitle={chatSessions.handleEditSessionTitle}
        onNewChat={() => handleSelectSession("new")}
        onOpenSettings={() => setShowSettings(true)}
        onLogout={onLogout}
      />

      {/* Main Chat Window */}
      <div className="flex-1 flex flex-col bg-gray-50 dark:bg-black overflow-hidden">
        {!chatSessions.activeSession ? (
          <WelcomeScreen
            input={chatMessages.input}
            setInput={chatMessages.setInput}
            onSend={chatMessages.handleSend}
            isLoading={chatMessages.isLoading}
          />
        ) : (
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Chat header */}
            <ChatHeader
              sessionTitle={chatSessions.activeSession.title || undefined}
              onToggleSearch={() =>
                messageSearch.setShowSearch(!messageSearch.showSearch)
              }
            />

            {/* Search bar */}
            {messageSearch.showSearch && (
              <MessageSearchBar
                searchQuery={messageSearch.searchQuery}
                searchResults={messageSearch.searchResults}
                currentSearchIndex={messageSearch.currentSearchIndex}
                onSearchChange={messageSearch.searchMessages}
                onNavigateSearch={messageSearch.navigateSearch}
                onCloseSearch={messageSearch.closeSearch}
              />
            )}

            {/* Chat content */}
            <ChatContent
              messages={chatMessages.messages}
              input={chatMessages.input}
              isLoading={chatMessages.isLoading}
              hasStarted={chatMessages.hasStarted}
              fontSize={fontSize}
              searchResults={messageSearch.searchResults}
              searchQuery={messageSearch.searchQuery}
              messagesEndRef={chatMessages.messagesEndRef}
              setInput={chatMessages.setInput}
              onSend={chatMessages.handleSend}
            />
          </div>
        )}
      </div>

      {/* Settings Modal */}
      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
    </div>
  );
};

export default ChatWindow;
