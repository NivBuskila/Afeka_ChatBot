import React, { useState, useEffect, useRef } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import { Terminal, History, Settings, LogOut, Calendar, Trash2, ChevronUp, ChevronDown, Pencil, Delete } from 'lucide-react';
import SettingsPanel from './SettingsPanel';
import { useNavigate } from 'react-router-dom';
import { API_CONFIG } from '../../config/constants';
import { useTranslation } from 'react-i18next';
import UserSettings from '../Settings/UserSettings';
import { supabase } from '../../supabase/client';
import { v4 as uuidv4 } from 'uuid';

interface Message {
  id: number;
  type: 'user' | 'bot';
  content: string;
  timestamp: string;
}

interface Conversation {
  id: string;
  title: string;
  date: Date;
  messageCount?: number;
}

interface ChatWindowProps {
  onLogout: () => void;
}

// Group conversations by date
const groupConversations = (conversations: Conversation[]) => {
  const today = new Date().toLocaleDateString();
  const yesterday = new Date(Date.now() - 86400000).toLocaleDateString();

  return {
    today: conversations.filter(conv => conv.date.toLocaleDateString() === today),
    yesterday: conversations.filter(conv => conv.date.toLocaleDateString() === yesterday),
    previous: conversations.filter(conv => {
      const dateStr = conv.date.toLocaleDateString();
      return dateStr !== today && dateStr !== yesterday;
    }),
  };
};

