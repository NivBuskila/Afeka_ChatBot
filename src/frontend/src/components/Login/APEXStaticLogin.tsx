import React, { useState, useEffect, useRef } from 'react';
import { Brain, LogIn, Shield, User, Lock, Eye, EyeOff } from 'lucide-react';
import './APEXStaticLogin.css';

interface APEXStaticLoginProps {
  onLoginSuccess: (isAdmin: boolean) => void;
}

const APEXStaticLogin: React.FC<APEXStaticLoginProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Minimal Matrix effect
  const MatrixRain = () => {
    const canvas = useRef<HTMLCanvasElement>(null);
    
    useEffect(() => {
      if (!canvas.current) return;
      
      const ctx = canvas.current.getContext('2d');
      if (!ctx) return;
      
      canvas.current.width = window.innerWidth;
      canvas.current.height = window.innerHeight;
      
      const binary = '01';
      const fontSize = 14;
      const columns = canvas.current.width / fontSize;
      const drops = new Array(Math.floor(columns)).fill(1);
      
      const draw = () => {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.current!.width, canvas.current!.height);
        ctx.fillStyle = '#0f0';
        ctx.font = `${fontSize}px monospace`;
        
        for (let i = 0; i < drops.length; i++) {
          const text = binary.charAt(Math.floor(Math.random() * binary.length));
          ctx.fillText(text, i * fontSize, drops[i] * fontSize);
          drops[i]++;
          if (drops[i] * fontSize > canvas.current!.height && Math.random() > 0.975) {
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Validate fields
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password');
      return;
    }
    
    // Show loading state
    setIsLoading(true);
    
    // Simulate authentication process
    setTimeout(() => {
      setIsLoading(false);
      
      // Check credentials
      const isAdminUser = username.trim().toLowerCase() === 'admin' && password === 'apex2025';
      const isRegularUser = username.trim().toLowerCase() === 'user' && password === 'apex2024';
      
      if (isAdminUser || isRegularUser) {
        onLoginSuccess(isAdminUser);
      } else {
        setError('Invalid credentials. Access denied.');
      }
    }, 1500);
  };

  return (
    <div className="relative h-screen bg-black text-white overflow-hidden">
      <MatrixRain />
      
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
      
      {/* Login Content */}
      <div className="flex flex-col items-center justify-center min-h-screen p-4 relative z-10">
        {/* Logo */}
        <div className="mb-8 flex flex-col items-center">
          <div className="relative">
            <div className="absolute inset-0 bg-green-500 rounded-full filter blur-lg opacity-20" />
            <Brain className="w-16 h-16 text-green-400 relative z-10" />
          </div>
          <div className="mt-4 text-3xl font-bold text-green-400">APEX</div>
          <div className="text-sm text-green-400/70 mt-1">Authentication Portal</div>
        </div>
        
        {/* Login card */}
        <div className="w-full max-w-md bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 overflow-hidden">
          {/* Header */}
          <div className="bg-green-500/5 border-b border-green-500/10 px-6 py-4 flex items-center">
            <Shield className="w-5 h-5 text-green-400/80 mr-2" />
            <span className="text-green-400/90 font-semibold">Secure Login</span>
          </div>
          
          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-5">
            {error && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-md text-sm">
                {error}
              </div>
            )}
            
            {/* Username field */}
            <div className="space-y-2">
              <label className="block text-sm text-green-400/80 mb-1">Username</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-green-500/50" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-black/50 border border-green-500/30 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-green-500/50 focus:border-green-500/50"
                  placeholder="Enter your username"
                />
              </div>
            </div>
            
            {/* Password field */}
            <div className="space-y-2">
              <label className="block text-sm text-green-400/80 mb-1">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-green-500/50" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-10 py-2 bg-black/50 border border-green-500/30 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-green-500/50 focus:border-green-500/50"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-green-500/50" />
                  ) : (
                    <Eye className="h-5 w-5 text-green-500/50" />
                  )}
                </button>
              </div>
            </div>
            
            {/* Submit button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-green-500/20 hover:bg-green-500/30 text-green-400 font-medium py-2 px-4 rounded-md border border-green-500/30 transition-colors flex items-center justify-center space-x-2"
            >
              {isLoading ? (
                <div className="flex space-x-1">
                  {[...Array(3)].map((_, i) => (
                    <div
                      key={i}
                      className="w-1 h-1 bg-green-400 rounded-full animate-bounce"
                      style={{ animationDelay: `${i * 0.2}s` }}
                    />
                  ))}
                </div>
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  <span>Login to APEX</span>
                </>
              )}
            </button>
            
            {/* Recovery link */}
            <div className="text-center mt-4">
              <a href="#" className="text-green-400/60 hover:text-green-400/80 text-sm transition-colors">
                Forgot credentials? Contact system administrator
              </a>
            </div>
          </form>
          
          {/* System info footer */}
          <div className="bg-black/40 px-6 py-3 text-xs text-green-400/50 flex justify-between">
            <span>APEX v3.5.2</span>
          </div>
        </div>
      </div>
      
      {/* Ambient light effects */}
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-green-500 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob" />
        <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-green-700 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob animation-delay-2000" />
      </div>
    </div>
  );
};

export default APEXStaticLogin; 