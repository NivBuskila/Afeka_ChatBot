import React from "react";

interface AnimatedTextProps {
  textVisible: boolean[];
  showFullName: boolean;
}

const AnimatedText: React.FC<AnimatedTextProps> = ({ textVisible, showFullName }) => (
  <div className="flex flex-col items-center mt-8 space-y-6">
    <div className="flex items-center justify-center space-x-4">
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
      className={`text-lg text-green-400/80 transition-all duration-1000 ${
        showFullName ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
      }`}
    >
      <div className="text-center space-y-1">
        <div>AFEKAs</div>
        <div>Professional</div>
        <div>Engineering</div>
        <div>eXperience</div>
      </div>
    </div>
  </div>
);

export default AnimatedText; 