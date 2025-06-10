import React from "react";

const AmbientEffects: React.FC = () => (
  <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
    <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-green-500 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob" />
    <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-green-700 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob animation-delay-2000" />
  </div>
);

export default AmbientEffects; 