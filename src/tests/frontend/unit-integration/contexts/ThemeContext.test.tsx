import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, renderHook, act } from '@testing-library/react';
import { ReactNode } from 'react';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Import after mocking
import { ThemeProvider, useTheme } from '../../src/contexts/ThemeContext';

// Helper component to test context
const TestComponent = ({ children }: { children?: ReactNode }) => (
  <ThemeProvider>{children}</ThemeProvider>
);

describe('ThemeContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock document.documentElement
    Object.defineProperty(document, 'documentElement', {
      value: {
        classList: {
          add: vi.fn(),
          remove: vi.fn(),
        },
      },
      configurable: true,
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('ThemeProvider', () => {
    it('should initialize with dark theme by default', () => {
      localStorageMock.getItem.mockReturnValue(null);

      const { result } = renderHook(() => useTheme(), {
        wrapper: TestComponent,
      });

      expect(result.current.theme).toBe('dark');
    });

    it('should initialize with saved theme from localStorage', () => {
      localStorageMock.getItem.mockReturnValue('light');

      const { result } = renderHook(() => useTheme(), {
        wrapper: TestComponent,
      });

      expect(result.current.theme).toBe('light');
      expect(localStorageMock.getItem).toHaveBeenCalledWith('theme');
    });

    it('should apply dark class to document root on mount', () => {
      localStorageMock.getItem.mockReturnValue('dark');

      renderHook(() => useTheme(), {
        wrapper: TestComponent,
      });

      expect(document.documentElement.classList.add).toHaveBeenCalledWith('dark');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'dark');
    });
  });

  describe('toggleTheme', () => {
    it('should toggle from dark to light', () => {
      localStorageMock.getItem.mockReturnValue('dark');

      const { result } = renderHook(() => useTheme(), {
        wrapper: TestComponent,
      });

      expect(result.current.theme).toBe('dark');

      act(() => {
        result.current.toggleTheme();
      });

      expect(result.current.theme).toBe('light');
      expect(document.documentElement.classList.remove).toHaveBeenCalledWith('dark');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'light');
    });

    it('should toggle from light to dark', () => {
      localStorageMock.getItem.mockReturnValue('light');

      const { result } = renderHook(() => useTheme(), {
        wrapper: TestComponent,
      });

      expect(result.current.theme).toBe('light');

      act(() => {
        result.current.toggleTheme();
      });

      expect(result.current.theme).toBe('dark');
      expect(document.documentElement.classList.add).toHaveBeenCalledWith('dark');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'dark');
    });
  });
}); 