import React from "react";
import { useTranslation } from "react-i18next";
import PropTypes from "prop-types";

/**
 * The animated APEX logo text
 */
const AnimatedText = ({ textVisible, showFullName }) => {
  const { i18n } = useTranslation();
  
  // APEX acronym explanation based on the current language
  const acronymExplanation = {
    A: i18n?.language === 'he' ? 'אפקה' : 'AFEKAs',
    P: i18n?.language === 'he' ? 'מקצועי' : 'Professional',
    E: i18n?.language === 'he' ? 'הנדסי' : 'Engineering',
    X: i18n?.language === 'he' ? 'חוויה' : 'eXperience'
  };
  
  return (
    <>
      <div className="mt-12 flex items-center space-x-4">
        {["A", "P", "E", "X"].map((letter, index) => (
          <div
            key={letter}
            className={`text-5xl font-bold transition-all duration-500 transform ${
              textVisible[index]
                ? "opacity-100 translate-y-0"
                : "opacity-0 translate-y-10"
            }`}
          >
            <span className="text-green-400">{letter}</span>
          </div>
        ))}
      </div>
      <div
        className={`mt-6 text-lg text-green-400/80 transition-all duration-1000 ${
          showFullName ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
        }`}
      >
        <div className="text-center space-y-1">
          <div>{acronymExplanation.A}</div>
          <div>{acronymExplanation.P}</div>
          <div>{acronymExplanation.E}</div>
          <div>{acronymExplanation.X}</div>
        </div>
      </div>
    </>
  );
};

// הגדרת PropTypes כתחליף לממשק TypeScript
AnimatedText.propTypes = {
  textVisible: PropTypes.arrayOf(PropTypes.bool).isRequired,
  showFullName: PropTypes.bool.isRequired
};

export default AnimatedText;
