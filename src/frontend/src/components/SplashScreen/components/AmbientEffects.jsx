import React from "react";
import PropTypes from "prop-types";

/**
 * Background ambient effects for the splash screen
 */
const AmbientEffects = ({ variant = 'default' }) => {
  const variations = {
    default: {
      first: {
        position: "top-1/4 right-1/4", 
        size: "w-96 h-96", 
        color: "bg-green-500",
        animation: "animate-blob"
      },
      second: {
        position: "bottom-1/4 left-1/4", 
        size: "w-96 h-96", 
        color: "bg-green-700",
        animation: "animate-blob animation-delay-2000"
      }
    },
    intense: {
      first: {
        position: "top-1/4 right-1/4", 
        size: "w-[30rem] h-[30rem]", 
        color: "bg-green-500",
        animation: "animate-blob-fast"
      },
      second: {
        position: "bottom-1/4 left-1/4", 
        size: "w-[30rem] h-[30rem]", 
        color: "bg-green-700",
        animation: "animate-blob-fast animation-delay-1000"
      }
    }
  };

  const { first, second } = variations[variant];

  return (
    <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
      <div className={`absolute ${first.position} ${first.size} ${first.color} rounded-full mix-blend-multiply filter blur-[128px] opacity-10 ${first.animation}`} />
      <div className={`absolute ${second.position} ${second.size} ${second.color} rounded-full mix-blend-multiply filter blur-[128px] opacity-10 ${second.animation}`} />
    </div>
  );
};

// הגדרת PropTypes כתחליף לממשק TypeScript
AmbientEffects.propTypes = {
  variant: PropTypes.oneOf(['default', 'intense'])
};

AmbientEffects.defaultProps = {
  variant: 'default'
};

export default AmbientEffects;
