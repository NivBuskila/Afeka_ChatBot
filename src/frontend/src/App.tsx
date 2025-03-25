import React, { useState } from 'react';
import APEXSplashScreen from './components/SplashScreen/components/APEXSplashScreen';


import './styles/globals.css';
import './styles/animations.css';

import ChatWindow from './components/Chat/ChatWindow';

const App: React.FC = () => {
  const [isLanding, setIsLanding] = useState(true);

  const handleSplashComplete = (): void => {
    setIsLanding(false);
  };

  return (

    <div className="h-screen w-screen bg-black text-white font-sans overflow-hidden">
      {isLanding ? (
        <APEXSplashScreen onSplashComplete={handleSplashComplete} />
      ) : (
        <ChatWindow />
      )}
    </div>
  );
};

export default App;
