import { useState, useEffect } from 'react';
import chatService, { ChatSession } from '../../../services/chatService';
import titleGenerationService from '../../../services/titleGenerationService';

interface UseChatSessionsReturn {
  chatSessions: ChatSession[];
  activeSession: ChatSession | null;
  isLoadingSessions: boolean;
  isInitializing: boolean;
  setActiveSession: (session: ChatSession | null) => void;
  setChatSessions: React.Dispatch<React.SetStateAction<ChatSession[]>>;
  handleSelectSession: (sessionId: string) => Promise<void>;
  handleDeleteSession: (sessionId: string) => Promise<void>;
  handleEditSessionTitle: (sessionId: string, title: string) => Promise<void>;
  updateChatTitle: (sessionId: string, messages: any[]) => Promise<void>;
  loadUserSessions: () => Promise<void>;
  initializeChat: () => Promise<{ user: any; statusMessage: string }>;
}

export function useChatSessions(): UseChatSessionsReturn {
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [isInitializing, setIsInitializing] = useState(false);

  // Load user chat sessions when hook mounts
  useEffect(() => {
    initializeChat();
  }, []);

  const loadUserSessions = async () => {
    const user = await chatService.getCurrentUser();
    if (user) {
      setIsLoadingSessions(true);
      const sessions = await chatService.fetchAllChatSessions(user.id);
      setChatSessions(sessions);
      setIsLoadingSessions(false);
    }
  };

  const handleSelectSession = async (sessionId: string) => {
    if (sessionId === "new") {
      setActiveSession(null);
      return;
    }

    try {
      const session = await chatService.getChatSessionWithMessages(sessionId);
      if (session) {
        setActiveSession(session);
      }
    } catch (error) {
      console.error("Error loading chat session:", error);
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      const success = await chatService.deleteChatSession(sessionId);
      if (success) {
        setChatSessions((prev) => prev.filter((s) => s.id !== sessionId));
        
        if (activeSession?.id === sessionId) {
          setActiveSession(null);
        }
      }
    } catch (error) {
      console.error("Error deleting chat session:", error);
    }
  };

  const handleEditSessionTitle = async (sessionId: string, title: string) => {
    try {
      const success = await chatService.updateChatSessionTitle(sessionId, title);
      if (success) {
        setChatSessions((prev) =>
          prev.map((s) => (s.id === sessionId ? { ...s, title } : s))
        );

        if (activeSession?.id === sessionId) {
          setActiveSession((prev) => (prev ? { ...prev, title } : null));
        }
      }
    } catch (error) {
      console.error("Error updating chat session title:", error);
    }
  };

  const updateChatTitle = async (sessionId: string, messages: any[]) => {
    try {
      if (!titleGenerationService.shouldUpdateTitle(
        activeSession?.title || null,
        messages.length
      )) {
        return;
      }

      const currentTitle = activeSession?.title || "";

      if (!titleGenerationService.isDefaultTitle(currentTitle) && messages.length < 6) {
        return;
      }

      let newTitle = await titleGenerationService.generateTitle(messages);

      if (!newTitle) {
        const firstUserMessage = messages.find((msg) => msg.type === "user")?.content || "";
        newTitle = titleGenerationService.generateSimpleTitle(firstUserMessage);
      }

      const success = await chatService.updateChatSessionTitle(sessionId, newTitle);

      if (success) {
        setActiveSession((prev) => prev ? { ...prev, title: newTitle } : null);
        setChatSessions((prev) =>
          prev.map((session) =>
            session.id === sessionId ? { ...session, title: newTitle } : session
          )
        );
      }
    } catch (error) {
      console.error("Error updating chat title:", error);
    }
  };

  const initializeChat = async () => {
    setIsInitializing(true);
    const user = await chatService.getCurrentUser();
    let statusMessage = "";

    if (user) {
      const sessions = await chatService.fetchAllChatSessions(user.id);
      setChatSessions(sessions);
      setActiveSession(null);
    } else {
      setChatSessions([]);
      statusMessage = "You are in demo mode. Messages will not be saved. Please log in to save your chats.";
    }

    setIsInitializing(false);
    return { user, statusMessage };
  };

  return {
    chatSessions,
    activeSession,
    isLoadingSessions,
    isInitializing,
    setActiveSession,
    setChatSessions,
    handleSelectSession,
    handleDeleteSession,
    handleEditSessionTitle,
    updateChatTitle,
    loadUserSessions,
    initializeChat,
  };
} 