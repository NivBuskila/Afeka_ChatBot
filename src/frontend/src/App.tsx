import React, { useState, useEffect } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
import { SessionContextProvider } from "@supabase/auth-helpers-react";
import { supabase } from "./config/supabase";
import { useTranslation } from "react-i18next";
import { CheckCircle } from "lucide-react";
import "./i18n/config";
import { useThemeClasses } from './hooks/useThemeClasses';

import APEXSplashScreen from "./components/SplashScreen/components/APEXSplashScreen";
import APEXStaticLogin from "./components/Login/APEXStaticLogin";
import APEXRegistration from "./components/Login/APEXRegistration";
import { AdminDashboard } from "./components/Dashboard/AdminDashboard";
import ChatWindow from "./components/Chat/ChatWindow";
import TermsAndConditions from "./components/Terms/TermsAndConditions";
import ResetPassword from "./components/ResetPassword/ResetPassword";
import LoadingScreen from "./components/LoadingScreen";

import "./styles/globals.css";

const App: React.FC = () => {
  const [isLanding, setIsLanding] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [showRegistration, setShowRegistration] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [successMessage, setSuccessMessage] = useState<string>("");
  const navigate = useNavigate();
  const { i18n } = useTranslation();
  const { currentTheme, pageBackground, textPrimary } = useThemeClasses();

  // Check initial session when app loads
  useEffect(() => {
    const checkInitialAuth = async () => {
      try {
        const {
          data: { session },
          error,
        } = await supabase.auth.getSession();

        if (error) {
          setIsCheckingAuth(false);
          return;
        }

        if (session && session.user) {
          // Check if user is admin
          const { data: adminData } = await supabase
            .from("admins")
            .select("id")
            .eq("user_id", session.user.id)
            .maybeSingle();

          const isAdminUser = !!adminData;
          setIsLoggedIn(true);
          setIsAdmin(isAdminUser);
          setIsLanding(false); // Skip splash screen if already logged in

          // Navigate to appropriate route
          if (isAdminUser) {
            navigate("/dashboard");
          } else {
            navigate("/chat");
          }
        }
      } catch (error) {
        // Silent fail
      } finally {
        setIsCheckingAuth(false);
      }
    };

    checkInitialAuth();
  }, [navigate]);

  useEffect(() => {
    // Set initial language direction
    document.documentElement.dir = i18n.language === "he" ? "rtl" : "ltr";
    document.documentElement.lang = i18n.language;
  }, [i18n.language]);

  // If still checking auth, show loading screen
  if (isCheckingAuth) {
    return (
      <LoadingScreen
        message={
          i18n.language === "he" ? "בודק הרשאות..." : "Checking permissions..."
        }
        subMessage={
          i18n.language === "he" ? "מתחבר למערכת..." : "Connecting to system..."
        }
      />
    );
  }

  const handleSplashComplete = () => {
    setIsLanding(false);
  };

  const handleLoginSuccess = (isAdminUser: boolean) => {
    setIsLoggedIn(true);
    setIsAdmin(isAdminUser);

    if (isAdminUser) {
      navigate("/dashboard");
    } else {
      navigate("/chat");
    }
  };

  const handleRegistrationSuccess = () => {
    setShowRegistration(false);
    showSuccessMessage(
      i18n.language === "he"
        ? "הרישום בוצע בהצלחה! אנא התחבר עם פרטי המשתמש שיצרת"
        : "Registration successful! Please login with your credentials"
    );
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setIsAdmin(false);
    supabase.auth.signOut();
    navigate("/");
  };

  // Show success message function
  const showSuccessMessage = (message: string) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(""), 4000);
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
      <div className={`h-screen w-screen font-sans overflow-auto ${pageBackground} ${textPrimary} ${currentTheme === 'dark' ? 'dark' : ''}`}>
        {/* Success message */}
        {successMessage && (
          <div className="fixed top-4 right-4 z-50 bg-green-50 border-l-4 border-green-500 p-4 rounded shadow-md max-w-md animate-fadeIn">
            <div className="flex items-center">
              <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
              <p className="text-green-700">{successMessage}</p>
            </div>
          </div>
        )}
        <Routes>
          <Route path="/" element={renderAuthScreen()} />
          <Route
            path="/dashboard"
            element={isAdmin ? <AdminDashboard onLogout={handleLogout} /> : <ChatWindow onLogout={handleLogout} />}
          />
          <Route
            path="/chat"
            element={<ChatWindow onLogout={handleLogout} />}
          />
          <Route
            path="/register"
            element={
              <APEXRegistration
                onRegistrationSuccess={handleRegistrationSuccess}
                onBackToLogin={() => navigate("/")}
              />
            }
          />
          <Route
            path="/terms-and-conditions"
            element={<TermsAndConditions />}
          />
          <Route path="/reset-password" element={<ResetPassword />} />
        </Routes>
      </div>
    </SessionContextProvider>
  );
};

export default App;
