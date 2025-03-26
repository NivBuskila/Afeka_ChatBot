import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { SessionContextProvider } from '@supabase/auth-helpers-react';
import { supabase } from './config/supabase';
import { useTranslation } from 'react-i18next';
import './i18n/config';

import APEXSplashScreen from './components/SplashScreen/components/APEXSplashScreen';
import APEXStaticLogin from './components/Login/APEXStaticLogin';
import APEXRegistration from './components/Login/APEXRegistration';
import { AdminDashboard } from './components/Dashboard/AdminDashboard';
import ChatWindow from './components/Chat/ChatWindow';

import './styles/globals.css';

const App: React.FC = () => {
  const [isLanding, setIsLanding] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [showRegistration, setShowRegistration] = useState(false);
  const navigate = useNavigate();
  const { i18n } = useTranslation();

  useEffect(() => {
    // Set initial language direction
    document.documentElement.dir = i18n.language === 'he' ? 'rtl' : 'ltr';
    document.documentElement.lang = i18n.language;
  }, [i18n.language]);

  const handleSplashComplete = () => {
    setIsLanding(false);
  };

  const handleLoginSuccess = (isAdminUser: boolean) => {
    setIsLoggedIn(true);
    setIsAdmin(isAdminUser);
    
    if (isAdminUser) {
      navigate('/dashboard');
    } else {
      navigate('/chat');
    }
  };

  const handleRegistrationSuccess = () => {
    setShowRegistration(false);
    alert(i18n.language === 'he' 
      ? 'הרישום בוצע בהצלחה! אנא התחבר עם פרטי המשתמש שיצרת' 
      : 'Registration successful! Please login with your credentials');
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setIsAdmin(false);
    supabase.auth.signOut();
    navigate('/');
  };

  const renderAuthScreen = () => {
    if (isLanding) {
      return <APEXSplashScreen onSplashComplete={handleSplashComplete} />;
    }
    
    if (!isLoggedIn) {
      if (showRegistration) {
        return (
          <APEXRegistration 
            onRegistrationSuccess={handleRegistrationSuccess} 
            onBackToLogin={() => setShowRegistration(false)} 
          />
        );
      } else {
        return (
          <APEXStaticLogin 
            onLoginSuccess={handleLoginSuccess}
            onRegisterClick={() => setShowRegistration(true)}
          />
        );
      }
    }
    
    return null;
  };

  return (
    <SessionContextProvider supabaseClient={supabase}>
      <div className="h-screen w-screen bg-black text-white font-sans overflow-hidden">
        <Routes>
          <Route path="/" element={renderAuthScreen()} />
          <Route path="/dashboard" element={<AdminDashboard onLogout={handleLogout} />} />
          <Route path="/chat" element={<ChatWindow onLogout={handleLogout} />} />
          <Route path="/register" element={<APEXRegistration onRegistrationSuccess={handleRegistrationSuccess} onBackToLogin={() => navigate('/')} />} />
        </Routes>
      </div>
    </SessionContextProvider>
  );
};

export default App;
