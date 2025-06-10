import { useTheme } from '../contexts/ThemeContext';
import { getThemeClasses, ThemeConfig, combineThemeClasses } from '../styles/theme';

// Custom hook for theme classes
export const useThemeClasses = () => {
  const { theme } = useTheme();
  const themeClasses = getThemeClasses(theme);
  
  return {
    // Direct access to all theme classes
    classes: themeClasses,
    
    // Helper functions for common combinations
    pageBackground: themeClasses.bg.primary,
    cardBackground: themeClasses.bg.card,
    textPrimary: themeClasses.text.primary,
    textSecondary: themeClasses.text.secondary,
    borderPrimary: themeClasses.border.primary,
    
    // Button variants
    primaryButton: themeClasses.button.primary,
    secondaryButton: themeClasses.button.secondary,
    ghostButton: themeClasses.button.ghost,
    
    // Common combinations
    container: combineThemeClasses(
      themeClasses.bg.primary,
      themeClasses.text.primary,
      themeClasses.border.primary
    ),
    
    card: combineThemeClasses(
      themeClasses.bg.card,
      themeClasses.text.primary,
      themeClasses.border.primary,
      'rounded-lg shadow-sm border'
    ),
    
    modal: combineThemeClasses(
      themeClasses.bg.modal,
      themeClasses.text.primary,
      'rounded-lg shadow-xl'
    ),
    
    input: combineThemeClasses(
      themeClasses.bg.input,
      themeClasses.text.primary,
      themeClasses.border.primary,
      themeClasses.border.focus,
      'border rounded-md px-3 py-2 transition-colors'
    ),
    
    // Chat specific
    chatContainer: combineThemeClasses(
      themeClasses.bg.primary,
      themeClasses.text.primary,
      'h-full'
    ),
    
    chatSidebar: combineThemeClasses(
      themeClasses.chat.sidebar,
      themeClasses.text.primary
    ),
    
    chatInput: combineThemeClasses(
      themeClasses.chat.input,
      'rounded-lg px-4 py-2 transition-colors focus:outline-none'
    ),
    
    userMessage: combineThemeClasses(
      themeClasses.chat.userBubble,
      'rounded-lg px-4 py-2 max-w-xs ml-auto'
    ),
    
    botMessage: combineThemeClasses(
      themeClasses.chat.botBubble,
      'rounded-lg px-4 py-2 max-w-xs mr-auto'
    ),
    
    // Helper function to get any specific theme class
    get: (category: keyof ThemeConfig, key: string) => {
      const categoryObj = themeClasses[category] as any;
      return categoryObj?.[key] || '';
    },
    
    // Combine multiple classes with theme awareness
    combine: (...classes: string[]) => combineThemeClasses(...classes),
    
    // Current theme name
    currentTheme: theme,
  };
}; 