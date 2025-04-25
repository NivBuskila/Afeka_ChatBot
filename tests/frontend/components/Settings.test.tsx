import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import Settings from '../../../src/frontend/components/Settings';

// Mock API if needed
jest.mock('../../../src/frontend/services/api', () => ({
  updateUserSettings: jest.fn().mockResolvedValue({ success: true }),
  getUserSettings: jest.fn().mockResolvedValue({
    theme: 'light',
    language: 'en',
    notifications: true
  })
}));

describe('Settings Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders settings form with correct initial values', async () => {
    render(<Settings />);
    
    // Wait for settings to load
    await waitFor(() => {
      // Check if form elements are present
      expect(screen.getByLabelText(/theme/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/language/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/notifications/i)).toBeInTheDocument();
    });
    
    // Check initial values
    expect(screen.getByLabelText(/theme/i)).toHaveValue('light');
    expect(screen.getByLabelText(/language/i)).toHaveValue('en');
    expect(screen.getByLabelText(/notifications/i)).toBeChecked();
  });

  it('updates theme setting when changed', async () => {
    render(<Settings />);
    
    // Wait for settings to load
    await waitFor(() => {
      expect(screen.getByLabelText(/theme/i)).toBeInTheDocument();
    });
    
    // Change theme to dark
    const themeSelect = screen.getByLabelText(/theme/i);
    await userEvent.selectOptions(themeSelect, 'dark');
    
    // Check if value changed
    expect(themeSelect).toHaveValue('dark');
  });

  it('updates language setting when changed', async () => {
    render(<Settings />);
    
    // Wait for settings to load
    await waitFor(() => {
      expect(screen.getByLabelText(/language/i)).toBeInTheDocument();
    });
    
    // Change language to Hebrew
    const languageSelect = screen.getByLabelText(/language/i);
    await userEvent.selectOptions(languageSelect, 'he');
    
    // Check if value changed
    expect(languageSelect).toHaveValue('he');
  });

  it('updates notification setting when toggled', async () => {
    render(<Settings />);
    
    // Wait for settings to load
    await waitFor(() => {
      expect(screen.getByLabelText(/notifications/i)).toBeInTheDocument();
    });
    
    // Toggle notifications off
    const notificationsCheckbox = screen.getByLabelText(/notifications/i);
    await userEvent.click(notificationsCheckbox);
    
    // Check if value changed
    expect(notificationsCheckbox).not.toBeChecked();
  });

  it('saves settings when save button is clicked', async () => {
    render(<Settings />);
    
    // Wait for settings to load
    await waitFor(() => {
      expect(screen.getByText(/save settings/i)).toBeInTheDocument();
    });
    
    // Change theme
    const themeSelect = screen.getByLabelText(/theme/i);
    await userEvent.selectOptions(themeSelect, 'dark');
    
    // Save settings
    const saveButton = screen.getByText(/save settings/i);
    await userEvent.click(saveButton);
    
    // Check if API was called with updated settings
    await waitFor(() => {
      expect(require('../../../src/frontend/services/api').updateUserSettings).toHaveBeenCalledWith(
        expect.objectContaining({
          theme: 'dark'
        })
      );
    });
    
    // Check for success message
    expect(screen.getByText(/settings saved/i)).toBeInTheDocument();
  });

  it('shows error message when settings save fails', async () => {
    // Mock API to reject
    require('../../../src/frontend/services/api').updateUserSettings.mockRejectedValueOnce(
      new Error('Failed to update settings')
    );
    
    render(<Settings />);
    
    // Wait for settings to load
    await waitFor(() => {
      expect(screen.getByText(/save settings/i)).toBeInTheDocument();
    });
    
    // Save settings
    const saveButton = screen.getByText(/save settings/i);
    await userEvent.click(saveButton);
    
    // Check for error message
    await waitFor(() => {
      expect(screen.getByText(/failed to save settings/i)).toBeInTheDocument();
    });
  });

  it('resets to default settings when reset button is clicked', async () => {
    render(<Settings />);
    
    // Wait for settings to load
    await waitFor(() => {
      expect(screen.getByText(/reset to defaults/i)).toBeInTheDocument();
    });
    
    // Change theme
    const themeSelect = screen.getByLabelText(/theme/i);
    await userEvent.selectOptions(themeSelect, 'dark');
    
    // Reset settings
    const resetButton = screen.getByText(/reset to defaults/i);
    await userEvent.click(resetButton);
    
    // Check if settings were reset
    expect(themeSelect).toHaveValue('light');
  });

  it('shows confirmation dialog before resetting settings', async () => {
    // Mock window.confirm
    const confirmSpy = jest.spyOn(window, 'confirm');
    confirmSpy.mockImplementation(() => true);
    
    render(<Settings />);
    
    // Wait for settings to load
    await waitFor(() => {
      expect(screen.getByText(/reset to defaults/i)).toBeInTheDocument();
    });
    
    // Reset settings
    const resetButton = screen.getByText(/reset to defaults/i);
    await userEvent.click(resetButton);
    
    // Check if confirmation was shown
    expect(confirmSpy).toHaveBeenCalled();
    
    // Clean up
    confirmSpy.mockRestore();
  });
}); 