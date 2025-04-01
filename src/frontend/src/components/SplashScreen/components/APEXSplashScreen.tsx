import React, { useState, useEffect } from 'react';
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
    setTimeout(() => {
      const showLetters = setInterval(() => {
        setTextVisible((prev) => {
          const newState = [...prev];
          const nextIndex = newState.findIndex((v) => !v);
          if (nextIndex !== -1) {
            newState[nextIndex] = true;
          }
          return newState;
        });
      }, 500);

      setTimeout(() => {
        setShowFullName(true);
        clearInterval(showLetters);
      }, 2500);
    }, 1000);
  }, []);

  return (
    <div
      className="relative h-screen bg-black text-white overflow-hidden cursor-pointer"
      onClick={onSplashComplete}
    >
      
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
