// APEXInterface Component
const APEXInterface = () => {
  // States
  const [messages, setMessages] = React.useState([
    {
      type: 'bot',
      content: 'Welcome to APEX - AFEKAs Professional Engineering Experience. How can I assist you today?',
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [input, setInput] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(false);
  const [isExpanded, setIsExpanded] = React.useState(false);
  const [currentView, setCurrentView] = React.useState('chat');

  // Settings Component
  const SettingsView = () => {
    return (
      <div className="h-full flex flex-col p-6 bg-black bg-opacity-20">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl text-green-400">Settings</h2>
          <button 
            onClick={() => setCurrentView('chat')}
            className="p-2 hover:bg-green-500 hover:bg-opacity-10 rounded-lg transition-colors"
          >
            <i className="fas fa-times text-green-400 opacity-80" />
          </button>
        </div>
        
        <div className="space-y-6">
          <div className="space-y-4">
            <h3 className="text-green-400 opacity-80 text-sm font-medium">Interface</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-white opacity-90">Dark Mode</span>
                <div className="w-12 h-6 bg-green-500 bg-opacity-20 rounded-full relative cursor-pointer">
                  <div className="absolute w-5 h-5 bg-green-400 rounded-full top-0.5 right-0.5"></div>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white opacity-90">Sound Effects</span>
                <div className="w-12 h-6 bg-green-500 bg-opacity-20 rounded-full relative cursor-pointer">
                  <div className="absolute w-5 h-5 bg-green-400 opacity-50 rounded-full top-0.5 left-0.5"></div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <h3 className="text-green-400 opacity-80 text-sm font-medium">About</h3>
            <div className="bg-black bg-opacity-20 p-4 rounded-lg">
              <p className="text-white opacity-70 text-sm">APEX Version 1.0.0</p>
              <p className="text-white opacity-50 text-xs mt-1">© 2024 AFEKA Engineering</p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Handle message sending
  const handleSend = () => {
    if (!input.trim()) return;
    
    const newMessage = {
      type: 'user',
      content: input,
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString()
    };
    
    setMessages(prev => [...prev, newMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate bot response
    setTimeout(() => {
      setMessages(prev => [...prev, {
        type: 'bot',
        content: 'Processing your request through AFEKAs advanced engineering knowledge base.',
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString()
      }]);
      setIsLoading(false);
    }, 1500);
  };

  // Chat View Component
  const ChatView = () => (
    <div>
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {messages.map((message) => (
          <div
            key={message.id}
            className={"flex items-start gap-3 " + (message.type === 'user' ? 'flex-row-reverse' : '')}
          >
            <div className={"relative p-3 rounded-lg " + 
              (message.type === 'user'
                ? 'bg-green-500 bg-opacity-10 border border-green-500 border-opacity-20'
                : 'bg-black bg-opacity-20 border border-green-500 border-opacity-10')
            }>
              <div className="flex items-center gap-2 mb-1">
                {message.type === 'user' ? (
                  <i className="fas fa-user w-3 h-3 text-green-400 opacity-80" />
                ) : (
                  <i className="fas fa-robot w-3 h-3 text-green-400 opacity-80" />
                )}
                <span className="text-xs text-green-400 opacity-60">
                  {message.timestamp}
                </span>
              </div>
              <p className="text-sm text-white opacity-90">{message.content}</p>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex items-center gap-2">
            <div className="flex space-x-1">
              {[1, 2, 3].map((_, i) => (
                <div
                  key={i}
                  className="w-1 h-1 bg-green-400 rounded-full animate-bounce"
                  style={{animationDelay: `${i * 0.2}s`}}
                />
              ))}
            </div>
            <span className="text-xs text-green-400 opacity-80">Processing...</span>
          </div>
        )}
      </div>

      <div className="p-4 bg-black bg-opacity-20 border-t border-green-500 border-opacity-10">
        <div className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            className="w-full bg-black bg-opacity-40 text-white rounded-lg p-3 pr-12 text-sm focus:outline-none focus:ring-1 focus:ring-green-500 focus:ring-opacity-30 placeholder-gray-500"
          />
          <button
            onClick={handleSend}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 hover:bg-green-500 hover:bg-opacity-10 rounded-lg transition-colors"
          >
            <i className="fas fa-paper-plane w-4 h-4 text-green-400 opacity-80" />
          </button>
        </div>
      </div>
    </div>
  );

  // Main Interface Render
  return (
    <div className="relative h-screen bg-black text-white overflow-hidden">
      <div className="relative h-full flex z-10">
        {/* Sidebar */}
        <div 
          className={"bg-black bg-opacity-40 backdrop-blur-xl p-4 transform transition-all duration-300 " + 
            (isExpanded ? 'w-64' : 'w-16') + 
            " border-r border-green-500 border-opacity-20"}
          onMouseEnter={() => setIsExpanded(true)}
          onMouseLeave={() => setIsExpanded(false)}
        >
          {/* APEX Logo */}
          <div className="mb-8 text-center">
            <div className="text-green-400 font-bold text-xl mb-1">APEX</div>
            {isExpanded && (
              <div className="text-xs text-green-400 opacity-70">
                AFEKA Engineering AI
              </div>
            )}
          </div>

          {/* Navigation */}
          <div className="space-y-2">
            {[
              { icon: 'fa-terminal', label: 'Console', view: 'chat' },
              { icon: 'fa-cog', label: 'Settings', view: 'settings' }
            ].map((item, index) => (
              <button
                key={index}
                onClick={() => setCurrentView(item.view)}
                className={"w-full p-2 flex items-center gap-3 rounded-md transition-all hover:bg-green-500 hover:bg-opacity-10 " +
                  (currentView === item.view ? 'bg-green-500 bg-opacity-20' : '')}
              >
                <i className={"fas " + item.icon + " w-5 h-5 text-green-400 opacity-80"} />
                <span className={"text-sm transition-all " +
                  (isExpanded ? 'opacity-100' : 'opacity-0')}>
                  {item.label}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="px-4 py-3 bg-black bg-opacity-20 border-b border-green-500 border-opacity-10">
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm text-green-400 opacity-80">APEX Active</span>
            </div>
          </div>
          
          {/* Conditional Content Render */}
          {currentView === 'chat' ? <ChatView /> : <SettingsView />}
        </div>
      </div>
    </div>
  );
};

// Landing Page Component
const APEXApplication = () => {
  const [showChat, setShowChat] = React.useState(false);
  const [showFullName, setShowFullName] = React.useState(false);
  const [textVisible, setTextVisible] = React.useState([false, false, false, false]);
  
  // Animation Effect
  React.useEffect(() => {
    setTimeout(() => {
      const showLetters = setInterval(() => {
        setTextVisible(prev => {
          const newState = [...prev];
          const nextIndex = newState.findIndex(v => !v);
          if (nextIndex !== -1) {
            newState[nextIndex] = true;
          }
          return newState;
        });
      }, 500);

      setTimeout(() => {
        setShowFullName(true);
        clearInterval(showLetters);
      }, 2500);
    }, 1000);
  }, []);

  // Render Chat Interface
  if (showChat) {
    return React.createElement(APEXInterface);
  }

  // Landing Page Render
  return (
    <div 
      className="relative h-screen bg-black text-white overflow-hidden cursor-pointer"
      onClick={() => setShowChat(true)}
    >
      <div className="relative z-10 h-full flex flex-col items-center justify-center">
        {/* Logo Container */}
        <div className="relative">
          {/* Rotating Hexagon Background */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-48 h-48 border-2 border-green-500 border-opacity-30 rotate-45 transform animate-spin-slow" />
            <div className="absolute w-48 h-48 border-2 border-green-500 border-opacity-20 -rotate-45 transform animate-spin-reverse" />
          </div>

          {/* Brain Icon */}
          <div className="relative transform hover:scale-105 transition-transform">
            <div className="absolute inset-0 bg-green-500 rounded-full filter blur-xl opacity-20 animate-pulse" />
            <i className="fas fa-brain text-6xl text-green-400 relative z-10" />
          </div>
        </div>

        {/* APEX Letters */}
        <div className="mt-12 flex items-center space-x-4">
          {['A', 'P', 'E', 'X'].map((letter, index) => (
            <div
              key={letter}
              className={"text-5xl font-bold transition-all duration-500 transform " +
                (textVisible[index] ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10')}
            >
              <span className="text-green-400">{letter}</span>
            </div>
          ))}
        </div>

        {/* Full Name */}
        {showFullName && (
          <div className="mt-6 text-lg text-green-400 opacity-80">
            <div className="text-center space-y-1">
              <div>AFEKAs</div>
              <div>Professional</div>
              <div>Engineering</div>
              <div>eXperience</div>
            </div>
          </div>
        )}

        {/* Click Instruction */}
        {showFullName && (
          <div className="absolute bottom-12 left-1/2 transform -translate-x-1/2 text-green-400 opacity-60 text-sm animate-pulse">
            Click anywhere to continue
          </div>
        )}
      </div>
    </div>
  );
};

// Initialize and Render Application
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(React.createElement(APEXApplication));