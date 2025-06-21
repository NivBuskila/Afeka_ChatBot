import React from "react";
import { screen, fireEvent } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from "vitest";
import { render } from "../../utils/test-utils";
import { DeleteModal } from "../../../../../frontend/src/components/Dashboard/DeleteModal";
import { ThemeProvider } from "../../../../../frontend/src/contexts/ThemeContext";

// Mock i18n
vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: Record<string, string> = {
        "documents.confirmDelete": "Confirm Delete",
        "common.cancel": "Cancel",
        "common.delete": "Delete",
      };
      return translations[key] || key;
    },
    i18n: {
      language: "en",
    },
  }),
}));

// Helper component to wrap with ThemeProvider
const TestWrapper: React.FC<{
  children: React.ReactNode;
  initialTheme?: "light" | "dark";
}> = ({ children, initialTheme = "light" }) => {
  // Mock localStorage for theme persistence
  Object.defineProperty(window, "localStorage", {
    value: {
      getItem: vi.fn(() => initialTheme),
      setItem: vi.fn(),
    },
    writable: true,
  });

  return <ThemeProvider>{children}</ThemeProvider>;
};

describe("DeleteModal", () => {
  const mockOnClose = vi.fn();
  const mockOnConfirm = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Theme Support", () => {
    it("should render with light theme styles", () => {
      const { container } = render(
        <TestWrapper initialTheme="light">
          <DeleteModal
            isOpen={true}
            onClose={mockOnClose}
            onConfirm={mockOnConfirm}
            documentName="test.pdf"
          />
        </TestWrapper>
      );

      const modal = container.querySelector(".bg-white");
      const title = screen.getByText("Confirm Delete");

      expect(modal).toBeInTheDocument();
      expect(title).toHaveClass("text-gray-900");
    });

    it("should render with dark theme styles when in dark mode", () => {
      // Set dark mode in localStorage
      Object.defineProperty(window, "localStorage", {
        value: {
          getItem: vi.fn(() => "dark"),
          setItem: vi.fn(),
        },
        writable: true,
      });

      const { container } = render(
        <TestWrapper initialTheme="dark">
          <DeleteModal
            isOpen={true}
            onClose={mockOnClose}
            onConfirm={mockOnConfirm}
            documentName="test.pdf"
          />
        </TestWrapper>
      );

      const modal = container.querySelector(".dark\\:bg-black\\/80");
      const title = screen.getByText("Confirm Delete");

      expect(modal).toBeInTheDocument();
      expect(title).toHaveClass("dark:text-green-400");
    });
  });

  describe("Long Text Handling", () => {
    it("should handle very long document names without overflow", () => {
      const longDocumentName =
        "1747572580_תקנון_הענקת_מלגות_עידוד_לקרובי_משפחה_מדרגה_ראשונה_הלומדים_בו_זמנית_במכללה.pdf";

      render(
        <TestWrapper>
          <DeleteModal
            isOpen={true}
            onClose={mockOnClose}
            onConfirm={mockOnConfirm}
            documentName={longDocumentName}
          />
        </TestWrapper>
      );

      const messageText = screen.getByText(new RegExp(longDocumentName));

      expect(messageText).toBeInTheDocument();
      expect(messageText).toHaveClass("break-words");
      expect(messageText).toHaveClass("leading-relaxed");
    });

    it("should display Hebrew text correctly for long file names", () => {
      const hebrewFileName =
        "קובץ_עם_שם_ארוך_מאוד_שיכול_לגרום_לבעיות_רצאפות_במסך.pdf";

      render(
        <TestWrapper>
          <DeleteModal
            isOpen={true}
            onClose={mockOnClose}
            onConfirm={mockOnConfirm}
            documentName={hebrewFileName}
          />
        </TestWrapper>
      );

      // Check that Hebrew text is handled properly with word breaking
      const textElement = screen.getByText(new RegExp(hebrewFileName));
      expect(textElement).toBeInTheDocument();
      expect(textElement).toHaveClass("break-words");
    });

    it("should maintain proper layout with very long text", () => {
      const { container } = render(
        <TestWrapper>
          <DeleteModal
            isOpen={true}
            onClose={mockOnClose}
            onConfirm={mockOnConfirm}
            documentName={"a".repeat(200) + ".pdf"}
          />
        </TestWrapper>
      );

      const modal = container.querySelector(".max-w-md");
      const textContainer = container.querySelector(".min-w-0.flex-1");

      expect(modal).toBeInTheDocument();
      expect(textContainer).toBeInTheDocument();
    });
  });

  describe("Modal Behavior", () => {
    it("should not render when isOpen is false", () => {
      render(
        <TestWrapper>
          <DeleteModal
            isOpen={false}
            onClose={mockOnClose}
            onConfirm={mockOnConfirm}
          />
        </TestWrapper>
      );

      expect(screen.queryByText("Confirm Delete")).not.toBeInTheDocument();
    });

    it("should call onClose when cancel button is clicked", () => {
      render(
        <TestWrapper>
          <DeleteModal
            isOpen={true}
            onClose={mockOnClose}
            onConfirm={mockOnConfirm}
          />
        </TestWrapper>
      );

      const cancelButton = screen.getByText("Cancel");
      fireEvent.click(cancelButton);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it("should call onConfirm when delete button is clicked", () => {
      render(
        <TestWrapper>
          <DeleteModal
            isOpen={true}
            onClose={mockOnClose}
            onConfirm={mockOnConfirm}
          />
        </TestWrapper>
      );

      const deleteButton = screen.getByText("Delete");
      fireEvent.click(deleteButton);

      expect(mockOnConfirm).toHaveBeenCalledTimes(1);
    });
  });

  describe("Accessibility", () => {
    it("should have proper contrast in both themes", () => {
      const { rerender } = render(
        <TestWrapper initialTheme="light">
          <DeleteModal
            isOpen={true}
            onClose={mockOnClose}
            onConfirm={mockOnConfirm}
            documentName="test.pdf"
          />
        </TestWrapper>
      );

      // Check light theme accessibility
      const lightTitle = screen.getByText("Confirm Delete");
      expect(lightTitle).toHaveClass("text-gray-900");

      // Re-render with dark theme
      rerender(
        <TestWrapper initialTheme="dark">
          <DeleteModal
            isOpen={true}
            onClose={mockOnClose}
            onConfirm={mockOnConfirm}
            documentName="test.pdf"
          />
        </TestWrapper>
      );

      // Check dark theme accessibility
      const darkTitle = screen.getByText("Confirm Delete");
      expect(darkTitle).toHaveClass("dark:text-green-400");
    });

    it("should have proper focus management", () => {
      render(
        <TestWrapper>
          <DeleteModal
            isOpen={true}
            onClose={mockOnClose}
            onConfirm={mockOnConfirm}
          />
        </TestWrapper>
      );

      const cancelButton = screen.getByText("Cancel");
      const deleteButton = screen.getByText("Delete");

      expect(cancelButton).toBeInTheDocument();
      expect(deleteButton).toBeInTheDocument();

      // Both buttons should be focusable
      cancelButton.focus();
      expect(document.activeElement).toBe(cancelButton);

      deleteButton.focus();
      expect(document.activeElement).toBe(deleteButton);
    });
  });
});
