import React, { useState, useEffect, useRef } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import ChatHistory from './ChatHistory';
import { Terminal, History, Settings, LogOut } from 'lucide-react';
import SettingsPanel from './SettingsPanel';
import { API_CONFIG } from '../../config/constants';
import UserSettings from '../Settings/UserSettings';
import chatService, { ChatSession } from '../../services/chatService';
import { useTranslation } from 'react-i18next';

// Interface for message display
interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: string;
  sessionId?: string;
}

interface ChatWindowProps {
  onLogout: () => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ onLogout }) => {
  const { t } = useTranslation();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Status message state for notifications
  const [statusMessage, setStatusMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // UI state
  const [isExpanded, setIsExpanded] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [hasStarted, setHasStarted] = useState(false);
  const [fontSize, setFontSize] = useState(14);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  
  // Chat history state
  const [showHistory, setShowHistory] = useState(false);
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);

  // Set theme
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  // Load user chat sessions
  useEffect(() => {
    const initializeChat = async () => {
      setIsLoading(true);
      const user = await chatService.getCurrentUser();

      if (user) {
        console.log('User logged in, initializing chat history...');
        // Fetch user's chat sessions
        const sessions = await chatService.getUserChatSessions(user.id);
        console.log(`Found ${sessions.length} chat sessions`);
        setChatSessions(sessions);

        // If there are sessions, load the most recent one
        if (sessions.length > 0) {
          const mostRecentSession = sessions[0]; // Sessions are ordered by updated_at desc
          console.log('Loading most recent session:', mostRecentSession.id);
          setActiveSession(mostRecentSession);

          // Load messages for this session
          const sessionWithMessages = await chatService.getChatSessionWithMessages(mostRecentSession.id);
          if (sessionWithMessages && sessionWithMessages.messages) {
            console.log(`Loaded ${sessionWithMessages.messages.length} messages`);
            const formattedMessages = sessionWithMessages.messages.map(msg => ({
              id: msg.id,
              type: (msg.is_bot ? 'bot' : 'user') as 'bot' | 'user',
              content: msg.content,
              timestamp: new Date(msg.created_at).toLocaleTimeString(),
              sessionId: msg.chat_session_id
            })) as Message[];
            setMessages(formattedMessages);
            setHasStarted(true);
          }
        }
      } else {
        // In demo mode, just start with empty state
        console.log('User not logged in, starting in demo mode');
        setChatSessions([]);
        setMessages([]);
        setStatusMessage('You are in demo mode. Messages will not be saved. Please log in to save your chats.');
        setTimeout(() => setStatusMessage(''), 5000);
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
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSelectSession = async (sessionId: string) => {
    try {
      const { data: session } = await chatService.getChatSessionWithMessages(sessionId);
      if (session) {
        setActiveSession(session);
        setMessages(session.messages || []);
      }
    } catch (error) {
      console.error('Error loading chat session:', error);
    }
  };

  // Handle sending messages
  const handleSend = async () => {
    if (!input.trim()) return;
    
    // Try to get current user
    const user = await chatService.getCurrentUser();
    
    // For demo/development, create a mock session if user is not logged in
    let sessionId = 'demo-session';
    let userId = 'demo-user';
    let isDemo = false;
    
    // If user is logged in, use real session management
    if (user) {
      userId = user.id;
      console.log('User is logged in:', user.id);
      
      // Create a new session if none exists
      if (!activeSession) {
        console.log('Creating new chat session...');
        const session = await chatService.createChatSession(user.id, `Chat ${new Date().toLocaleDateString()}`);
        if (session) {
          console.log('Chat session created successfully:', session.id);
          setChatSessions(prev => [session, ...prev]);
          setActiveSession(session);
          sessionId = session.id;
        } else {
          // Use local demo session if can't create real one
          console.error('Failed to create chat session - using demo session instead');
          isDemo = true;
        }
      } else {
        console.log('Using existing chat session:', activeSession.id);
        sessionId = activeSession.id;
      }
    } else {
      console.log('User not logged in - using demo mode');
      isDemo = true;
      // Show a brief toast notification to inform user they're in demo mode
      if (messages.length === 0) {
        setStatusMessage('You are in demo mode. Messages will not be saved. Please log in to save your chats.');
        setTimeout(() => setStatusMessage(''), 5000);
      }
    }

    // If this is first message of the session, show welcome message
    if (!hasStarted) {
      setHasStarted(true);
      const welcomeMessage: Message = {
        id: `welcome-${Date.now().toString()}`,
        type: 'bot',
        content: t('chat.welcomeMessage') || 'Welcome to APEX - AFEKAs Professional Engineering Experience. How can I assist you?',
        timestamp: new Date().toLocaleTimeString(),
        sessionId: sessionId
      };
      
      setMessages([welcomeMessage]);
      
      // Save welcome message to database if user is logged in and not in demo mode
      if (user && !isDemo) {
        try {
          console.log('Saving welcome message to database...', {userId, sessionId});
          const savedMessage = await chatService.addMessage({
            user_id: userId,
            chat_session_id: sessionId,
            content: welcomeMessage.content,
            is_bot: true
          });
          
          if (savedMessage) {
            console.log('Welcome message saved successfully:', savedMessage.id);
          } else {
            console.error('Failed to save welcome message - database returned null');
          }
        } catch (error) {
          console.error('Exception while saving welcome message:', error);
        }
      } else {
        console.log('Not saving welcome message - demo mode or user not logged in', {isDemo, hasUser: !!user});
      }
    }

    // Create user message
    const userMessage: Message = {
      id: `user-${Date.now().toString()}`,
      type: 'user',
      content: input,
      timestamp: new Date().toLocaleTimeString(),
      sessionId: sessionId
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Save user message to database if user is logged in
    if (user && !isDemo) {
      try {
        console.log('Saving user message to database...', {userId, sessionId});
        const savedMessage = await chatService.addMessage({
          user_id: userId,
          chat_session_id: sessionId,
          content: userMessage.content,
          is_bot: false
        });
        
        if (savedMessage) {
          console.log('User message saved successfully:', savedMessage.id);
        } else {
          console.error('Failed to save user message - database returned null');
        }
      } catch (error) {
        console.error('Exception while saving user message:', error);
      }
    } else {
      console.log('Not saving user message - demo mode or user not logged in', {isDemo, hasUser: !!user});
    }

    try {
      // Call backend API
      const response = await fetch(API_CONFIG.CHAT_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage.content }),
        signal: AbortSignal.timeout(API_CONFIG.DEFAULT_TIMEOUT),
      });

      let botContent = '';
      
      if (response.ok) {
        const data = await response.json();
        botContent = data.result || t('chat.errorProcessing') || "Sorry, I couldn't process your request.";
      } else {
        botContent = t('chat.errorRequest') || 'Sorry, I encountered an error while processing your request.';
      }
      
      // Create bot reply
      const botReply: Message = {
        id: `bot-${Date.now().toString()}`,
        type: 'bot',
        content: botContent,
        timestamp: new Date().toLocaleTimeString(),
        sessionId: sessionId
      };
      
      setMessages(prev => [...prev, botReply]);
      
      // Save bot message to database if user is logged in
      if (user && !isDemo) {
        try {
          console.log('Saving bot message to database...', {userId, sessionId});
          const savedMessage = await chatService.addMessage({
            user_id: userId,
            chat_session_id: sessionId,
            content: botReply.content,
            is_bot: true
          });
          
          if (savedMessage) {
            console.log('Bot message saved successfully:', savedMessage.id);
          } else {
            console.error('Failed to save bot message - database returned null');
          }
        } catch (error) {
          console.error('Exception while saving bot message:', error);
        }
      } else {
        console.log('Not saving bot message - demo mode or user not logged in', {isDemo, hasUser: !!user});
      }
    } catch (error) {
      console.error('Exception while sending message:', error);
      const errorContent = t('chat.errorRequest') || 'Sorry, I encountered an error while processing your request.';
      const botReply: Message = {
        id: `error-${Date.now().toString()}`,
        type: 'bot',
        content: errorContent,
        timestamp: new Date().toLocaleTimeString(),
        sessionId: sessionId
      };
      
      setMessages(prev => [...prev, botReply]);
      
      // Save error message to database if user is logged in
      if (user && !isDemo) {
        try {
          console.log('Saving error message to database...', {userId, sessionId});
          const savedMessage = await chatService.addMessage({
            user_id: userId,
            chat_session_id: sessionId,
            content: botReply.content,
            is_bot: true
          });
          
          if (savedMessage) {
            console.log('Error message saved successfully:', savedMessage.id);
          } else {
            console.error('Failed to save error message - database returned null');
          }
        } catch (error) {
          console.error('Exception while saving error message:', error);
        }
      } else {
        console.log('Not saving error message - demo mode or user not logged in', {isDemo, hasUser: !!user});
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    onLogout();
  };

  return (
    <div className="relative h-full w-full bg-gray-50 dark:bg-black text-gray-900 dark:text-white overflow-hidden flex">
      {/* Status message toast */}
      {statusMessage && (
        <div className="absolute top-4 right-4 z-50 bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 rounded shadow-md max-w-md animate-fadeIn">
          <div className="flex">
            <div className="py-1">
              <svg className="h-6 w-6 text-yellow-500 mr-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <p className="font-bold">Demo Mode</p>
              <p className="text-sm">{statusMessage}</p>
            </div>
          </div>
        </div>
      )}

      {/* Sidebar component */}
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
            {
              [
                { icon: Terminal, label: t('chat.sidebar.chat'), onClick: () => setShowHistory(false) },
                { icon: History, label: t('chat.sidebar.history'), onClick: () => setShowHistory(true) },
                { icon: Settings, label: t('chat.sidebar.settings'), onClick: () => setShowSettings(true) }
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
              ))
            }
          </div>

          {/* Logout Button */}
          <div className="mt-auto">
            <button
              onClick={handleLogout}
              className="w-full flex items-center transition-all p-2 gap-3 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400"
            >
              <LogOut className="w-5 h-5" />
              <span className="text-sm">
                {t('common.logout')}
              </span>
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* History Panel */}
        {showHistory && (
          <div className="w-80 h-full">
            <ChatHistory
              sessions={chatSessions}
              onSelectSession={handleSelectSession}
              onCreateNewSession={() => handleSelectSession('new')}
              onDeleteSession={(sessionId) => console.log('Delete session:', sessionId)}
              onEditSessionTitle={(sessionId, title) => console.log('Edit session title:', sessionId, title)}
              activeSessionId={activeSession?.id}
              isLoading={isLoadingSessions}
            />
          </div>
        )}
        {/* Chat Window */}
        <div className="flex-1 flex flex-col bg-gray-50 dark:bg-black">
          {!activeSession ? (
            <div className="flex-1 flex flex-col items-center justify-center">
              <h1 className="text-3xl font-bold mb-6 text-gray-800 dark:text-white">
                {t('chat.noActiveSession', 'No chat session found')}
              </h1>
              <button
                onClick={() => handleSelectSession('new')}
                className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-xl text-lg font-semibold shadow-md transition-colors"
              >
                {t('chat.startNewChat', 'Start a New Chat')}
              </button>
            </div>
          ) : (
            <>
              {/* Header with session title */}
              <div className="py-2 px-4 border-b border-gray-200 dark:border-gray-800 flex justify-between items-center">
                <h2 className="text-lg font-medium truncate">
                  {activeSession.title || t('chat.untitledChat')}
                </h2>
                <button
                  onClick={() => handleSelectSession('new')}
                  className="p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800"
                  title={t('chat.newChat')}
                >
                  <Terminal className="w-5 h-5" />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto">
                {!hasStarted ? (
                  <div className="h-full flex flex-col items-center justify-center">
                    <h1 className="text-4xl font-bold mb-8 text-gray-800 dark:text-white">
                      {t('chat.startPrompt')}
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
                        <span className="text-sm text-green-700 dark:text-green-500">{t('chat.processing')}</span>
                      </div>
                    )}
                    {hasStarted && (
                      <ChatInput
                        input={input}
                        setInput={setInput}
                        onSend={handleSend}
                        isLoading={isLoading}
                      />
                    )}
                  </>
                )}
              </div>
            </>
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
