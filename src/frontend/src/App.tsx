import React, { useState } from 'react';
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

  const handleSplashComplete = (): void => {
    setIsLanding(false);
  };

  const handleLoginSuccess = (isAdminUser: boolean): void => {
    setIsLoggedIn(true);
    setIsAdmin(isAdminUser);
  };

  return (
    <div className="h-screen w-screen bg-black text-white font-sans overflow-hidden">
      {isLanding ? (
        <APEXSplashScreen onSplashComplete={handleSplashComplete} />
      ) : !isLoggedIn ? (
        <APEXStaticLogin onLoginSuccess={handleLoginSuccess} />
      ) : isAdmin ? (
        <AdminDashboard />
      ) : (
        <ChatWindow />
      )}
    </div>
  );
};

export default App;