const ChatWindow: React.FC<ChatWindowProps> = ({ onLogout }) => {
  const navigate = useNavigate();
  const { i18n } = useTranslation();
  const isRTL = i18n.language === 'he';
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [hasStarted, setHasStarted] = useState(false);
  const [fontSize, setFontSize] = useState(14);
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const actionsMenuRef = useRef<HTMLDivElement>(null);
  const menuPositionRefs = useRef<Map<string, DOMRect>>(new Map());
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const [activeButtonRect, setActiveButtonRect] = useState<DOMRect | null>(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [settings] = useState({
    systemPrompt: "You are a helpful assistant.",
    model: "gemini-pro"
  });
  const [user, setUser] = useState<any>(null);

  // חשוב: רק הגדרה אחת של activeConversation ושיחות
  const [activeConversation, setActiveConversation] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);

  // חשוב: רק הגדרה אחת של groupedConversations
  const [groupedConversations, setGroupedConversations] = useState<{
    today: Conversation[],
    yesterday: Conversation[],
    previous: Conversation[]
  }>({
    today: [],
    yesterday: [],
    previous: []
  });

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  // Automatically expand sidebar when showing history
  useEffect(() => {
    if (showHistory) {
      setIsExpanded(true);
    }
  }, [showHistory]);

  useEffect(() => {
    const getCurrentUser = async () => {
      const { data } = await supabase.auth.getUser();
      setUser(data.user);
    };
    getCurrentUser();
  }, []);

  const handleSend = async (message: string) => {
    if (!message.trim() || isLoading) return;

    setIsLoading(true);

    // Create user message
    const userMessage: Message = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };

    // Update messages state with user message
    setMessages(prev => [...prev, userMessage]);

    try {
      // Handle conversation creation or retrieval
      let currentConversationId = activeConversation;

      if (!currentConversationId && user) {
        // Create new conversation
        const { data: newConvData, error: convError } = await supabase.rpc(
          'create_conversation',
          {
            user_id: user?.id || 'anonymous',
            title: message.slice(0, 50),
            system_prompt: settings.systemPrompt
          }
        );

        if (convError) {
          console.error('Error creating conversation:', convError);
          throw new Error('Failed to create conversation');
        }

        currentConversationId = newConvData;
        const newConversation: Conversation = {
          id: currentConversationId || '',
          title: message.slice(0, 50),
          date: new Date(),
          messageCount: 0
        };

        setActiveConversation(currentConversationId);
        setConversations(prev => [newConversation, ...prev]);
      }

      // Add message to database if user is authenticated
      if (user && currentConversationId) {
        const { error: msgError } = await supabase.rpc(
          'add_message',
          {
            conversation_id: currentConversationId,
            user_id: user?.id || 'anonymous',
            content: message,
            role: 'user'
          }
        );

        if (msgError) {
          console.error('Error adding user message:', msgError);
        }
      }

      // Send to API - שימוש בכתובת מוחלטת
      const apiUrl = 'http://localhost:8000/api/chat';
      console.log('Sending request to:', apiUrl);

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          conversation_id: currentConversationId || '',
          model: settings.model
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // Create bot reply
      const botReply: Message = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.response || 'Sorry, I could not process your request.',
        timestamp: new Date().toISOString(),
      };

      // Update messages state with bot reply
      setMessages(prev => [...prev, botReply]);

      // Add bot message to database if user is authenticated and conversation exists
      if (user && currentConversationId) {
        const { error: botMsgError } = await supabase.rpc(
          'add_message',
          {
            conversation_id: currentConversationId,
            user_id: user?.id || 'anonymous',
            content: botReply.content,
            role: 'assistant'
          }
        );

        if (botMsgError) {
          console.error('Error adding bot message:', botMsgError);
        }
      }

    } catch (error) {
      console.error('Error sending message:', error);

      // Create error bot reply
      const errorReply: Message = {
        id: Date.now() + 2,
        type: 'bot',
        content: 'Sorry, there was an error processing your request. Please try again later.',
        timestamp: new Date().toISOString(),
      };

      // Update messages with error
      setMessages(prev => [...prev, errorReply]);
    } finally {
      setIsLoading(false);
      setInput('');
    }
  };

  const handleSelectConversation = async (id: string) => {
    try {
      setIsLoading(true);
      setActiveConversation(id);
      setShowHistory(false);

      // Clear current messages
      setMessages([]);

      // Fetch messages for this conversation
      const { data, error } = await supabase.rpc('get_conversation_messages', {
        p_conversation_id: id,
        p_limit: 100,
        p_offset: 0
      });

      if (error) throw error;

      // Convert to our Message format
      if (data && data.length > 0) {
        const loadedMessages: Message[] = [];

        data.forEach((msg: any, index: number) => {
          if (msg.request) {
            loadedMessages.push({
              id: (index * 2) + Date.now(),
              type: 'user',
              content: msg.request,
              timestamp: new Date(msg.created_at).toLocaleTimeString(),
            });
          }

          if (msg.response) {
            loadedMessages.push({
              id: (index * 2 + 1) + Date.now(),
              type: 'bot',
              content: msg.response,
              timestamp: new Date(msg.created_at).toLocaleTimeString(),
            });
          }
        });

        setMessages(loadedMessages);
        setHasStarted(true);
      }
    } catch (error) {
      console.error('Error loading conversation:', error);
      alert(i18n.language === 'he' ? 'שגיאה בטעינת השיחה' : 'Error loading conversation');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleHistory = () => {
    setShowHistory(prev => !prev);
  };

  const handleClearHistory = () => {
    // For demonstration purposes only - in real app this would make an API call
    if (window.confirm(i18n.language === 'he' ? 'האם אתה בטוח שברצונך למחוק את כל היסטוריית השיחות?' : 'Are you sure you want to clear all conversation history?')) {
      setConversations([]);
      setShowHistory(false);
    }
  };

  const handleLogout = () => {
    onLogout();
  };

  const handleRenameConversation = (id: string) => {
    console.log("Rename conversation called with ID:", id);
    const newTitle = window.prompt(
      i18n.language === 'he'
        ? 'הזן שם חדש לשיחה:'
        : 'Enter a new name for this conversation:'
    );

    if (newTitle?.trim()) {
      console.log("Setting new title:", newTitle);
      setConversations(prev =>
        prev.map(conv =>
          conv.id === id
            ? { ...conv, title: newTitle.trim() }
            : conv
        )
      );
    }
  };

  const handleDeleteConversation = (id: string) => {
    console.log("Delete conversation called with ID:", id);
    const shouldDelete = window.confirm(
      i18n.language === 'he'
        ? 'האם אתה בטוח שברצונך למחוק את השיחה הזו?'
        : 'Are you sure you want to delete this conversation?'
    );

    if (shouldDelete) {
      console.log("Confirmed deletion");
      setConversations(prev => prev.filter(conv => conv.id !== id));
    }
  };

  // Fetch conversation list on component mount
  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) return;

        const { data, error } = await supabase.rpc('get_user_conversations', {
          p_user_id: user.id,
          p_limit: 50,
          p_offset: 0
        });

        if (error) throw error;

        const today = new Date().toLocaleDateString();
        const yesterday = new Date(Date.now() - 86400000).toLocaleDateString();

        if (data && data.length > 0) {
          // Group conversations by date
          const conversationsByDate = data.reduce((acc: Record<string, any[]>, conv: any) => {
            const date = new Date(conv.created_at).toLocaleDateString();
            if (!acc[date]) {
              acc[date] = [];
            }
            acc[date].push({
              id: conv.conversation_id,
              title: conv.title || `Conversation ${conv.conversation_id.substring(0, 8)}`,
              date: new Date(conv.created_at),
              messageCount: conv.message_count || 0,
            });
            return acc;
          }, {});

          const conversationsList = data.map((conv: any) => ({
            id: conv.conversation_id,
            title: conv.title || `Conversation ${conv.conversation_id.substring(0, 8)}`,
            date: new Date(conv.created_at),
            messageCount: conv.message_count || 0,
          }));

          setConversations(conversationsList);

          // עדכון קבוצות השיחות
          setGroupedConversations({
            today: conversationsByDate[today] || [],
            yesterday: conversationsByDate[yesterday] || [],
            previous: Object.keys(conversationsByDate)
              .filter(date => date !== today && date !== yesterday)
              .reduce((acc: any[], date) => [...acc, ...conversationsByDate[date]], []),
          });
        }
      } catch (error) {
        console.error('Error fetching conversations:', error);
      }
    };

    fetchConversations();
  }, []);

  const handleClear = () => {
    setInput('');
  };

  const language = i18n.language === 'he' ? 'he' : 'en';

  return (
    <div className="relative h-full w-full bg-gray-50 dark:bg-black text-gray-900 dark:text-white overflow-hidden">
      <div className="relative h-full flex z-10">
        {/* Sidebar */}
        <div
          className={`flex-shrink-0 bg-gray-100 dark:bg-black backdrop-blur-xl transform transition-all duration-300 ${isExpanded ? `${showHistory ? 'w-80' : 'w-64'} p-4` : 'w-16 py-4 px-2'
            } border-r border-gray-200 dark:border-gray-800 flex flex-col overflow-hidden z-30`}
          onMouseEnter={() => setIsExpanded(true)}
          onMouseLeave={() => !showHistory && setIsExpanded(false)}
        >
          <div className={`${isExpanded ? 'mb-6 text-center px-4' : 'mb-6 flex justify-center'}`}>
            {isExpanded ? (
              <>
                <div className="text-green-700 dark:text-green-500 font-bold text-3xl tracking-wider mb-1">APEX</div>
                <div className="text-[10px] text-green-700/70 dark:text-green-500/70 tracking-wide">
                  AFEKA Engineering AI
                </div>
              </>
            ) : (
              <div className="text-green-700 dark:text-green-500 font-bold text-lg tracking-wider">APEX</div>
            )}
          </div>

          <div className={`space-y-2 ${isExpanded ? 'px-1' : 'px-0'}`}>
            <button
              onClick={() => {
                setShowHistory(false);
              }}
              className={`w-full flex items-center transition-all ${isExpanded
                ? 'p-2 gap-3 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800'
                : 'justify-center py-1'
                }`}
            >
              <div className="relative">
                <Terminal className="w-5 h-5 text-green-700 dark:text-green-500" />
              </div>
              {isExpanded && (
                <span className="text-sm text-gray-700 dark:text-gray-200">
                  Chat
                </span>
              )}
            </button>

            <button
              onClick={toggleHistory}
              className={`w-full flex items-center transition-all ${isExpanded
                ? 'p-2 gap-3 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800'
                : 'justify-center py-1'
                } ${showHistory ? 'bg-gray-200 dark:bg-gray-800' : ''}`}
            >
              <div className="relative">
                <History className={`w-5 h-5 ${showHistory ? 'text-green-600 dark:text-green-400' : 'text-green-700 dark:text-green-500'}`} />
              </div>
              {isExpanded && (
                <span className={`text-sm ${showHistory ? 'text-gray-800 dark:text-gray-50 font-medium' : 'text-gray-700 dark:text-gray-200'}`}>
                  History
                </span>
              )}
            </button>

            {/* Conversation History Section - moved to appear directly after History button */}
            {showHistory && isExpanded && (
              <div className="mt-1 mb-2 flex-col overflow-hidden">
                <div className="overflow-y-auto max-h-[50vh] px-1">
                  {conversations.length === 0 ? (
                    <div className="text-center py-4 text-gray-500 dark:text-gray-400 text-xs">
                      {isRTL ? 'אין שיחות קודמות להצגה' : 'No previous conversations to display'}
                    </div>
                  ) : (
                    <div className="pt-1">
                      {/* Today's conversations */}
                      {groupedConversations.today.length > 0 && (
                        <div>
                          <div className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase py-1.5">
                            {isRTL ? 'היום' : 'Today'}
                          </div>
                          {groupedConversations.today.map(conversation => (
                            <div key={conversation.id} className="relative group">
                              <div className="flex justify-between items-center">
                                <button
                                  className="w-full text-left py-1.5 px-1 rounded hover:bg-gray-200/50 dark:hover:bg-gray-800/50 transition-colors flex-grow"
                                  onClick={() => handleSelectConversation(conversation.id)}
                                >
                                  <div className="text-sm text-gray-800 dark:text-white font-medium line-clamp-1 pr-7">
                                    {conversation.title}
                                  </div>
                                </button>
                                <div className="flex items-center">
                                  <button
                                    className="p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                    onClick={() => handleRenameConversation(conversation.id)}
                                    title={isRTL ? 'שנה שם' : 'Rename'}
                                  >
                                    <Pencil className="w-4 h-4 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300" />
                                  </button>
                                  <button
                                    className="p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                    onClick={() => handleDeleteConversation(conversation.id)}
                                    title={isRTL ? 'מחק' : 'Delete'}
                                  >
                                    <Delete className="w-4 h-4 text-red-500 hover:text-red-600 dark:text-red-400 dark:hover:text-red-300" />
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Yesterday's conversations */}
                      {groupedConversations.yesterday.length > 0 && (
                        <div className="mt-1">
                          <div className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase py-1.5">
                            {isRTL ? 'אתמול' : 'Yesterday'}
                          </div>
                          {groupedConversations.yesterday.map(conversation => (
                            <div key={conversation.id} className="relative group">
                              <div className="flex justify-between items-center">
                                <button
                                  className="w-full text-left py-1.5 px-1 rounded hover:bg-gray-200/50 dark:hover:bg-gray-800/50 transition-colors flex-grow"
                                  onClick={() => handleSelectConversation(conversation.id)}
                                >
                                  <div className="text-sm text-gray-800 dark:text-white font-medium line-clamp-1 pr-7">
                                    {conversation.title}
                                  </div>
                                </button>
                                <div className="flex items-center">
                                  <button
                                    className="p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                    onClick={() => handleRenameConversation(conversation.id)}
                                    title={isRTL ? 'שנה שם' : 'Rename'}
                                  >
                                    <Pencil className="w-4 h-4 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300" />
                                  </button>
                                  <button
                                    className="p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                    onClick={() => handleDeleteConversation(conversation.id)}
                                    title={isRTL ? 'מחק' : 'Delete'}
                                  >
                                    <Delete className="w-4 h-4 text-red-500 hover:text-red-600 dark:text-red-400 dark:hover:text-red-300" />
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Previous conversations */}
                      {groupedConversations.previous.length > 0 && (
                        <div className="mt-1">
                          <div className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase py-1.5">
                            {isRTL ? '7 ימים אחרונים' : 'Previous 7 Days'}
                          </div>
                          {groupedConversations.previous.map(conversation => (
                            <div key={conversation.id} className="relative group">
                              <div className="flex justify-between items-center">
                                <button
                                  className="w-full text-left py-1.5 px-1 rounded hover:bg-gray-200/50 dark:hover:bg-gray-800/50 transition-colors flex-grow"
                                  onClick={() => handleSelectConversation(conversation.id)}
                                >
                                  <div className="text-sm text-gray-800 dark:text-white font-medium line-clamp-1 pr-7">
                                    {conversation.title}
                                  </div>
                                </button>
                                <div className="flex items-center">
                                  <button
                                    className="p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                    onClick={() => handleRenameConversation(conversation.id)}
                                    title={isRTL ? 'שנה שם' : 'Rename'}
                                  >
                                    <Pencil className="w-4 h-4 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300" />
                                  </button>
                                  <button
                                    className="p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                    onClick={() => handleDeleteConversation(conversation.id)}
                                    title={isRTL ? 'מחק' : 'Delete'}
                                  >
                                    <Delete className="w-4 h-4 text-red-500 hover:text-red-600 dark:text-red-400 dark:hover:text-red-300" />
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            <button
              onClick={() => setShowSettings(true)}
              className={`w-full flex items-center transition-all ${isExpanded
                ? 'p-2 gap-3 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800'
                : 'justify-center py-1'
                }`}
            >
              <div className="relative">
                <Settings className="w-5 h-5 text-green-700 dark:text-green-500" />
              </div>
              {isExpanded && (
                <span className="text-sm text-gray-700 dark:text-gray-200">
                  Settings
                </span>
              )}
            </button>
          </div>

          {/* Logout Button */}
          <div className={`mt-auto ${isExpanded ? 'px-1' : 'px-0'}`}>
            <button
              onClick={handleLogout}
              className={`w-full flex items-center transition-all ${isExpanded
                ? 'p-2 gap-3 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400'
                : 'justify-center py-1 text-red-600 dark:text-red-400'
                }`}
            >
              <LogOut className="w-5 h-5" />
              {isExpanded && (
                <span className="text-sm">
                  {isRTL ? 'התנתק' : 'Log out'}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col bg-gray-50 dark:bg-black">
          <div className="flex-1 overflow-y-auto">
            {!hasStarted ? (
              <div className="h-full flex flex-col items-center justify-center">
                <h1 className="text-4xl font-bold mb-8 text-gray-800 dark:text-white">
                  {isRTL ? 'במה אוכל לעזור?' : 'What can I help with?'}
                </h1>
                <div className="w-full max-w-2xl">
                  <ChatInput
                    value={input}
                    onChange={setInput}
                    onSend={() => handleSend(input)}
                    isLoading={isLoading}
                    onClear={handleClear}
                    language={language}
                  />
                </div>
              </div>
            ) : (
              <>
                <MessageList messages={messages} fontSize={fontSize} />
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
                      {isRTL ? 'מעבד...' : 'Processing...'}
                    </span>
                  </div>
                )}
              </>
            )}
          </div>

          {hasStarted && (
            <ChatInput
              value={input}
              onChange={setInput}
              onSend={() => handleSend(input)}
              isLoading={isLoading}
              onClear={handleClear}
              language={language}
            />
          )}
        </div>
      </div>

      {showSettings && (
        <SettingsPanel
          onClose={() => setShowSettings(false)}
          theme={theme}
          setTheme={setTheme}
        />
      )}

      {isSettingsOpen && (
        <UserSettings onClose={() => setIsSettingsOpen(false)} />
      )}
    </div>
  );
};

export default ChatWindow;
