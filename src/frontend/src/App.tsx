import React, { useState } from 'react';
import APEXSplashScreen from './components/SplashScreen/components/APEXSplashScreen';
import './styles/animations.css';
import './styles/index.css';

const App: React.FC = () => {
  const [isLanding, setIsLanding] = useState(true);

  const handleSplashComplete = (): void => {
    setIsLanding(false);
  };

  return (
    <div className="min-h-screen w-full bg-black text-white overflow-hidden font-sans">
      {isLanding ? (
        // מסך הנחיתה
        <APEXSplashScreen onSplashComplete={handleSplashComplete} />
      ) : (
        // המסך הבא
        <div className="flex items-center justify-center min-h-screen text-green-400">
          <div className="text-xl">Chat Interface Coming Soon</div>
        </div>
      )}
    </div>
  );
};

export default App;
