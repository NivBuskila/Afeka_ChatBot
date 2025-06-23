import { useState, useEffect } from 'react';
import chatService, { ChatSession } from '../../../services/chatService';

interface UseChatSearchReturn {
  chatSearchQuery: string;
  filteredChatSessions: ChatSession[];
  searchChatSessions: (query: string) => Promise<void>;
  setChatSearchQuery: (query: string) => void;
  setFilteredChatSessions: (sessions: ChatSession[]) => void;
}

export function useChatSearch(chatSessions: ChatSession[]): UseChatSearchReturn {
  const [chatSearchQuery, setChatSearchQuery] = useState("");
  const [filteredChatSessions, setFilteredChatSessions] = useState<ChatSession[]>([]);

  // Update filtered sessions when chatSessions changes
  useEffect(() => {
    if (!chatSearchQuery) {
      setFilteredChatSessions(chatSessions);
    }
  }, [chatSessions, chatSearchQuery]);

  const searchChatSessions = async (query: string) => {
    setChatSearchQuery(query);

    if (!query.trim()) {
      setFilteredChatSessions(chatSessions);
      return;
    }

    try {
      const user = await chatService.getCurrentUser();
      if (user) {
        const searchResults = await chatService.searchChatSessions(
          user.id,
          query.trim()
        );
        setFilteredChatSessions(searchResults);
      }
    } catch (error) {
      console.error("Error searching chat sessions:", error);
      // Fallback to local search
      const localResults = chatSessions.filter((session) =>
        session.title?.toLowerCase().includes(query.toLowerCase())
      );
      setFilteredChatSessions(localResults);
    }
  };

  return {
    chatSearchQuery,
    filteredChatSessions,
    searchChatSessions,
    setChatSearchQuery,
    setFilteredChatSessions,
  };
} 