import { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import chatService, { ChatSession } from '../../../services/chatService';
import titleGenerationService from '../../../services/titleGenerationService';
import { Message, formatMessages } from '../utils/messageFormatter';

interface UseChatMessagesProps {
  activeSession: ChatSession | null;
  setChatSessions: React.Dispatch<React.SetStateAction<ChatSession[]>>;
  setActiveSession: (session: ChatSession | null) => void;
  updateChatTitle: (sessionId: string, messages: Message[]) => Promise<void>;
}

interface UseChatMessagesReturn {
  messages: Message[];
  input: string;
  isLoading: boolean;
  hasStarted: boolean;
  statusMessage: string;
  messagesEndRef: React.RefObject<HTMLDivElement>;
  setInput: (value: string) => void;
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  setHasStarted: (value: boolean) => void;
  setStatusMessage: (message: string) => void;
  handleSend: () => Promise<void>;
  loadSessionMessages: (sessionId: string) => Promise<void>;
}

export function useChatMessages({
  activeSession,
  setChatSessions,
  setActiveSession,
  updateChatTitle,
}: UseChatMessagesProps): UseChatMessagesReturn {
  const { t } = useTranslation();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load messages when active session changes
  useEffect(() => {
    if (activeSession && activeSession.messages) {
      const formattedMessages = formatMessages(activeSession.messages, activeSession.id);
      setMessages(formattedMessages);
      setHasStarted(formattedMessages.length > 0);
    } else if (!activeSession) {
      setMessages([]);
      setHasStarted(false);
    }
  }, [activeSession]);

  const loadSessionMessages = async (sessionId: string) => {
    try {
      const session = await chatService.getChatSessionWithMessages(sessionId);

      if (session && session.messages && session.messages.length > 0) {
        const formattedMessages = formatMessages(session.messages, sessionId);
        setMessages(formattedMessages);
        setHasStarted(formattedMessages.length > 0);
      } else {
        setMessages([]);
        setHasStarted(false);
      }
    } catch (error) {
      console.error("Error reloading session messages:", error);
    }
  };

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
        const initialTitle = titleGenerationService.generateSimpleTitle(input, 40);
        const session = await chatService.createChatSession(user.id, initialTitle);

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

  const processBotResponse = async (
    userMessage: Message,
    sessionId: string,
    userId: string
  ) => {
    try {
      const streamingBotReply: Message = {
        id: `bot-${Date.now().toString()}`,
        type: "bot",
        content: "",
        timestamp: "",
        sessionId: sessionId,
      };

      setMessages((prev) => [...prev, streamingBotReply]);

      const chatHistory = messages.map((msg) => ({
        type: msg.type === "user" ? "user" : "bot",
        content: msg.content,
      }));

      await chatService.sendStreamingMessage(
        userMessage.content,
        userId,
        chatHistory,

        // onChunk callback
        (_chunk: string, accumulated: string) => {
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
        async (fullResponse: string, _sources?: any[], _chunks?: number) => {
          setMessages((prev) => {
            const updated = [...prev];
            const botMessageIndex = updated.findIndex(
              (msg) => msg.id === streamingBotReply.id
            );
            if (botMessageIndex >= 0) {
              updated[botMessageIndex] = {
                ...updated[botMessageIndex],
                content: fullResponse,
                timestamp: new Date().toLocaleTimeString(),
              };
            }
            return updated;
          });

          await chatService.addMessage({
            user_id: userId,
            chat_session_id: sessionId,
            content: fullResponse,
            is_bot: true,
          });

          // Small delay to ensure database transaction completes before reloading
          setTimeout(async () => {
            await loadSessionMessages(sessionId);
          }, 500);

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
                timestamp: new Date().toLocaleTimeString(),
              };
            }
            return updated;
          });

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
        timestamp: new Date().toLocaleTimeString(),
        sessionId: sessionId,
      };

      setMessages((prev) => [...prev, botReply]);

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

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return {
    messages,
    input,
    isLoading,
    hasStarted,
    statusMessage,
    messagesEndRef,
    setInput,
    setMessages,
    setHasStarted,
    setStatusMessage,
    handleSend,
    loadSessionMessages,
  };
} 