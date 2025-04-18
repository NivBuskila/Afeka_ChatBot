import React, { useState, useEffect } from 'react';
import MatrixBackground from './MatrixBackground';
import LogoContainer from './LogoContainer';
import AnimatedText from './AnimatedText';
import AmbientEffects from './AmbientEffects';


interface APEXSplashScreenProps {
  onSplashComplete: () => void;
}

const APEXSplashScreen: React.FC<APEXSplashScreenProps> = ({ onSplashComplete }) => {
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
      className="relative h-screen bg-black text-white overflow-hidden cursor-pointer"
      onClick={onSplashComplete}
    >
      <MatrixBackground />
      <div className="relative z-10 h-full flex flex-col items-center justify-center">
        <LogoContainer />
        <AnimatedText textVisible={textVisible} showFullName={showFullName} />
        {showFullName && (
          <div className="absolute bottom-12 left-1/2 transform -translate-x-1/2 text-green-400/60 text-sm animate-pulse">
            Click anywhere to continue
          </div>
        )}
      </div>
      <AmbientEffects />
    </div>
  );
};

export default APEXSplashScreen;
