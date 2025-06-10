// Theme system with predefined configurations
export const themes = {
  light: {
    // Main backgrounds
    bg: {
      primary: 'bg-white',
      secondary: 'bg-gray-50',
      tertiary: 'bg-gray-100',
      card: 'bg-white',
      modal: 'bg-white',
      sidebar: 'bg-gray-50',
      header: 'bg-white',
      input: 'bg-white',
      hover: 'hover:bg-gray-50',
      active: 'bg-gray-100',
    },
    
    // Text colors
    text: {
      primary: 'text-gray-900',
      secondary: 'text-gray-600',
      tertiary: 'text-gray-500',
      accent: 'text-blue-600',
      success: 'text-green-600',
      warning: 'text-yellow-600',
      error: 'text-red-600',
      muted: 'text-gray-400',
      inverse: 'text-white',
    },
    
    // Borders
    border: {
      primary: 'border-gray-300',
      secondary: 'border-gray-300',
      accent: 'border-blue-500',
      focus: 'focus:border-blue-500',
      hover: 'hover:border-gray-300',
    },
    
    // Buttons
    button: {
      primary: 'bg-blue-600 hover:bg-blue-700 text-white',
      secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-900',
      success: 'bg-green-600 hover:bg-green-700 text-white',
      danger: 'bg-red-600 hover:bg-red-700 text-white',
      warning: 'bg-yellow-500 hover:bg-yellow-600 text-white',
      info: 'bg-blue-500 hover:bg-blue-600 text-white',
      ghost: 'hover:bg-gray-100 text-gray-700',
      outline: 'border border-gray-300 hover:bg-gray-50 text-gray-700',
      link: 'hover:text-blue-700 text-blue-600 underline-offset-4 hover:underline',
      'gradient-primary': 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white',
      'gradient-success': 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white',
    },
    
    // Specific components
    chat: {
      userBubble: 'bg-blue-600 text-white',
      botBubble: 'bg-gray-100 text-gray-900',
      input: 'bg-white border-gray-300 text-gray-900 placeholder-gray-500',
      sidebar: 'bg-gray-50',
    },
    
    // Status indicators
    status: {
      online: 'bg-green-500',
      offline: 'bg-gray-400',
      busy: 'bg-yellow-500',
      error: 'bg-red-500',
    }
  },
  
  dark: {
    // Main backgrounds
    bg: {
      primary: 'bg-black',
      secondary: 'bg-gray-900',
      tertiary: 'bg-gray-800',
      card: 'bg-gray-900',
      modal: 'bg-gray-900',
      sidebar: 'bg-black',
      header: 'bg-black',
      input: 'bg-gray-800',
      hover: 'hover:bg-gray-800',
      active: 'bg-gray-700',
    },
    
    // Text colors
    text: {
      primary: 'text-white',
      secondary: 'text-gray-300',
      tertiary: 'text-gray-400',
      accent: 'text-blue-400',
      success: 'text-green-400',
      warning: 'text-yellow-400',
      error: 'text-red-400',
      muted: 'text-gray-500',
      inverse: 'text-gray-900',
    },
    
    // Borders
    border: {
      primary: 'border-gray-700',
      secondary: 'border-gray-500',
      accent: 'border-blue-500',
      focus: 'focus:border-blue-400',
      hover: 'hover:border-gray-500',
    },
    
    // Buttons
    button: {
      primary: 'bg-blue-600 hover:bg-blue-700 text-white',
      secondary: 'bg-gray-600 hover:bg-gray-700 text-white',
      success: 'bg-green-600 hover:bg-green-700 text-white',
      danger: 'bg-red-600 hover:bg-red-700 text-white',
      warning: 'bg-yellow-500 hover:bg-yellow-600 text-white',
      info: 'bg-blue-500 hover:bg-blue-600 text-white',
      ghost: 'hover:bg-gray-700 text-gray-300',
      outline: 'border border-gray-600 hover:bg-gray-700 text-gray-300',
      link: 'hover:text-blue-400 text-blue-300 underline-offset-4 hover:underline',
      'gradient-primary': 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white',
      'gradient-success': 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white',
    },
    
    // Specific components
    chat: {
      userBubble: 'bg-blue-600 text-white',
      botBubble: 'bg-gray-700 text-gray-100',
      input: 'bg-gray-700 border-gray-600 text-white placeholder-gray-400',
      sidebar: 'bg-black',
    },
    
    // Status indicators
    status: {
      online: 'bg-green-500',
      offline: 'bg-gray-600',
      busy: 'bg-yellow-500',
      error: 'bg-red-500',
    }
  }
} as const;

export type ThemeConfig = typeof themes.light;
export type ThemeVariant = keyof typeof themes;

// Helper function to get theme classes
export const getThemeClasses = (theme: ThemeVariant) => themes[theme];

// Utility function to combine theme classes
export const combineThemeClasses = (...classes: string[]) => {
  return classes.filter(Boolean).join(' ');
}; 