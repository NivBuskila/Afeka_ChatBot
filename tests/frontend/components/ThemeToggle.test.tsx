import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import ThemeToggle from '../../../src/frontend/components/ThemeToggle';

// Mock theme context
const mockSetTheme = jest.fn();
jest.mock('../../../src/frontend/context/ThemeContext', () => ({
  useTheme: () => ({
    theme: 'light',
    setTheme: mockSetTheme
  })
}));

describe('ThemeToggle Component', () => {
  beforeEach(() => {
    mockSetTheme.mockClear();
    // Reset document theme class before each test
    document.documentElement.classList.remove('dark');
  });

  it('renders the theme toggle button', () => {
    render(<ThemeToggle />);
    
    // Check if toggle button is rendered
    const toggleButton = screen.getByTestId('theme-toggle');
    expect(toggleButton).toBeInTheDocument();
  });

  it('displays the correct icon for light theme', () => {
    render(<ThemeToggle />);
    
    // Check if sun icon or light theme indicator is visible
    const lightIcon = screen.getByTestId('light-theme-icon');
    expect(lightIcon).toBeInTheDocument();
    
    // Dark icon should not be visible
    expect(screen.queryByTestId('dark-theme-icon')).not.toBeInTheDocument();
  });

  it('switches to dark theme when clicked in light mode', async () => {
    render(<ThemeToggle />);
    
    // Click the toggle button
    const toggleButton = screen.getByTestId('theme-toggle');
    await userEvent.click(toggleButton);
    
    // Check if setTheme was called with 'dark'
    expect(mockSetTheme).toHaveBeenCalledWith('dark');
  });

  it('has the correct aria-label for accessibility', () => {
    render(<ThemeToggle />);
    
    const toggleButton = screen.getByTestId('theme-toggle');
    expect(toggleButton).toHaveAttribute('aria-label', 'Toggle dark mode');
  });

  it('applies appropriate styles', () => {
    render(<ThemeToggle />);
    
    const toggleButton = screen.getByTestId('theme-toggle');
    
    // Check if button has expected classes for styling
    expect(toggleButton).toHaveClass('theme-toggle-button');
  });
});

// Test with dark theme active
describe('ThemeToggle Component with Dark Theme', () => {
  beforeEach(() => {
    mockSetTheme.mockClear();
    // Mock theme context for dark theme
    jest.resetModules();
    jest.mock('../../../src/frontend/context/ThemeContext', () => ({
      useTheme: () => ({
        theme: 'dark',
        setTheme: mockSetTheme
      })
    }));
    
    // Add dark class to document
    document.documentElement.classList.add('dark');
  });

  it('displays the correct icon for dark theme', () => {
    render(<ThemeToggle />);
    
    // Check if moon icon or dark theme indicator is visible
    const darkIcon = screen.getByTestId('dark-theme-icon');
    expect(darkIcon).toBeInTheDocument();
    
    // Light icon should not be visible
    expect(screen.queryByTestId('light-theme-icon')).not.toBeInTheDocument();
  });

  it('switches to light theme when clicked in dark mode', async () => {
    render(<ThemeToggle />);
    
    // Click the toggle button
    const toggleButton = screen.getByTestId('theme-toggle');
    await userEvent.click(toggleButton);
    
    // Check if setTheme was called with 'light'
    expect(mockSetTheme).toHaveBeenCalledWith('light');
  });
}); 