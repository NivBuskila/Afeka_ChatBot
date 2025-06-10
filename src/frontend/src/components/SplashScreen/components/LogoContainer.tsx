import React from "react";
import { Brain } from "lucide-react";

const LogoContainer: React.FC = () => (
  <div className="relative">
    <div className="absolute inset-0 flex items-center justify-center">
      <div className="w-48 h-48 border-2 border-green-500/30 rotate-45 transform animate-spin-slow" />
      <div className="absolute w-48 h-48 border-2 border-green-500/20 -rotate-45 transform animate-spin-reverse" />
    </div>
    <div className="relative transform hover:scale-105 transition-transform">
      <div className="absolute inset-0 bg-green-500 rounded-full filter blur-xl opacity-20 animate-pulse" />
      <Brain className="w-24 h-24 text-green-400 relative z-10" />
    </div>
  </div>
);

export default LogoContainer; 