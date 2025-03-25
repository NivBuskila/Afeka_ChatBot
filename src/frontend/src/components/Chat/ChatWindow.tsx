import React, { useState, useEffect } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import { Terminal, Search, History, Settings } from 'lucide-react';
import SettingsPanel from './SettingsPanel';

interface Message {
  id: number;
  type: 'user' | 'bot';
  content: string;
  timestamp: string;
}

const ChatWindow: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      type: 'bot',
      content:
        'Welcome to APEX - AFEKAs Professional Engineering Experience. How can I assist you?',
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  
  const [isExpanded, setIsExpanded] = useState(false);

  const [showSettings, setShowSettings] = useState(false);

  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [fontSize, setFontSize] = useState(14);
  const [animations, setAnimations] = useState('Enabled');
  const [contrast, setContrast] = useState('Normal');

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const handleSend = () => {
    if (!input.trim()) return;

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
    <div className="relative h-full w-full bg-black text-white dark:bg-gray-900 dark:text-gray-100 overflow-hidden">
      <div className="relative h-full flex z-10">
        {/* Sidebar */}
        <div
          className={`bg-black/40 dark:bg-gray-800/40 backdrop-blur-xl p-4 transform transition-all duration-300 ${
            isExpanded ? 'w-64' : 'w-16'
          } border-r border-green-500/20`}
          onMouseEnter={() => setIsExpanded(true)}
          onMouseLeave={() => setIsExpanded(false)}
        >
          <div className="mb-8 text-center">
            <div className="text-green-400 font-bold text-xl mb-1">APEX</div>
            {isExpanded && (
              <div className="text-xs text-green-400/70">
                AFEKA Engineering AI
              </div>
            )}
          </div>

          {}
          <div className="space-y-2">
            {[
              { icon: Terminal, label: 'Console' },
              { icon: Search, label: 'Search' },
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
                className="w-full p-2 flex items-center gap-3 rounded-md transition-all hover:bg-green-500/10"
              >
                <item.icon className="w-5 h-5 text-green-400/80" />
                <span
                  className={`text-sm transition-all ${
                    isExpanded ? 'opacity-100' : 'opacity-0'
                  }`}
                >
                  {item.label}
                </span>
              </button>
            ))}
          </div>
        </div>

        {}
        <div className="flex-1 flex flex-col">
          {}
          <div className="px-4 py-3 bg-black/20 dark:bg-gray-800/30 border-b border-green-500/10">
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm text-green-400/80">APEX Active</span>
            </div>
          </div>

          {}
          <MessageList messages={messages} fontSize={fontSize} />

          {}
          {isLoading && (
            <div className="p-4 flex items-center gap-2">
              <div className="flex space-x-1">
                {[...Array(3)].map((_, i) => (
                  <div
                    key={i}
                    className="w-1 h-1 bg-green-400 rounded-full animate-bounce"
                    style={{ animationDelay: `${i * 0.2}s` }}
                  />
                ))}
              </div>
              <span className="text-xs text-green-400/80">Processing...</span>
            </div>
          )}

          {}
          <ChatInput
            input={input}
            setInput={setInput}
            onSend={handleSend}
            isLoading={isLoading}
          />
        </div>
      </div>

      {}
      {showSettings && (
        <SettingsPanel
          onClose={() => setShowSettings(false)}
          theme={theme}
          setTheme={setTheme}
          fontSize={fontSize}
          setFontSize={setFontSize}
          animations={animations}
          setAnimations={setAnimations}
          contrast={contrast}
          setContrast={setContrast}
        />
      )}
    </div>
  );
};

export default ChatWindow;
