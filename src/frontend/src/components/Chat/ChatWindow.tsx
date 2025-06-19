import React, { useState, useEffect, useRef } from "react";
import MessageList from "./MessageList";
import ChatInput from "./ChatInput";
import ChatHistory from "./ChatHistory";
import {
  Terminal,
  History,
  Settings,
  LogOut,
  Plus,
  Search,
  X,
  Bot,
} from "lucide-react";
import SettingsPanel from "./SettingsPanel";
import { API_CONFIG } from "../../config/constants";
import UserSettings from "../Settings/UserSettings";
import chatService, { ChatSession } from "../../services/chatService";
import titleGenerationService from "../../services/titleGenerationService";
import { useTranslation } from "react-i18next";
import { supabase } from "../../config/supabase";
import { useThemeClasses } from "../../hooks/useThemeClasses";
import ThemeButton from "../ui/ThemeButton";
import ThemeCard from "../ui/ThemeCard";

// Interface for message display
interface Message {
  id: string;
  type: "user" | "bot";
  content: string;
  timestamp: string;
  sessionId?: string;
  chunkText?: string; // Added chunk text for bot messages
}

interface ChatWindowProps {
  onLogout: () => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ onLogout }) => {
  const { t, i18n } = useTranslation();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Status message state for notifications
  const [statusMessage, setStatusMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // UI state
  const [isExpanded, setIsExpanded] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const {
    currentTheme,
    classes,
    chatContainer,
    chatSidebar,
    primaryButton,
    cardBackground,
    textPrimary,
  } = useThemeClasses();
  const [hasStarted, setHasStarted] = useState(false);
  const [fontSize, setFontSize] = useState(16);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Chat history state
  const [showHistory, setShowHistory] = useState(false);
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);

  // Search state
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<number[]>([]);
  const [currentSearchIndex, setCurrentSearchIndex] = useState(-1);

  // Chat search state - for sidebar search
  const [chatSearchQuery, setChatSearchQuery] = useState("");
  const [filteredChatSessions, setFilteredChatSessions] = useState<
    ChatSession[]
  >([]);

  // Load user chat sessions
  useEffect(() => {
    const initializeChat = async () => {
      setIsLoading(true);
      const user = await chatService.getCurrentUser();

      if (user) {
        console.log("User logged in, initializing chat history...");
        // Fetch user's chat sessions
        const sessions = await chatService.getUserChatSessions(user.id);
        console.log(`Found ${sessions.length} chat sessions`);
        setChatSessions(sessions);

        // Start with a new empty chat instead of loading the most recent session
        setActiveSession(null);
        setMessages([]);
        setHasStarted(false);
      } else {
        // In demo mode, just start with empty state
        console.log("User not logged in, starting in demo mode");
        setChatSessions([]);
        setMessages([]);
        setStatusMessage(
          "You are in demo mode. Messages will not be saved. Please log in to save your chats."
        );
        setTimeout(() => setStatusMessage(""), 5000);
      }

      setIsLoading(false);
    };

    initializeChat();
  }, []);

  // Load user chat sessions when component mounts
  useEffect(() => {
    const loadUserSessions = async () => {
      const user = await chatService.getCurrentUser();
      if (user) {
        setIsLoadingSessions(true);
        const sessions = await chatService.getUserChatSessions(user.id);
        setChatSessions(sessions);
        setIsLoadingSessions(false);
      }
    };

    loadUserSessions();
  }, []);

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Update filtered sessions when chatSessions changes
  useEffect(() => {
    if (!chatSearchQuery) {
      setFilteredChatSessions(chatSessions);
    }
  }, [chatSessions, chatSearchQuery]);

  // Helper function to load session messages
  const loadSessionMessages = async (sessionId: string) => {
    try {
      console.log(`🔍 Loading messages for session: ${sessionId}`);
      const session = await chatService.getChatSessionWithMessages(sessionId);
      console.log(`🔍 Received session data:`, session);

      if (session && session.messages && session.messages.length > 0) {
        console.log(`🔍 Found ${session.messages.length} messages`);
        console.log(`🔍 First message:`, session.messages[0]);
        
        const formattedMessages = session.messages.map(
          (msg: any, index: number) => {
            // זיהוי סוג הודעה עם fallback logic לשיחות ישנות
            let isBot = false;

            if (msg.role === "bot" || msg.role === "assistant") {
              isBot = true;
            } else if (msg.is_bot === true || msg.is_bot === 1) {
              isBot = true;
            } else if (msg.role === "user" && index % 2 === 1) {
              isBot = true;
            } else if (
              msg.content &&
              msg.content.length > 100 &&
              msg.role === "user"
            ) {
              isBot = true;
            }

            let messageContent =
              msg.content || msg.message_text || msg.text || "";
            const messageId =
              msg.id || msg.message_id || `msg-${Date.now()}-${index}`;
              
            console.log(`🔍 Processing message ${index}: role=${msg.role}, isBot=${isBot}, content length=${messageContent.length}`);

            return {
              id: messageId,
              type: (isBot ? "bot" : "user") as "bot" | "user",
              content: messageContent,
              timestamp: new Date(msg.created_at).toLocaleTimeString(),
              sessionId:
                msg.chat_session_id || msg.conversation_id || sessionId,
            };
          }
        );

        console.log(`🔍 Formatted ${formattedMessages.length} messages`);
        setMessages(formattedMessages);
        setHasStarted(formattedMessages.length > 0);
      } else {
        console.log(`🔍 No messages found for session ${sessionId}`);
      }
    } catch (error) {
      console.error("Error reloading session messages:", error);
    }
  };

  const handleSelectSession = async (sessionId: string) => {
    if (sessionId === "new") {
      setActiveSession(null);
      setMessages([]);
      setHasStarted(false);
      setShowHistory(false);
      return;
    }

    try {
      console.log(`📊 Selecting session: ${sessionId}`);
      const session = await chatService.getChatSessionWithMessages(sessionId);
      console.log(`📊 Session data received:`, session);

      if (session) {
        setActiveSession(session);

        if (session.messages && session.messages.length > 0) {
          console.log(`📊 Found ${session.messages.length} messages in session`);
          const formattedMessages = session.messages.map(
            (msg: any, index: number) => {
              let isBot = false;

              if (msg.role === "bot" || msg.role === "assistant") {
                isBot = true;
              } else if (msg.is_bot === true || msg.is_bot === 1) {
                isBot = true;
              } else if (msg.role === "user" && index % 2 === 1) {
                isBot = true;
              } else if (
                msg.content &&
                msg.content.length > 100 &&
                msg.role === "user"
              ) {
                isBot = true;
              }

              let messageContent =
                msg.content || msg.message_text || msg.text || "";
              const messageId =
                msg.id || msg.message_id || `msg-${Date.now()}-${index}`;

              return {
                id: messageId,
                type: (isBot ? "bot" : "user") as "bot" | "user",
                content: messageContent,
                timestamp: new Date(msg.created_at).toLocaleTimeString(),
                sessionId:
                  msg.chat_session_id || msg.conversation_id || sessionId,
              };
            }
          );

          setMessages(formattedMessages);
          setHasStarted(true);
        } else {
          setMessages([]);
          setHasStarted(false);
        }

        setShowHistory(false);
      }
    } catch (error) {
      console.error("Error loading chat session:", error);
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      const success = await chatService.deleteChatSession(sessionId);
      if (success) {
        // Remove the session from state
        setChatSessions((prev) => prev.filter((s) => s.id !== sessionId));

        // If the deleted session was active, reset the chat
        if (activeSession?.id === sessionId) {
          setActiveSession(null);
          setMessages([]);
          setHasStarted(false);
        }
      }
    } catch (error) {
      console.error("Error deleting chat session:", error);
    }
  };

  // פונקציה לעדכון title של השיחה
  const updateChatTitle = async (sessionId: string, newMessages: Message[]) => {
    try {
      // בדיקה אם כדאי לעדכן את הכותרת
      if (
        !titleGenerationService.shouldUpdateTitle(
          activeSession?.title || null,
          newMessages.length
        )
      ) {
        return;
      }

      const currentTitle = activeSession?.title || "";

      // אם הכותרת לא ברירת מחדל ויש פחות מ-6 הודעות, לא לעדכן
      if (
        !titleGenerationService.isDefaultTitle(currentTitle) &&
        newMessages.length < 6
      ) {
        return;
      }

      console.log(
        `Attempting to update title for session ${sessionId} with ${newMessages.length} messages`
      );

      // ניסיון ליצור כותרת חכמה עם AI
      let newTitle = await titleGenerationService.generateTitle(newMessages);

      // אם נכשל, ליצור כותרת פשוטה
      if (!newTitle) {
        const firstUserMessage =
          newMessages.find((msg) => msg.type === "user")?.content || "";
        newTitle = titleGenerationService.generateSimpleTitle(firstUserMessage);
      }

      console.log(`Generated new title: ${newTitle}`);

      // עדכון הכותרת בשרת
      const success = await chatService.updateChatSessionTitle(
        sessionId,
        newTitle
      );

      if (success) {
        // עדכון הכותרת ב-state המקומי
        setActiveSession((prev) =>
          prev ? { ...prev, title: newTitle } : null
        );
        setChatSessions((prev) =>
          prev.map((session) =>
            session.id === sessionId ? { ...session, title: newTitle } : session
          )
        );
        console.log(`Title updated successfully to: ${newTitle}`);
      }
    } catch (error) {
      console.error("Error updating chat title:", error);
    }
  };

  const handleEditSessionTitle = async (sessionId: string, title: string) => {
    try {
      const success = await chatService.updateChatSessionTitle(
        sessionId,
        title
      );
      if (success) {
        // Update session title in state
        setChatSessions((prev) =>
          prev.map((s) => (s.id === sessionId ? { ...s, title } : s))
        );

        // If it's the active session, update that too
        if (activeSession?.id === sessionId) {
          setActiveSession((prev) => (prev ? { ...prev, title } : null));
        }
      }
    } catch (error) {
      console.error("Error updating chat session title:", error);
    }
  };

  // Handle sending messages
  const handleSend = async () => {
    if (!input.trim()) return;

    const user = await chatService.getCurrentUser();

    if (!user) {
      setStatusMessage(
        "You are in demo mode. Messages will not be saved. Please log in to save your chats."
      );
      setTimeout(() => setStatusMessage(""), 5000);
      return;
    }

    let sessionId: string;

    if (!activeSession) {
      try {
        const initialTitle = titleGenerationService.generateSimpleTitle(
          input,
          40
        );
        const session = await chatService.createChatSession(
          user.id,
          initialTitle
        );

        if (session) {
          setChatSessions((prev) => [session, ...prev]);
          setActiveSession(session);
          sessionId = session.id;

          const userMessage: Message = {
            id: `user-${Date.now().toString()}`,
            type: "user",
            content: input,
            timestamp: new Date().toLocaleTimeString(),
            sessionId: sessionId,
          };

          setMessages([userMessage]);
          setInput("");
          setIsLoading(true);
          setHasStarted(true);

          try {
            await chatService.addMessage({
              user_id: user.id,
              chat_session_id: sessionId,
              content: userMessage.content,
              is_bot: false,
            });

            await processBotResponse(userMessage, sessionId, user.id);

            setTimeout(async () => {
              const currentMessages = [...messages, userMessage];
              await updateChatTitle(sessionId, currentMessages);
            }, 1000);
          } catch (error) {
            console.error("Error saving message:", error);
            setIsLoading(false);
          }
        }
      } catch (error) {
        console.error("Exception creating chat session:", error);
      }
    } else {
      sessionId = activeSession.id;

      const userMessage: Message = {
        id: `user-${Date.now().toString()}`,
        type: "user",
        content: input,
        timestamp: new Date().toLocaleTimeString(),
        sessionId: sessionId,
      };

      setMessages((prev) => [...prev, userMessage]);
      setInput("");
      setIsLoading(true);

      try {
        await chatService.addMessage({
          user_id: user.id,
          chat_session_id: sessionId,
          content: userMessage.content,
          is_bot: false,
        });

        await processBotResponse(userMessage, sessionId, user.id);

        setTimeout(async () => {
          const currentMessages = [...messages, userMessage];
          await updateChatTitle(sessionId, currentMessages);
        }, 1000);
      } catch (error) {
        console.error("Error saving message:", error);
        setIsLoading(false);
      }
    }
  };

  // Helper function to process bot response
  const processBotResponse = async (
    userMessage: Message,
    sessionId: string,
    userId: string
  ) => {
    try {
      // Create a placeholder bot message for streaming
      const streamingBotReply: Message = {
        id: `bot-${Date.now().toString()}`,
        type: "bot",
        content: "",
        timestamp: "", // Empty timestamp until streaming completes
        sessionId: sessionId,
      };

      // Add the placeholder message
      setMessages((prev) => [...prev, streamingBotReply]);
      let messageIndex = messages.length + 1; // Position of the bot message

      // Prepare chat history for the current session
      const chatHistory = messages.map((msg) => ({
        type: msg.type === "user" ? "user" : "bot",
        content: msg.content,
      }));

      // Use streaming service
      await chatService.sendStreamingMessage(
        userMessage.content,
        userId,
        chatHistory,

        // onChunk callback
        (chunk: string, accumulated: string) => {
          setMessages((prev) => {
            const updated = [...prev];
            const botMessageIndex = updated.findIndex(
              (msg) => msg.id === streamingBotReply.id
            );
            if (botMessageIndex >= 0) {
              updated[botMessageIndex] = {
                ...updated[botMessageIndex],
                content: accumulated,
              };
            }
            return updated;
          });
        },

        // onComplete callback
        async (fullResponse: string, sources?: any[], chunks?: number) => {
          // Update final message with timestamp when complete
          setMessages((prev) => {
            const updated = [...prev];
            const botMessageIndex = updated.findIndex(
              (msg) => msg.id === streamingBotReply.id
            );
            if (botMessageIndex >= 0) {
              updated[botMessageIndex] = {
                ...updated[botMessageIndex],
                content: fullResponse,
                timestamp: new Date().toLocaleTimeString(), // Add timestamp only when complete
              };
            }
            return updated;
          });

          // Save bot message to database
          const savedMessage = await chatService.addMessage({
            user_id: userId,
            chat_session_id: sessionId,
            content: fullResponse,
            is_bot: true,
          });

          // Reload session messages to ensure consistency
          await loadSessionMessages(sessionId);

          // Update chat title
          const updatedMessages = [
            ...messages,
            userMessage,
            {
              ...streamingBotReply,
              content: fullResponse,
            },
          ];
          await updateChatTitle(sessionId, updatedMessages);
        },

        // onError callback
        async (error: string) => {
          console.error("Streaming error:", error);
          const errorContent =
            (t("chat.errorRequest") as string) ||
            "Sorry, I encountered an error while processing your request.";

          setMessages((prev) => {
            const updated = [...prev];
            const botMessageIndex = updated.findIndex(
              (msg) => msg.id === streamingBotReply.id
            );
            if (botMessageIndex >= 0) {
              updated[botMessageIndex] = {
                ...updated[botMessageIndex],
                content: errorContent,
                timestamp: new Date().toLocaleTimeString(), // Add timestamp even for errors
              };
            }
            return updated;
          });

          // Save error message to database
          try {
            await chatService.addMessage({
              user_id: userId,
              chat_session_id: sessionId,
              content: errorContent,
              is_bot: true,
            });
          } catch (saveError) {
            console.error("Error saving error message:", saveError);
          }
        }
      );
    } catch (error) {
      console.error("Exception while processing bot response:", error);
      const errorContent =
        (t("chat.errorRequest") as string) ||
        "Sorry, I encountered an error while processing your request.";

      const botReply: Message = {
        id: `error-${Date.now().toString()}`,
        type: "bot",
        content: errorContent,
        timestamp: new Date().toLocaleTimeString(), // Show timestamp for error messages too
        sessionId: sessionId,
      };

      setMessages((prev) => [...prev, botReply]);

      // Save error message to database
      try {
        await chatService.addMessage({
          user_id: userId,
          chat_session_id: sessionId,
          content: botReply.content,
          is_bot: true,
        });
      } catch (saveError) {
        console.error("Error saving error message:", saveError);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Search chat sessions function
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
      const localResults = chatSessions.filter((session) =>
        session.title?.toLowerCase().includes(query.toLowerCase())
      );
      setFilteredChatSessions(localResults);
    }
  };

  // Search within current messages
  const searchMessages = (query: string) => {
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

  // Scroll to a specific message by index
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

  // Navigate to next/previous search result
  const navigateSearch = (direction: "next" | "prev") => {
    if (searchResults.length === 0) return;

    let newIndex;
    if (direction === "next") {
      newIndex = (currentSearchIndex + 1) % searchResults.length;
    } else {
      newIndex =
        (currentSearchIndex - 1 + searchResults.length) % searchResults.length;
    }

    setCurrentSearchIndex(newIndex);
    scrollToMessage(searchResults[newIndex]);
  };

  // Close search
  const closeSearch = () => {
    setShowSearch(false);
    setSearchQuery("");
    setSearchResults([]);
    setCurrentSearchIndex(-1);
  };

  const handleLogout = () => {
    onLogout();
  };

  return (
    <div
      className={`relative h-full w-full ${chatContainer} flex`}
      data-testid="chat-container"
    >
      {/* Status message toast */}
      {statusMessage && (
        <div className="absolute top-4 right-4 z-50 bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 rounded shadow-md max-w-md animate-fadeIn">
          <div className="flex">
            <div className="py-1">
              <svg
                className="h-6 w-6 text-yellow-500 mr-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <div>
              <p className="font-bold">Demo Mode</p>
              <p className="text-sm">{statusMessage}</p>
            </div>
          </div>
        </div>
      )}

      {/* Sidebar with navigation and chat history */}
      <div
        className={`h-full flex flex-col ${chatSidebar} w-60 overflow-hidden flex-shrink-0`}
      >
        {/* Sidebar header with logo and main actions */}
        <div
          className={`p-3 border-b ${classes.border.primary} flex items-center justify-between`}
        >
          <div
            className={`${classes.text.success} font-bold text-lg tracking-wider`}
          >
            APEX
          </div>
          <div className="flex items-center space-x-2">
            <ThemeButton
              variant="success"
              size="sm"
              onClick={() => handleSelectSession("new")}
              icon={<Plus className="w-3.5 h-3.5" />}
              title={(t("chat.history.newChat") as string) || "צ'אט חדש"}
            />
            <ThemeButton
              variant="ghost"
              size="sm"
              onClick={() => setShowSettings(true)}
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
              onChange={(e) => {
                searchChatSessions(e.target.value);
              }}
            />
            {chatSearchQuery ? (
              <button
                onClick={() => {
                  setChatSearchQuery("");
                  setFilteredChatSessions(chatSessions);
                }}
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
            onSelectSession={(session) => handleSelectSession(session.id)}
            onCreateNewSession={() => handleSelectSession("new")}
            onDeleteSession={handleDeleteSession}
            onEditSessionTitle={handleEditSessionTitle}
            activeSessionId={activeSession?.id}
            isLoading={isLoadingSessions}
          />
        </div>

        {/* Logout Button */}
        <div className="p-3 border-t border-gray-300 dark:border-gray-700">
          <button
            onClick={handleLogout}
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

      {/* Main Chat Window */}
      <div className="flex-1 flex flex-col bg-gray-50 dark:bg-black overflow-hidden">
        {!activeSession ? (
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 flex flex-col items-center justify-center">
              <h1 className="text-5xl font-light mb-8 text-gray-800 dark:text-white">
                {t("chat.noActiveSession", "ברוך הבא לצ'אטבוט אפקה!")}
              </h1>
              <p className="text-gray-500 dark:text-gray-400 mb-12 text-lg text-center mx-auto max-w-2xl leading-relaxed">
                {t(
                  "chat.startNewChatPrompt",
                  "כאן תוכלו לשאול שאלות לגבי תקנון הלימודים, נהלי הפקולטה, ומידע אחר שקשור ללימודים באפקה. התחילו שיחה חדשה כדי להתחיל!"
                )}
              </p>

              {/* Input in the center for initial screen */}
              <div className="w-full max-w-md">
                <ChatInput
                  input={input}
                  setInput={setInput}
                  onSend={handleSend}
                  isLoading={isLoading}
                  isInitial={true}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Minimal top bar like ChatGPT */}
            <div className="flex justify-center items-center py-4 flex-shrink-0">
              <div className="flex items-center space-x-4">
                <h1 className="text-lg font-medium text-gray-700 dark:text-gray-300">
                  {activeSession?.title ||
                    (t("chat.newChat") as string) ||
                    "ChatGPT"}
                </h1>

                {/* Search button - minimal style */}
                <button
                  onClick={() => setShowSearch(!showSearch)}
                  className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                  title={(t("chat.search") as string) || "Search"}
                >
                  <Search className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                </button>
              </div>
            </div>

            {/* Search bar */}
            {showSearch && (
              <div className="p-2 bg-gray-100 dark:bg-black flex items-center flex-shrink-0">
                <div className="relative flex-1 max-w-md mx-auto">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      searchMessages(e.target.value);
                    }}
                    placeholder={
                      (t("chat.searchMessages") as string) ||
                      "Search messages..."
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
                      onClick={() => navigateSearch("prev")}
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
                      onClick={() => navigateSearch("next")}
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
                      onClick={closeSearch}
                      className="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                      title={(t("chat.close") as string) || "Close"}
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            )}

            <div className="flex-1 overflow-y-auto">
              {!hasStarted ? (
                <div className="h-full flex flex-col items-center justify-center">
                  <h1 className="text-4xl font-bold mb-8 text-gray-800 dark:text-white">
                    {(t("chat.startPrompt") as string) || "Start chatting..."}
                  </h1>
                  {/* Input in the center for new chat */}
                  <div className="w-full max-w-md">
                    <ChatInput
                      input={input}
                      setInput={setInput}
                      onSend={handleSend}
                      isLoading={isLoading}
                      isInitial={true}
                    />
                  </div>
                </div>
              ) : (
                <>
                  <MessageList
                    messages={messages}
                    fontSize={fontSize}
                    highlightIndices={searchResults}
                    searchTerm={searchQuery}
                    showChunkText={false}
                  />
                  <div ref={messagesEndRef} />
                  {isLoading && (() => {
                    // Check if the last message is a bot message with content (streaming has started)
                    const lastMessage = messages[messages.length - 1];
                    const isBotStreaming = lastMessage && lastMessage.type === 'bot' && lastMessage.content.length > 0;
                    
                    // Only show "מכין תשובה" if no bot message is streaming yet
                    return !isBotStreaming && (
                      <div
                        className="max-w-3xl mx-auto px-8 py-4"
                        data-testid="typing-indicator"
                      >
                        <div className="w-full">
                          <div className="mb-6">
                            <div className="flex items-center gap-2 ml-auto w-fit">
                              <div className="flex gap-1">
                                {[...Array(3)].map((_, i) => (
                                  <div
                                    key={i}
                                    className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"
                                    style={{ animationDelay: `${i * 0.2}s` }}
                                  />
                                ))}
                              </div>
                              <div className="text-xs text-gray-500 dark:text-gray-500 opacity-60">
                                {(t("chat.preparingResponse") as string) || "מכין תשובה..."}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })()}
                </>
              )}
            </div>

            {/* Input at the bottom only when conversation has started */}
            {hasStarted && (
              <div className="p-4 flex-shrink-0">
                <ChatInput
                  input={input}
                  setInput={setInput}
                  onSend={handleSend}
                  isLoading={isLoading}
                />
              </div>
            )}
          </div>
        )}
      </div>

      {/* Settings Panel - Clean & Minimal with Green Accent */}
      {showSettings && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <ThemeCard className="w-full max-w-md" shadow="lg" padding="none">
            {/* Header */}
            <div
              className={`flex items-center justify-between p-6 border-b ${classes.border.primary}`}
            >
              <div className="flex items-center space-x-3">
                <div
                  className={`w-10 h-10 rounded-xl ${classes.bg.tertiary} flex items-center justify-center`}
                >
                  <svg
                    className={`w-5 h-5 ${classes.text.success}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                  </svg>
                </div>
                <div>
                  <h2
                    className={`text-xl font-semibold ${classes.text.primary}`}
                  >
                    {i18n.language === "he" ? "הגדרות" : "Settings"}
                  </h2>
                  <p className={`text-sm ${classes.text.secondary}`}>
                    {i18n.language === "he" ? "התאמה אישית" : "Customize"}
                  </p>
                </div>
              </div>
              <ThemeButton
                variant="ghost"
                size="sm"
                onClick={() => setShowSettings(false)}
                icon={
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
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                }
              />
            </div>

            {/* Content */}
            <div className="p-6">
              <UserSettings onClose={() => setShowSettings(false)} />
            </div>
          </ThemeCard>
        </div>
      )}
    </div>
  );
};

export default ChatWindow;
