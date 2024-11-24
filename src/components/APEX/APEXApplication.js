const APEXInterface = () => {
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
  const messagesEndRef = React.useRef(null);

  // Minimal Matrix effect
  const MatrixRain = () => {
    const canvas = React.useRef(null);
    
    React.useEffect(() => {
      const ctx = canvas.current.getContext('2d');
      canvas.current.width = window.innerWidth;
      canvas.current.height = window.innerHeight;
      
      const binary = '01';
      const fontSize = 14;
      const columns = canvas.current.width / fontSize;
      const drops = new Array(Math.floor(columns)).fill(1);
      
      const draw = () => {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.current.width, canvas.current.height);
        ctx.fillStyle = '#0f0';
        ctx.font = `${fontSize}px monospace`;
        
        for (let i = 0; i < drops.length; i++) {
          const text = binary.charAt(Math.floor(Math.random() * binary.length));
          ctx.fillText(text, i * fontSize, drops[i] * fontSize);
          drops[i]++;
          if (drops[i] * fontSize > canvas.current.height && Math.random() > 0.975) {
            drops[i] = 0;
          }
        }
      };
      
      const interval = setInterval(draw, 33);
      return () => clearInterval(interval);
    }, []);

    return (
      <canvas
        ref={canvas}
        className="absolute inset-0 opacity-5"
        style={{ zIndex: 0 }}
      />
    );
  };

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
  return (
    <div className="relative h-screen bg-black text-white overflow-hidden">
      <MatrixRain />
      
      <div className="relative h-full flex z-10">
        {/* Minimal sidebar */}
        <div 
          className={`bg-black/40 backdrop-blur-xl p-4 transform transition-all duration-300 ${
            isExpanded ? 'w-64' : 'w-16'
          } border-r border-green-500/20`}
          onMouseEnter={() => setIsExpanded(true)}
          onMouseLeave={() => setIsExpanded(false)}
        >
          {/* APEX Logo */}
          <div className="mb-8 text-center">
            <div className="text-green-400 font-bold text-xl mb-1">APEX</div>
            {isExpanded && (
              <div className="text-xs text-green-400/70">
                AFEKA Engineering AI
              </div>
            )}
          </div>

          {/* Navigation */}
          <div className="space-y-2">
            {[
              { icon: 'fa-terminal', label: 'Console' },
              { icon: 'fa-search', label: 'Search' },
              { icon: 'fa-history', label: 'History' },
              { icon: 'fa-cog', label: 'Settings' }
            ].map((item, index) => (
              <button
                key={index}
                className="w-full p-2 flex items-center gap-3 rounded-md transition-all hover:bg-green-500/10"
              >
                <i className={`fas ${item.icon} w-5 h-5 text-green-400/80`} />
                <span className={`text-sm transition-all ${
                  isExpanded ? 'opacity-100' : 'opacity-0'
                }`}>
                  {item.label}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Main chat area */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="px-4 py-3 bg-black/20 border-b border-green-500/10">
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm text-green-400/80">APEX Active</span>
            </div>
          </div>
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start gap-3 ${
                  message.type === 'user' ? 'flex-row-reverse' : ''
                }`}
              >
                <div className={`relative p-3 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-green-500/10 border border-green-500/20'
                    : 'bg-black/20 border border-green-500/10'
                } max-w-2xl`}>
                  <div className="flex items-center gap-2 mb-1">
                    {message.type === 'user' ? (
                      <i className="fas fa-user w-3 h-3 text-green-400/80" />
                    ) : (
                      <i className="fas fa-robot w-3 h-3 text-green-400/80" />
                    )}
                    <span className="text-xs text-green-400/60">
                      {message.timestamp}
                    </span>
                  </div>
                  <p className="text-sm text-white/90">{message.content}</p>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex items-center gap-2">
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
          </div>

          {/* Input */}
          <div className="p-4 bg-black/20 border-t border-green-500/10">
            <div className="relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Type your message..."
                className="w-full bg-black/40 text-white rounded-lg p-3 pr-12 text-sm focus:outline-none focus:ring-1 focus:ring-green-500/30 placeholder-gray-500"
              />
              <button
                onClick={handleSend}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 hover:bg-green-500/10 rounded-lg transition-colors"
              >
                <i className="fas fa-paper-plane w-4 h-4 text-green-400/80" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
const APEXApplication = () => {
  const [showChat, setShowChat] = React.useState(false);
  const [showFullName, setShowFullName] = React.useState(false);
  const [textVisible, setTextVisible] = React.useState(Array(4).fill(false));
  
  React.useEffect(() => {
    // Start showing letters after a delay
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

      // Show full name after all letters appear
      setTimeout(() => {
        setShowFullName(true);
        clearInterval(showLetters);
      }, 2500);
    }, 1000);
  }, []);

  const handleClick = () => {
    setShowChat(true);
  };

  if (showChat) {
    return <APEXInterface />;
  }

  return (
    <div 
      className="relative h-screen bg-black text-white overflow-hidden cursor-pointer"
      onClick={handleClick}
    >
      {/* Matrix-like background */}
      <div className="absolute inset-0 opacity-20">
        {[...Array(50)].map((_, i) => (
          <div
            key={i}
            className="absolute text-green-500 text-opacity-20 animate-matrix"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              fontSize: `${Math.random() * 10 + 10}px`
            }}
          >
            01
          </div>
        ))}
      </div>

      {/* Main content */}
      <div className="relative z-10 h-full flex flex-col items-center justify-center">
        {/* Logo container */}
        <div className="relative">
          {/* Rotating hexagon background */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-48 h-48 border-2 border-green-500/30 rotate-45 transform animate-spin-slow" />
            <div className="absolute w-48 h-48 border-2 border-green-500/20 -rotate-45 transform animate-spin-reverse" />
          </div>

          {/* Central brain icon */}
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
              className={`text-5xl font-bold transition-all duration-500 transform
                ${textVisible[index] ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}
              `}
            >
              <span className="text-green-400">{letter}</span>
            </div>
          ))}
        </div>

        {/* Full name reveal */}
        <div className={`mt-6 text-lg text-green-400/80 transition-all duration-1000 
          ${showFullName ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}
        >
          <div className="text-center space-y-1">
            <div>AFEKAs</div>
            <div>Professional</div>
            <div>Engineering</div>
            <div>eXperience</div>
          </div>
        </div>

        {/* Hover instruction */}
        {showFullName && (
          <div className="absolute bottom-12 left-1/2 transform -translate-x-1/2 text-green-400/60 text-sm animate-pulse">
            Click anywhere to continue
          </div>
        )}
      </div>

      {/* Ambient light effects */}
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-green-500 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob" />
        <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-green-700 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob animation-delay-2000" />
      </div>
    </div>
  );
};

// Create root and render the application
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<APEXApplication />);