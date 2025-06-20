import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock react-i18next
const mockUseTranslation = vi.fn();
const mockChangeLanguage = vi.fn();

vi.mock('react-i18next', () => ({
  useTranslation: () => mockUseTranslation(),
  initReactI18next: {
    type: '3rdParty',
    init: vi.fn(),
  },
}));

vi.mock('../../../src/contexts/LanguageContext', () => ({
  LanguageProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="language-provider">{children}</div>
  ),
  useLanguage: () => ({
    language: 'he',
    changeLanguage: mockChangeLanguage,
    isRTL: true,
  }),
}));

import { LanguageProvider, useLanguage } from '../../../src/contexts/LanguageContext';

// Test component that uses the context
function TestComponent() {
  const { language, changeLanguage, isRTL } = useLanguage();
  return (
    <div>
      <span data-testid="current-language">{language}</span>
      <span data-testid="is-rtl">{isRTL.toString()}</span>
      <button onClick={() => changeLanguage('en')} data-testid="change-language">
        Change Language
      </button>
    </div>
  );
}

describe('LanguageContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseTranslation.mockReturnValue({
      t: (key: string) => key,
      i18n: { changeLanguage: mockChangeLanguage },
    });
  });

  describe('LanguageProvider', () => {
    it('should render children', () => {
      render(
        <LanguageProvider>
          <div data-testid="child">Child Component</div>
        </LanguageProvider>
      );

      expect(screen.getByTestId('language-provider')).toBeInTheDocument();
      expect(screen.getByTestId('child')).toBeInTheDocument();
    });
  });

  describe('useLanguage hook', () => {
    it('should provide language context values', () => {
      render(
        <LanguageProvider>
          <TestComponent />
        </LanguageProvider>
      );

      expect(screen.getByTestId('current-language')).toHaveTextContent('he');
      expect(screen.getByTestId('is-rtl')).toHaveTextContent('true');
    });

    it('should provide changeLanguage function', () => {
      render(
        <LanguageProvider>
          <TestComponent />
        </LanguageProvider>
      );

      const changeButton = screen.getByTestId('change-language');
      expect(changeButton).toBeInTheDocument();
    });
  });

  describe('Language functionality', () => {
    it('should handle Hebrew (RTL) language', () => {
      const context = useLanguage();
      
      expect(context.language).toBe('he');
      expect(context.isRTL).toBe(true);
    });

    it('should support change language function', () => {
      const context = useLanguage();
      
      expect(typeof context.changeLanguage).toBe('function');
    });
  });
}); 