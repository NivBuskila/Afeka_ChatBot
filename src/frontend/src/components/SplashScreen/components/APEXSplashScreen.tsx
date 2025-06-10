import React, { useState, useEffect } from 'react';
import LogoContainer from './LogoContainer';
import AnimatedText from './AnimatedText';
import AmbientEffects from './AmbientEffects';
import { useTheme } from '../../../contexts/ThemeContext';


interface APEXSplashScreenProps {
  onSplashComplete: () => void;
}

const APEXSplashScreen: React.FC<APEXSplashScreenProps> = ({ onSplashComplete }) => {
  const { theme } = useTheme();
  const [showFullName, setShowFullName] = useState(false);
  const [textVisible, setTextVisible] = useState(Array(4).fill(false));

  useEffect(() => {
    // Start animation after 1 second
    setTimeout(() => {
      // Show first letter (A) after initial delay
      setTextVisible([true, false, false, false]);
      
      // Show second letter (P) after 500ms
      setTimeout(() => {
        setTextVisible([true, true, false, false]);
        
        // Show third letter (E) after 500ms
        setTimeout(() => {
          setTextVisible([true, true, true, false]);
          
          // Show fourth letter (X) after 500ms
          setTimeout(() => {
            setTextVisible([true, true, true, true]);
            
            // Show full name after all letters are visible
            setTimeout(() => {
              setShowFullName(true);
            }, 500);
          }, 500);
        }, 500);
      }, 500);
    }, 1000);
  }, []);

  return (
    <div
      className={`relative h-screen overflow-hidden cursor-pointer ${
        theme === 'dark' 
          ? 'bg-black text-white' 
          : 'bg-gradient-to-br from-gray-50 to-gray-100 text-gray-900'
      }`}
      onClick={onSplashComplete}
    >
      <div className="relative z-10 h-full flex flex-col items-center justify-center">
        <LogoContainer />
        <AnimatedText textVisible={textVisible} showFullName={showFullName} />
        {showFullName && (
          <div className={`absolute bottom-12 left-1/2 transform -translate-x-1/2 text-sm animate-pulse ${
            theme === 'dark' ? 'text-green-400/60' : 'text-green-600/70'
          }`}>
            Click anywhere to continue
          </div>
        )}
      </div>
      <AmbientEffects />
    </div>
  );
};

export default APEXSplashScreen;
