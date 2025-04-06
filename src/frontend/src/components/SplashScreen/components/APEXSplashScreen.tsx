import React, { useState, useEffect, useCallback } from 'react';
import LogoContainer from './LogoContainer';
import AnimatedText from './AnimatedText';
import AmbientEffects from './AmbientEffects';
import { useTranslation } from 'react-i18next';

interface APEXSplashScreenProps {
  onSplashComplete: () => void;
}

/**
 * Custom hook for letter animation
 */
const useLetterAnimation = () => {
  const [showFullName, setShowFullName] = useState(false);
  const [textVisible, setTextVisible] = useState(Array(4).fill(false));

  // Start the animation
  const startAnimation = useCallback(() => {
    // Show each letter one by one
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

    // Show the full name after all letters are shown
    setTimeout(() => {
      setShowFullName(true);
      clearInterval(showLetters);
    }, 2500);
  }, []);

  return { showFullName, textVisible, startAnimation };
};

/**
 * Splash screen component that displays the APEX logo and animation
 */
const APEXSplashScreen: React.FC<APEXSplashScreenProps> = ({ onSplashComplete }) => {
  const { i18n } = useTranslation();
  const { showFullName, textVisible, startAnimation } = useLetterAnimation();

  // Start animation after component mounts
  useEffect(() => {
    const timer = setTimeout(() => {
      startAnimation();
    }, 1000);

    return () => clearTimeout(timer);
  }, [startAnimation]);

  // Continue button text based on language
  const continueText = i18n?.language === 'he' 
    ? 'לחץ בכל מקום להמשיך' 
    : 'Click anywhere to continue';

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
            {continueText}
          </div>
        )}
      </div>
      <AmbientEffects />
    </div>
  );
};

export default APEXSplashScreen;
