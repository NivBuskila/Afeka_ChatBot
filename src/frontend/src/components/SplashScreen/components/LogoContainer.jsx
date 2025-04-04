import React from "react";
import { Brain } from "lucide-react";
import PropTypes from "prop-types";

/**
 * Logo container component with animated rings
 */
const LogoContainer = ({ size = 'md' }) => {
  // Size classes based on the size prop
  const sizeClasses = {
    sm: {
      container: 'w-32 h-32',
      icon: 'w-16 h-16',
      outerRing: 'w-32 h-32',
      innerRing: 'w-32 h-32'
    },
    md: {
      container: 'w-48 h-48',
      icon: 'w-24 h-24',
      outerRing: 'w-48 h-48',
      innerRing: 'w-48 h-48'
    },
    lg: {
      container: 'w-64 h-64',
      icon: 'w-32 h-32',
      outerRing: 'w-64 h-64',
      innerRing: 'w-64 h-64'
    }
  };

  const classes = sizeClasses[size];

  return (
    <div className="relative">
      <div className="absolute inset-0 flex items-center justify-center">
        <div className={`${classes.outerRing} border-2 border-green-500/30 rotate-45 transform animate-spin-slow`} />
        <div className={`absolute ${classes.innerRing} border-2 border-green-500/20 -rotate-45 transform animate-spin-reverse`} />
      </div>
      <div className="relative transform hover:scale-105 transition-transform">
        <div className="absolute inset-0 bg-green-500 rounded-full filter blur-xl opacity-20 animate-pulse" />
        <Brain className={`${classes.icon} text-green-400 relative z-10`} />
      </div>
    </div>
  );
};

// הגדרת PropTypes כתחליף לממשק TypeScript
LogoContainer.propTypes = {
  size: PropTypes.oneOf(['sm', 'md', 'lg'])
};

LogoContainer.defaultProps = {
  size: 'md'
};

export default LogoContainer;
