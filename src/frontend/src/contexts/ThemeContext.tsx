import React, { createContext, useState, useContext, useEffect } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType>({
  theme: 'dark',
  setTheme: () => {},
  toggleTheme: () => {},
});

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Get saved theme or default to dark mode
  const getSavedTheme = (): Theme => {
    const savedTheme = localStorage.getItem('theme');
    console.log('Getting saved theme from localStorage:', savedTheme);
    return (savedTheme === 'light' || savedTheme === 'dark') 
      ? savedTheme 
      : 'dark';
  };

  const [theme, setTheme] = useState<Theme>(getSavedTheme());

  // Apply theme to document
  useEffect(() => {
    console.log('Theme changed to:', theme);
    const root = window.document.documentElement;
    
    if (theme === 'dark') {
      root.classList.add('dark');
      console.log('Added dark class to document root');
    } else {
      root.classList.remove('dark');
      console.log('Removed dark class from document root');
    }
    
    // Save theme to localStorage
    localStorage.setItem('theme', theme);
    console.log('Saved theme to localStorage:', theme);
  }, [theme]);

  const setThemeHandler = (newTheme: Theme) => {
    console.log('setTheme called with:', newTheme);
    setTheme(newTheme);
  };

  const toggleTheme = () => {
    console.log('toggleTheme called, current theme:', theme);
    setTheme(prevTheme => {
      const newTheme = prevTheme === 'light' ? 'dark' : 'light';
      console.log('Toggling from', prevTheme, 'to', newTheme);
      return newTheme;
    });
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme: setThemeHandler, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeProvider; 