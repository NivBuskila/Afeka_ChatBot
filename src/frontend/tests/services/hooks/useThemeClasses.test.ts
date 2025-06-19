import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook } from '@testing-library/react';

// Mock ThemeContext
const mockUseTheme = vi.fn();
vi.mock('../../../src/contexts/ThemeContext', () => ({
  useTheme: () => mockUseTheme(),
}));

// Mock theme utilities with factory function
vi.mock('../../../src/styles/theme', () => {
  const mockGetThemeClasses = vi.fn();
  const mockCombineThemeClasses = vi.fn();
  
  return {
    getThemeClasses: mockGetThemeClasses,
    combineThemeClasses: mockCombineThemeClasses,
  };
});

import { useThemeClasses } from '../../../src/hooks/useThemeClasses';
import { getThemeClasses, combineThemeClasses } from '../../../src/styles/theme';

const mockGetThemeClasses = getThemeClasses as ReturnType<typeof vi.fn>;
const mockCombineThemeClasses = combineThemeClasses as ReturnType<typeof vi.fn>;

describe('useThemeClasses', () => {
  const mockThemeClasses = {
    bg: {
      primary: 'bg-white',
      card: 'bg-gray-50',
      modal: 'bg-white',
      input: 'bg-white',
    },
    text: {
      primary: 'text-gray-900',
      secondary: 'text-gray-600',
    },
    border: {
      primary: 'border-gray-200',
      focus: 'focus:border-blue-500',
    },
    button: {
      primary: 'bg-blue-600 text-white',
      secondary: 'bg-gray-200 text-gray-900',
      ghost: 'bg-transparent text-blue-600',
    },
    chat: {
      sidebar: 'bg-gray-100',
      input: 'bg-white border-gray-300',
      userBubble: 'bg-blue-600 text-white',
      botBubble: 'bg-gray-200 text-gray-900',
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
    
    mockUseTheme.mockReturnValue({ theme: 'light' });
    mockGetThemeClasses.mockReturnValue(mockThemeClasses);
    mockCombineThemeClasses.mockImplementation((...classes) => classes.join(' '));
  });

  it('should return theme classes and utilities', () => {
    const { result } = renderHook(() => useThemeClasses());

    expect(result.current.classes).toEqual(mockThemeClasses);
    expect(result.current.currentTheme).toBe('light');
  });

  it('should provide direct access to common theme properties', () => {
    const { result } = renderHook(() => useThemeClasses());

    expect(result.current.pageBackground).toBe('bg-white');
    expect(result.current.cardBackground).toBe('bg-gray-50');
    expect(result.current.textPrimary).toBe('text-gray-900');
    expect(result.current.textSecondary).toBe('text-gray-600');
    expect(result.current.borderPrimary).toBe('border-gray-200');
  });

  it('should provide button variants', () => {
    const { result } = renderHook(() => useThemeClasses());

    expect(result.current.primaryButton).toBe('bg-blue-600 text-white');
    expect(result.current.secondaryButton).toBe('bg-gray-200 text-gray-900');
    expect(result.current.ghostButton).toBe('bg-transparent text-blue-600');
  });

  it('should provide combined theme classes', () => {
    const { result } = renderHook(() => useThemeClasses());

    expect(typeof result.current.container).toBe('string');
    expect(typeof result.current.card).toBe('string');
    expect(typeof result.current.modal).toBe('string');
    expect(typeof result.current.input).toBe('string');
  });

  it('should provide chat-specific classes', () => {
    const { result } = renderHook(() => useThemeClasses());

    expect(typeof result.current.chatContainer).toBe('string');
    expect(typeof result.current.chatSidebar).toBe('string');
    expect(typeof result.current.chatInput).toBe('string');
    expect(typeof result.current.userMessage).toBe('string');
    expect(typeof result.current.botMessage).toBe('string');
  });

  it('should provide get function for accessing specific classes', () => {
    const { result } = renderHook(() => useThemeClasses());

    const bgPrimary = result.current.get('bg', 'primary');
    expect(bgPrimary).toBe('bg-white');

    const textSecondary = result.current.get('text', 'secondary');
    expect(textSecondary).toBe('text-gray-600');
  });

  it('should handle get function with non-existent keys', () => {
    const { result } = renderHook(() => useThemeClasses());

    const nonExistent = result.current.get('bg', 'nonexistent');
    expect(nonExistent).toBe('');
  });

  it('should provide combine function', () => {
    const { result } = renderHook(() => useThemeClasses());

    const combined = result.current.combine('class1', 'class2', 'class3');
    expect(combined).toBe('class1 class2 class3');
    expect(mockCombineThemeClasses).toHaveBeenCalledWith('class1', 'class2', 'class3');
  });

  it('should update when theme changes', () => {
    const { result, rerender } = renderHook(() => useThemeClasses());

    expect(result.current.currentTheme).toBe('light');

    // Change theme
    mockUseTheme.mockReturnValue({ theme: 'dark' });
    rerender();

    expect(result.current.currentTheme).toBe('dark');
    expect(mockGetThemeClasses).toHaveBeenCalledWith('dark');
  });

  it('should call getThemeClasses with correct theme', () => {
    renderHook(() => useThemeClasses());

    expect(mockGetThemeClasses).toHaveBeenCalledWith('light');
  });

  it('should handle theme classes for different categories', () => {
    const { result } = renderHook(() => useThemeClasses());

    // Test background classes
    expect(result.current.classes.bg.primary).toBe('bg-white');
    expect(result.current.classes.bg.card).toBe('bg-gray-50');

    // Test text classes
    expect(result.current.classes.text.primary).toBe('text-gray-900');
    expect(result.current.classes.text.secondary).toBe('text-gray-600');

    // Test button classes
    expect(result.current.classes.button.primary).toBe('bg-blue-600 text-white');
    expect(result.current.classes.button.secondary).toBe('bg-gray-200 text-gray-900');

    // Test chat classes
    expect(result.current.classes.chat.userBubble).toBe('bg-blue-600 text-white');
    expect(result.current.classes.chat.botBubble).toBe('bg-gray-200 text-gray-900');
  });
}); 