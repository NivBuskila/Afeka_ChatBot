import React, { useState, useEffect, useRef } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import { Terminal, History, Settings, LogOut, Calendar, Trash2, ChevronUp, ChevronDown, Pencil, Delete } from 'lucide-react';
import SettingsPanel from './SettingsPanel';
import { useNavigate } from 'react-router-dom';
import { API_CONFIG } from '../../config/constants';
import { useTranslation } from 'react-i18next';

interface Message {
  id: number;
  type: 'user' | 'bot';
  content: string;
  timestamp: string;
}

interface Conversation {
  id: string;
  title: string;
  date: string;
  preview: string;
}

interface ChatWindowProps {
  onLogout: () => void;
}

// Group conversations by date
const groupConversations = (conversations: Conversation[]) => {
  const today = new Date().toLocaleDateString();
  const yesterday = new Date(Date.now() - 86400000).toLocaleDateString();
  
  return {
    today: conversations.filter(conv => conv.date === today),
    yesterday: conversations.filter(conv => conv.date === yesterday),
    previous: conversations.filter(conv => conv.date !== today && conv.date !== yesterday),
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
  const [activeConversation, setActiveConversation] = useState<string | null>(null);
  const [activeButtonRect, setActiveButtonRect] = useState<DOMRect | null>(null);

  // Mock conversation history data (will be replaced with API data later)
  const today = new Date().toLocaleDateString();
  const yesterday = new Date(Date.now() - 86400000).toLocaleDateString();
  const previousDay = new Date(Date.now() - 2 * 86400000).toLocaleDateString();
  
  const [conversations, setConversations] = useState([
    {
      id: '1',
      title: 'שאלות על קורס אלגוריתמים',
      date: today,
      preview: 'שאלתי על חומר הלימוד בקורס אלגוריתמים והתנאים לקבלת תואר'
    },
    {
      id: '2',
      title: 'מידע על רישום לקורסים',
      date: yesterday,
      preview: 'התייעצתי בנוגע לרישום לקורסים והתנאים להרשמה'
    },
    {
      id: '3',
      title: 'שאלות על פרויקט גמר',
      date: previousDay,
      preview: 'ביקשתי מידע על דרישות פרויקט הגמר ומועדי הגשה'
    },
    {
      id: '4',
      title: '300 Million Button Company',
      date: today,
      preview: 'מידע על חברת 300 Million Button'
    },
    {
      id: '5',
      title: 'גניבת צמחים סיבות',
      date: yesterday,
      preview: 'דיון על הסיבות לגניבת צמחים'
    },
    {
      id: '6',
      title: 'המסך שחור בטלוויזיה',
      date: previousDay,
      preview: 'פתרון בעיות במסך שחור בטלוויזיה'
    }
  ]);

  // Group conversations
  const groupedConversations = groupConversations(conversations);

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

  const handleSend = async () => {
    if (!input.trim()) return;

    if (!hasStarted) {
      setHasStarted(true);
      setMessages([
        {
          type: 'bot',
          content: 'Welcome to APEX - AFEKAs Professional Engineering Experience. How can I assist you?',
          id: Date.now() - 1,
          timestamp: new Date().toLocaleTimeString(),
        }
      ]);
    }

    const userMessage: Message = {
      type: 'user',
      content: input,
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call backend API
      const response = await fetch(API_CONFIG.CHAT_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage.content }),
        // Add timeout using AbortController
        signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT),
      });

      if (response.ok) {
        const data = await response.json();
        
        const botReply: Message = {
          type: 'bot',
          content: data.result || "Sorry, I couldn't process your request.",
          id: Date.now(),
          timestamp: new Date().toLocaleTimeString(),
        };
        
        setMessages((prev) => [...prev, botReply]);
      } else {
        // Handle error response
        const botReply: Message = {
          type: 'bot',
          content: 'Sorry, I encountered an error while processing your request.',
          id: Date.now(),
          timestamp: new Date().toLocaleTimeString(),
        };
        setMessages((prev) => [...prev, botReply]);
      }
    } catch (error) {
      // Handle network errors
      const botReply: Message = {
        type: 'bot',
        content: 'Sorry, I was unable to connect to the server. Please try again later.',
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, botReply]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectConversation = (id: string) => {
    // Will be implemented with backend integration later
    
    // Mock loading a conversation
    alert(`בעתיד: טעינת שיחה מספר ${id}`);
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

  return (
    <div className="relative h-full w-full bg-gray-50 dark:bg-black text-gray-900 dark:text-white overflow-hidden">
      <div className="relative h-full flex z-10">
        {/* Sidebar */}
        <div
          className={`flex-shrink-0 bg-gray-100 dark:bg-black backdrop-blur-xl transform transition-all duration-300 ${
            isExpanded ? `${showHistory ? 'w-80' : 'w-64'} p-4` : 'w-16 py-4 px-2'
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
              className={`w-full flex items-center transition-all ${
                isExpanded 
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
              className={`w-full flex items-center transition-all ${
                isExpanded 
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
              className={`w-full flex items-center transition-all ${
                isExpanded 
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
              className={`w-full flex items-center transition-all ${
                isExpanded 
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
              input={input}
              setInput={setInput}
              onSend={handleSend}
              isLoading={isLoading}
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
    </div>
  );
};

export default ChatWindow;
