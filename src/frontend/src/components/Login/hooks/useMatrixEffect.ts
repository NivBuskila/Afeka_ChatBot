import { useEffect, useRef } from 'react';

export function useMatrixEffect() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    let canvasElement = canvasRef.current;
    
    // Wait a bit after render to ensure canvas exists
    const initTimer = setTimeout(() => {
      canvasElement = canvasRef.current;
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
    }, 100);
    
    return () => {
      clearTimeout(initTimer);
    };
  }, []);

  return canvasRef;
} 