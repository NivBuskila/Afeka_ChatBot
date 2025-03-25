import React, { useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import APEXSplashScreen from './components/SplashScreen/components/APEXSplashScreen';
import APEXStaticLogin from './components/Login/APEXStaticLogin';
import AdminDashboard from './components/Dashboard/AdminDashboard';
import ChatWindow from './components/Chat/ChatWindow';

import './styles/globals.css';
import './styles/animations.css';

const App: React.FC = () => {
  const [isLanding, setIsLanding] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const navigate = useNavigate();

  const handleSplashComplete = (): void => {
    setIsLanding(false);
  };

  const handleLoginSuccess = (isAdminUser: boolean): void => {
    setIsLoggedIn(true);
    setIsAdmin(isAdminUser);
    if (isAdminUser) {
      navigate('/dashboard');
    } else {
      navigate('/chat');
    }
  };

  const handleLogout = (): void => {
    setIsLoggedIn(false);
    setIsAdmin(false);
    navigate('/');
  };

  return (
    <div className="h-screen w-screen bg-black text-white font-sans overflow-hidden">
      <Routes>
        <Route path="/" element={
          isLanding ? (
            <APEXSplashScreen onSplashComplete={handleSplashComplete} />
          ) : !isLoggedIn ? (
            <APEXStaticLogin onLoginSuccess={handleLoginSuccess} />
          ) : null
        } />
        <Route path="/dashboard" element={<AdminDashboard onLogout={handleLogout} />} />
        <Route path="/chat" element={<ChatWindow onLogout={handleLogout} />} />
      </Routes>
    </div>
  );
};

export default App;
