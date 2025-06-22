import React from 'react';
import { useMatrixEffect } from '../hooks/useMatrixEffect';

const MatrixRain: React.FC = () => {
  const canvasRef = useMatrixEffect();

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 opacity-5"
      style={{ zIndex: 0 }}
    />
  );
};

export default MatrixRain; 