import React, { useState, useEffect } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import { Terminal, History, Settings, LogOut } from 'lucide-react';
import SettingsPanel from './SettingsPanel';
import { useNavigate } from 'react-router-dom';
import { API_CONFIG } from '../../config/constants';
import UserSettings from '../Settings/UserSettings';

interface Message {
  id: number;
  type: 'user' | 'bot';
  content: string;
  timestamp: string;
}

interface ChatWindowProps {
  onLogout: () => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ onLogout }) => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [hasStarted, setHasStarted] = useState(false);
  const [fontSize, setFontSize] = useState(14);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

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

  const handleLogout = () => {
    onLogout();
  };

  return (
    <div className="relative h-full w-full bg-gray-50 dark:bg-black text-gray-900 dark:text-white overflow-hidden">
      <div className="relative h-full flex z-10">
        {/* Sidebar */}
        <div
          className={`bg-gray-100 dark:bg-black backdrop-blur-xl transform transition-all duration-300 ${
            isExpanded ? 'w-64 p-4' : 'w-16 py-4 px-2'
          } border-r border-gray-200 dark:border-gray-800 flex flex-col overflow-hidden`}
          onMouseEnter={() => setIsExpanded(true)}
          onMouseLeave={() => setIsExpanded(false)}
        >
          <div className={`${isExpanded ? 'mb-8 text-center px-4' : 'mb-6 flex justify-center'}`}>
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

          <div className={`space-y-6 ${isExpanded ? 'px-4' : 'px-0'} flex-1`}>
            {[
              { icon: Terminal, label: 'Chat' },
              { icon: History, label: 'History' },
              {   
                icon: Settings,
                label: 'Settings',
                onClick: () => setShowSettings(true), 
              },
            ].map((item, index) => (
              <button
                key={index}
                onClick={item.onClick}
                className={`w-full flex items-center transition-all ${
                  isExpanded 
                    ? 'p-2 gap-3 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800' 
                    : 'justify-center py-1'
                }`}
              >
                <item.icon className="w-5 h-5 text-green-700 dark:text-green-500" />
                {isExpanded && (
                  <span className="text-sm text-gray-700 dark:text-gray-100">
                    {item.label}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Logout Button */}
          <div className={`mt-auto ${isExpanded ? 'px-4' : 'px-0'}`}>
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
                  Log out
                </span>
              )}
            </button>
          </div>
        </div>

        <div className="flex-1 flex flex-col bg-gray-50 dark:bg-black">
          <div className="flex-1 overflow-y-auto">
            {!hasStarted ? (
              <div className="h-full flex flex-col items-center justify-center">
                <h1 className="text-4xl font-bold mb-8 text-gray-800 dark:text-white">
                  What can I help with?
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
                    <span className="text-sm text-green-700 dark:text-green-500">Processing...</span>
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

      {isSettingsOpen && (
        <UserSettings onClose={() => setIsSettingsOpen(false)} />
      )}
    </div>
  );
};

export default ChatWindow;
