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
} from "lucide-react";
import SettingsPanel from "./SettingsPanel";
import { API_CONFIG } from "../../config/constants";
import UserSettings from "../Settings/UserSettings";
import chatService, { ChatSession } from "../../services/chatService";
import titleGenerationService from "../../services/titleGenerationService";
import { useTranslation } from "react-i18next";
import { supabase } from "../../config/supabase";

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
  theme?: "dark" | "light";
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  onLogout,
  theme: parentTheme,
}) => {
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
  const theme = parentTheme || "dark"; // Use parent theme or fallback to dark
  const [hasStarted, setHasStarted] = useState(false);
  const [fontSize, setFontSize] = useState(14);
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

  // Theme is now managed by parent component

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

  // Helper function to load session messages
  const loadSessionMessages = async (sessionId: string) => {
    try {
      console.log("Reloading session messages for session:", sessionId);
      const session = await chatService.getChatSessionWithMessages(sessionId);

      if (session && session.messages && session.messages.length > 0) {
        console.log(`Successfully loaded ${session.messages.length} messages`);
        console.log(
          "First message structure example:",
          JSON.stringify(session.messages[0])
        );

        // המר את ההודעות למבנה הנכון עבור ממשק המשתמש
        const formattedMessages = session.messages.map((msg: any) => {
          // קביעת תוכן ההודעה - יכול להיות ב-content, request או response
          let messageContent = "";
          let isBot = !!msg.is_bot;

          // בדיקה אם יש לנו הודעת משתמש/בוט לפי שדות request/response
          if (msg.request && msg.request.trim() !== "") {
            messageContent = msg.request;
            isBot = false;
          } else if (msg.response && msg.response.trim() !== "") {
            messageContent = msg.response;
            isBot = true;
          } else if (msg.content) {
            messageContent = msg.content;
          } else if (msg.message_text) {
            messageContent = msg.message_text;
          } else if (msg.text) {
            messageContent = msg.text;
          }

          // יצירת מזהה ייחודי אם חסר
          const messageId = msg.id || msg.message_id || `msg-${Date.now()}`;

          console.log(
            `Message ${messageId} content source:`,
            msg.request
              ? "request"
              : msg.response
              ? "response"
              : msg.content
              ? "content"
              : "other",
            "is_bot:",
            isBot
          );

          return {
            id: messageId,
            type: (isBot ? "bot" : "user") as "bot" | "user",
            content: messageContent,
            timestamp: new Date(msg.created_at).toLocaleTimeString(),
            sessionId: msg.chat_session_id || msg.conversation_id || sessionId,
          };
        });

        console.log(
          "Formatted messages for display:",
          formattedMessages.length
        );
        console.log(
          "Message types count:",
          "bot:",
          formattedMessages.filter((m) => m.type === "bot").length,
          "user:",
          formattedMessages.filter((m) => m.type === "user").length
        );

        // עדכן את מצב ההודעות בממשק
        setMessages(formattedMessages);
        setHasStarted(formattedMessages.length > 0);
      } else {
        console.log("No messages found in session or session is empty");
      }
    } catch (error) {
      console.error("Error reloading session messages:", error);
    }
  };

  const handleSelectSession = async (sessionId: string) => {
    // If 'new' is passed, it's a request to start a new chat
    if (sessionId === "new") {
      setActiveSession(null);
      setMessages([]);
      setHasStarted(false);
      setShowHistory(false);
      return;
    }

    try {
      console.log("Loading session with ID:", sessionId);
      const session = await chatService.getChatSessionWithMessages(sessionId);

      if (session) {
        console.log("Session loaded successfully:", session);
        console.log("Messages count:", session.messages?.length || 0);

        if (session.messages && session.messages.length > 0) {
          console.log(
            "First message structure example:",
            JSON.stringify(session.messages[0])
          );
        }

        setActiveSession(session);

        if (session.messages && session.messages.length > 0) {
          // המר את ההודעות למבנה הנכון עבור ממשק המשתמש
          const formattedMessages = session.messages.map((msg: any) => {
            // קביעת תוכן ההודעה - יכול להיות ב-content, request או response
            let messageContent = "";
            let isBot = !!msg.is_bot;

            // בדיקה אם יש לנו הודעת משתמש/בוט לפי שדות request/response
            if (msg.request && msg.request.trim() !== "") {
              messageContent = msg.request;
              isBot = false;
            } else if (msg.response && msg.response.trim() !== "") {
              messageContent = msg.response;
              isBot = true;
            } else if (msg.content) {
              messageContent = msg.content;
            } else if (msg.message_text) {
              messageContent = msg.message_text;
            } else if (msg.text) {
              messageContent = msg.text;
            }

            // יצירת מזהה ייחודי אם חסר
            const messageId = msg.id || msg.message_id || `msg-${Date.now()}`;

            console.log(
              `Message ${messageId} content source:`,
              msg.request
                ? "request"
                : msg.response
                ? "response"
                : msg.content
                ? "content"
                : "other",
              "is_bot:",
              isBot
            );

            return {
              id: messageId,
              type: (isBot ? "bot" : "user") as "bot" | "user",
              content: messageContent,
              timestamp: new Date(msg.created_at).toLocaleTimeString(),
              sessionId:
                msg.chat_session_id || msg.conversation_id || sessionId,
            };
          });

          console.log("Formatted messages:", formattedMessages.length);
          console.log(
            "Message types count:",
            "bot:",
            formattedMessages.filter((m) => m.type === "bot").length,
            "user:",
            formattedMessages.filter((m) => m.type === "user").length
          );

          setMessages(formattedMessages);
          setHasStarted(true);
        } else {
          console.log("No messages found in session");
          setMessages([]);
          setHasStarted(false);
        }

        setShowHistory(false); // Hide history after selecting a chat
      } else {
        console.error("Failed to load session, session is null");
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
    console.clear(); // Clear the console to make debugging easier
    console.log("=== Starting handleSend with input ===", input);

    if (!input.trim()) {
      console.log("Empty input, nothing to send");
      return;
    }

    // Try to get current user
    const user = await chatService.getCurrentUser();
    console.log(
      "Current user:",
      user ? `${user.id} (logged in)` : "not logged in"
    );

    if (!user) {
      console.log("No user logged in - using demo mode");
      setStatusMessage(
        "You are in demo mode. Messages will not be saved. Please log in to save your chats."
      );
      setTimeout(() => setStatusMessage(""), 5000);
      return; // Return early for now to focus on user logged in case
    }

    let sessionId: string;

    // Create a new session if none exists
    if (!activeSession) {
      console.log("No active session, creating new chat session...");
      try {
        // יצירת כותרת ראשונית בהתבסס על ההודעה הראשונה
        const initialTitle = titleGenerationService.generateSimpleTitle(
          input,
          40
        );
        console.log("Attempting to create session with title:", initialTitle);

        const session = await chatService.createChatSession(
          user.id,
          initialTitle
        );
        console.log("Session creation response:", session);

        if (session) {
          console.log("Chat session created successfully:", session.id);
          setChatSessions((prev) => [session, ...prev]);
          setActiveSession(session);
          sessionId = session.id;

          // Create user message
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

          // Save user message to database
          try {
            const savedMessage = await chatService.addMessage({
              user_id: user.id,
              chat_session_id: sessionId,
              content: userMessage.content,
              is_bot: false,
            });

            console.log("User message saved successfully:", savedMessage?.id);

            // Call API for bot response
            await processBotResponse(userMessage, sessionId, user.id);

            // עדכון title לאחר השלמת השיחה הראשונה
            setTimeout(async () => {
              const currentMessages = [...messages, userMessage];
              await updateChatTitle(sessionId, currentMessages);
            }, 1000);
          } catch (error) {
            console.error("Error saving message:", error);
            setIsLoading(false);
          }
        } else {
          console.error(
            "Failed to create chat session - session response is null"
          );
        }
      } catch (error) {
        console.error("Exception creating chat session:", error);
      }
    } else {
      // Use existing session
      sessionId = activeSession.id;
      console.log("Using existing chat session:", sessionId);

      // Create user message
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

      // Save user message to database
      try {
        const savedMessage = await chatService.addMessage({
          user_id: user.id,
          chat_session_id: sessionId,
          content: userMessage.content,
          is_bot: false,
        });

        console.log("User message saved successfully:", savedMessage?.id);

        // Call API for bot response
        await processBotResponse(userMessage, sessionId, user.id);

        // עדכון title לאחר הוספת הודעה לשיחה קיימת
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
      // Check if user is authenticated for full RAG, otherwise use demo endpoint
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const BACKEND_URL =
        import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

      let response;

      // Prepare chat history for the current session
      const chatHistory = messages.map((msg) => ({
        type: msg.type === "user" ? "user" : "bot",
        content: msg.content,
      }));

      if (session && session.access_token) {
        // User is authenticated - use full chat endpoint with history
        console.log("Using authenticated chat endpoint with history");
        console.log("Sending chat history:", chatHistory.length, "messages");
        response = await fetch(`${BACKEND_URL}/api/chat`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${session.access_token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: userMessage.content,
            user_id: userId,
            history: chatHistory,
          }),
          signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT),
        });
      } else {
        // User not authenticated - use demo endpoint (no auth required)
        console.log("Using demo RAG endpoint (no auth)");
        response = await fetch(`${BACKEND_URL}/api/chat/demo`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: userMessage.content,
          }),
          signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT),
        });
      }

      let botContent = "";
      let chunkText = "";

      if (response.ok) {
        const data = await response.json();
        console.log("Chat API response:", data);

        // Handle different response formats based on endpoint
        if (session && session.access_token) {
          // Authenticated endpoint returns { response, sources, chunks }
          botContent =
            data.response ||
            (t("chat.errorProcessing") as string) ||
            "Sorry, I couldn't process your request.";
        } else {
          // Demo endpoint returns { answer, response, chunkText }
          botContent =
            data.answer ||
            data.response ||
            (t("chat.errorProcessing") as string) ||
            "Sorry, I couldn't process your request.";
          chunkText = data.chunkText || "";
        }
      } else {
        console.error("Chat API error:", response.status, response.statusText);
        botContent =
          (t("chat.errorRequest") as string) ||
          "Sorry, I encountered an error while processing your request.";
      }

      // Create bot reply
      const botReply: Message = {
        id: `bot-${Date.now().toString()}`,
        type: "bot",
        content: botContent,
        timestamp: new Date().toLocaleTimeString(),
        sessionId: sessionId,
        chunkText: chunkText,
      };

      setMessages((prev) => [...prev, botReply]);

      // Save bot message to database
      const savedMessage = await chatService.addMessage({
        user_id: userId, // Ensure userId is passed correctly
        chat_session_id: sessionId,
        content: botContent, // Ensure botContent has a value
        is_bot: true,
      });

      // if (savedMessage) {
      //   console.log('Bot message saved successfully:', savedMessage.id);
      // } else {
      //   console.warn('Bot message was not saved, addMessage returned null or undefined');
      // }

      await loadSessionMessages(sessionId);

      // עדכון title של השיחה לאחר הוספת הודעה חדשה
      const updatedMessages = [...messages, userMessage, botReply];
      await updateChatTitle(sessionId, updatedMessages);
    } catch (error) {
      console.error("Exception while processing bot response:", error);
      const errorContent =
        (t("chat.errorRequest") as string) ||
        "Sorry, I encountered an error while processing your request.";
      const botReply: Message = {
        id: `error-${Date.now().toString()}`,
        type: "bot",
        content: errorContent,
        timestamp: new Date().toLocaleTimeString(),
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
    <div className="relative h-full w-full bg-gray-50 dark:bg-black text-gray-900 dark:text-white flex">
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
      <div className="h-full border-l dark:border-gray-800 flex flex-col bg-gray-50 dark:bg-black w-60 overflow-hidden flex-shrink-0">
        {/* Sidebar header with logo and main actions */}
        <div className="p-3 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
          <div className="text-green-700 dark:text-green-500 font-bold text-lg tracking-wider">
            APEX
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleSelectSession("new")}
              className="p-1.5 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-1 focus:ring-green-500"
              title={(t("chat.history.newChat") as string) || "צ'אט חדש"}
            >
              <Plus className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setShowSettings(true)}
              className="p-1.5 rounded-full hover:bg-gray-200 dark:hover:bg-gray-800"
              title={(t("chat.sidebar.settings") as string) || "Settings"}
            >
              <Settings className="w-4 h-4 text-gray-700 dark:text-gray-300" />
            </button>
          </div>
        </div>

        {/* Search input */}
        <div className="px-3 py-2 border-b border-gray-200 dark:border-gray-800">
          <div className="relative">
            <input
              type="text"
              placeholder={(t("chat.history.search") as string) || "Search..."}
              className="w-full px-2 py-1.5 pr-7 text-xs rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-green-500"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                searchMessages(e.target.value);
              }}
            />
            {searchQuery ? (
              <button
                onClick={() => setSearchQuery("")}
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
            sessions={chatSessions}
            onSelectSession={(session) => handleSelectSession(session.id)}
            onCreateNewSession={() => handleSelectSession("new")}
            onDeleteSession={handleDeleteSession}
            onEditSessionTitle={handleEditSessionTitle}
            activeSessionId={activeSession?.id}
            isLoading={isLoadingSessions}
          />
        </div>

        {/* Logout Button */}
        <div className="p-3 border-t border-gray-200 dark:border-gray-800">
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
              <h1 className="text-3xl font-bold mb-6 text-gray-800 dark:text-white">
                {t("chat.noActiveSession", "ברוך הבא לצ'אטבוט אפקה!")}
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mb-6 text-xl text-center mx-auto max-w-2xl">
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
            {/* Top bar */}
            <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-800 flex-shrink-0">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold text-gray-800 dark:text-white">
                  {activeSession?.title ||
                    (t("chat.newChat") as string) ||
                    "New Chat"}
                </h1>
              </div>

              <div className="flex items-center space-x-2">
                {/* Search button */}
                <button
                  onClick={() => setShowSearch(!showSearch)}
                  className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-800"
                  title={(t("chat.search") as string) || "Search"}
                >
                  <Search className="h-5 w-5 text-gray-700 dark:text-gray-300" />
                </button>
              </div>
            </div>

            {/* Search bar */}
            {showSearch && (
              <div className="p-2 bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center flex-shrink-0">
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
                  {isLoading && (
                    <div className="p-4 flex items-center gap-2">
                      <div className="flex space-x-1">
                        {[...Array(3)].map((_, i) => (
                          <div
                            key={i}
                            className="w-1.5 h-1.5 bg-green-700 dark:bg-green-500 rounded-full animate-bounce"
                            style={{ animationDelay: `${i * 0.2}s` }}
                          />
                        ))}
                      </div>
                      <span className="text-sm text-green-700 dark:text-green-500">
                        {(t("chat.processing") as string) || "Processing..."}
                      </span>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Input at the bottom only when conversation has started */}
            {hasStarted && (
              <div className="p-4 border-t border-gray-200 dark:border-gray-800 flex-shrink-0">
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
          <div className="bg-white dark:bg-black rounded-2xl shadow-2xl w-full max-w-md border border-slate-200 dark:border-gray-800">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-gray-800">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-green-50 dark:bg-green-900/20 flex items-center justify-center">
                  <svg
                    className="w-5 h-5 text-green-600 dark:text-green-400"
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
                  <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                    {i18n.language === "he" ? "הגדרות" : "Settings"}
                  </h2>
                  <p className="text-sm text-slate-500 dark:text-gray-400">
                    {i18n.language === "he" ? "התאמה אישית" : "Customize"}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowSettings(false)}
                className="w-8 h-8 rounded-lg hover:bg-slate-100 dark:hover:bg-gray-800 flex items-center justify-center transition-colors"
              >
                <svg
                  className="w-4 h-4 text-slate-400"
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
              </button>
            </div>

            {/* Content */}
            <div className="p-6">
              <UserSettings
                onClose={() => setShowSettings(false)}
                theme={theme}
                onThemeChange={() => {}} // Theme is controlled by parent
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWindow;
