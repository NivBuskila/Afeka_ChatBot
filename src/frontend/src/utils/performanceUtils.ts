/**
 * Performance monitoring utilities for AdminDashboard optimization
 */

interface PerformanceMetrics {
  componentName: string;
  renderTime: number;
  timestamp: number;
}

class PerformanceMonitor {
  private metrics: PerformanceMetrics[] = [];
  private isEnabled = process.env.NODE_ENV === 'development';

  /**
   * Start measuring render time
   */
  startMeasure(componentName: string): () => void {
    if (!this.isEnabled) return () => {};

    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      this.metrics.push({
        componentName,
        renderTime,
        timestamp: Date.now()
      });

      // Log slow renders (> 16ms for 60fps)
      if (renderTime > 16) {
        console.warn(`Slow render detected: ${componentName} took ${renderTime.toFixed(2)}ms`);
      }

      // Keep only last 100 measurements
      if (this.metrics.length > 100) {
        this.metrics = this.metrics.slice(-100);
      }
    };
  }

  /**
   * Get performance metrics for a component
   */
  getMetrics(componentName?: string): PerformanceMetrics[] {
    if (componentName) {
      return this.metrics.filter(m => m.componentName === componentName);
    }
    return [...this.metrics];
  }

  /**
   * Get average render time for a component
   */
  getAverageRenderTime(componentName: string): number {
    const componentMetrics = this.getMetrics(componentName);
    if (componentMetrics.length === 0) return 0;
    
    const total = componentMetrics.reduce((sum, metric) => sum + metric.renderTime, 0);
    return total / componentMetrics.length;
  }

  /**
   * Clear all metrics
   */
  clear(): void {
    this.metrics = [];
  }

  /**
   * Log performance summary
   */
  logSummary(): void {
    if (!this.isEnabled || this.metrics.length === 0) return;

    const componentStats = this.metrics.reduce((stats, metric) => {
      if (!stats[metric.componentName]) {
        stats[metric.componentName] = { count: 0, totalTime: 0, maxTime: 0 };
      }
      
      stats[metric.componentName].count++;
      stats[metric.componentName].totalTime += metric.renderTime;
      stats[metric.componentName].maxTime = Math.max(
        stats[metric.componentName].maxTime, 
        metric.renderTime
      );
      
      return stats;
    }, {} as Record<string, { count: number; totalTime: number; maxTime: number }>);

    console.group('🚀 AdminDashboard Performance Summary');
    Object.entries(componentStats).forEach(([component, stats]) => {
      const avgTime = stats.totalTime / stats.count;
      console.log(`${component}: ${stats.count} renders, avg: ${avgTime.toFixed(2)}ms, max: ${stats.maxTime.toFixed(2)}ms`);
    });
    console.groupEnd();
  }
}

// Global performance monitor instance
export const performanceMonitor = new PerformanceMonitor();

/**
 * React hook for measuring component render performance
 */
export const usePerformanceMonitor = (componentName: string) => {
  if (process.env.NODE_ENV !== 'development') {
    return { startMeasure: () => () => {}, logSummary: () => {} };
  }

  return {
    startMeasure: () => performanceMonitor.startMeasure(componentName),
    logSummary: () => performanceMonitor.logSummary(),
  };
};

/**
 * Debounce utility for performance optimization
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

/**
 * Throttle utility for performance optimization
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}; 