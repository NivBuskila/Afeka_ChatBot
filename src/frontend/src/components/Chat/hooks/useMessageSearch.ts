import { useState } from 'react';

interface Message {
  id: string;
  type: "user" | "bot";
  content: string;
  timestamp: string;
  sessionId?: string;
  chunkText?: string;
}

interface UseMessageSearchReturn {
  showSearch: boolean;
  searchQuery: string;
  searchResults: number[];
  currentSearchIndex: number;
  setShowSearch: (show: boolean) => void;
  searchMessages: (query: string) => void;
  navigateSearch: (direction: 'next' | 'prev') => void;
  closeSearch: () => void;
}

export function useMessageSearch(messages: Message[]): UseMessageSearchReturn {
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<number[]>([]);
  const [currentSearchIndex, setCurrentSearchIndex] = useState(-1);

  const searchMessages = (query: string) => {
    setSearchQuery(query);
    
    if (!query.trim()) {
      setSearchResults([]);
      setCurrentSearchIndex(-1);
      return;
    }

    const lowerQuery = query.toLowerCase();
    const indices: number[] = [];

    messages.forEach((message, index) => {
      if (message.content.toLowerCase().includes(lowerQuery)) {
        indices.push(index);
      }
    });

    setSearchResults(indices);
    setCurrentSearchIndex(indices.length > 0 ? 0 : -1);

    // Scroll to the first result if found
    if (indices.length > 0) {
      scrollToMessage(indices[0]);
    }
  };

  const scrollToMessage = (index: number) => {
    const messageEl = document.getElementById(`message-${index}`);
    if (messageEl) {
      messageEl.scrollIntoView({ behavior: "smooth", block: "center" });
      messageEl.classList.add("bg-green-100", "dark:bg-green-900/30");
      setTimeout(() => {
        messageEl.classList.remove("bg-green-100", "dark:bg-green-900/30");
      }, 1500);
    }
  };

  const navigateSearch = (direction: "next" | "prev") => {
    if (searchResults.length === 0) return;

    let newIndex;
    if (direction === "next") {
      newIndex = (currentSearchIndex + 1) % searchResults.length;
    } else {
      newIndex = (currentSearchIndex - 1 + searchResults.length) % searchResults.length;
    }

    setCurrentSearchIndex(newIndex);
    scrollToMessage(searchResults[newIndex]);
  };

  const closeSearch = () => {
    setShowSearch(false);
    setSearchQuery("");
    setSearchResults([]);
    setCurrentSearchIndex(-1);
  };

  return {
    showSearch,
    searchQuery,
    searchResults,
    currentSearchIndex,
    setShowSearch,
    searchMessages,
    navigateSearch,
    closeSearch,
  };
} 