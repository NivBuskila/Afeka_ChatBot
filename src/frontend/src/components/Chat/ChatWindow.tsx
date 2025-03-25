import React, { useState, useEffect } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import { Terminal, History, Settings } from 'lucide-react';
import SettingsPanel from './SettingsPanel';

interface Message {
  id: number;
  type: 'user' | 'bot';
  content: string;
  timestamp: string;
}

const ChatWindow: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [hasStarted, setHasStarted] = useState(false);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const handleSend = () => {
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

    const newMessage: Message = {
      type: 'user',
      content: input,
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setInput('');
    setIsLoading(true);

    setTimeout(() => {
      const botReply: Message = {
        type: 'bot',
        content:
          'Processing your request through AFEKAs advanced engineering knowledge base.',
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, botReply]);
      setIsLoading(false);
    }, 1500);
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

          <div className={`space-y-6 ${isExpanded ? 'px-4' : 'px-0'}`}>
            {[
              { icon: Terminal, label: 'Console' },
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
                <MessageList messages={messages} />
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
    </div>
  );
};

export default ChatWindow;
