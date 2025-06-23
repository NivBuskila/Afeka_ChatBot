import React, { useRef, useEffect } from 'react';
import { useTheme } from '../../../contexts/ThemeContext';

const LoginBackgroundEffects: React.FC = () => {
  const { theme } = useTheme();
  const canvas = useRef<HTMLCanvasElement>(null);

  // Matrix Rain effect for dark mode
  useEffect(() => {
    if (theme !== 'dark') return;

    let canvasElement = canvas.current;
    
    // Wait a bit after render to ensure canvas exists
    const initTimer = setTimeout(() => {
      canvasElement = canvas.current;
      if (!canvasElement) {
        console.warn('Canvas element not available');
        return;
      }
      
      const ctx = canvasElement.getContext('2d');
      if (!ctx) {
        console.warn('Canvas context not available');
        return;
      }
      
      const updateCanvasSize = () => {
        if (!canvasElement) return;
        canvasElement.width = window.innerWidth;
        canvasElement.height = window.innerHeight;
      };
      
      updateCanvasSize();
      window.addEventListener('resize', updateCanvasSize);
      
      const binary = '01';
      const fontSize = 14;
      
      let columns: number[] = [];
      
      const initColumns = () => {
        if (!canvasElement) return;
        const columnsCount = Math.floor(canvasElement.width / fontSize);
        columns = Array(columnsCount).fill(1);
      };
      
      initColumns();
      
      const draw = () => {
        if (!canvasElement || !ctx || columns.length === 0) return;
        
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvasElement.width, canvasElement.height);
        ctx.fillStyle = '#0f0';
        ctx.font = `${fontSize}px monospace`;
        
        for (let i = 0; i < columns.length; i++) {
          const text = binary.charAt(Math.floor(Math.random() * binary.length));
          ctx.fillText(text, i * fontSize, columns[i] * fontSize);
          columns[i]++;
          if (columns[i] * fontSize > canvasElement.height && Math.random() > 0.975) {
            columns[i] = 0;
          }
        }
      };
      
      const interval = setInterval(draw, 33);
      
      return () => {
        clearInterval(interval);
        window.removeEventListener('resize', updateCanvasSize);
      };
    }, 100); // Small delay to allow render to complete
    
    return () => {
      clearTimeout(initTimer);
    };
  }, [theme]);

  return (
    <>
      {/* Matrix Rain for dark mode */}
      {theme === 'dark' && (
        <canvas
          ref={canvas}
          className="absolute inset-0 opacity-5"
          style={{ zIndex: 0 }}
        />
      )}

      {/* Light mode background effects */}
      {theme === 'light' && (
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
          <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-green-200 rounded-full mix-blend-multiply filter blur-[128px] opacity-20 animate-blob" />
          <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-green-300 rounded-full mix-blend-multiply filter blur-[128px] opacity-15 animate-blob animation-delay-2000" />
        </div>
      )}

      {/* Dark mode background effects */}
      {theme === 'dark' && (
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
          <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-green-500 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob" />
          <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-green-700 rounded-full mix-blend-multiply filter blur-[128px] opacity-10 animate-blob animation-delay-2000" />
        </div>
      )}
    </>
  );
};

export default LoginBackgroundEffects; 