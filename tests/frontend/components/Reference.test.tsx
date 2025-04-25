import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Reference from '../../../src/frontend/components/Reference';

describe('Reference Component', () => {
  const mockReference = {
    title: 'Test Document',
    url: 'https://example.com/test',
    content: 'This is a test document content.'
  };

  it('renders the reference title', () => {
    render(<Reference reference={mockReference} />);
    
    const titleElement = screen.getByText(mockReference.title);
    expect(titleElement).toBeInTheDocument();
  });

  it('renders a link with the correct URL', () => {
    render(<Reference reference={mockReference} />);
    
    const linkElement = screen.getByRole('link');
    expect(linkElement).toHaveAttribute('href', mockReference.url);
  });

  it('expands to show content when clicked', () => {
    render(<Reference reference={mockReference} />);
    
    // Content should be hidden initially
    expect(screen.queryByText(mockReference.content)).not.toBeInTheDocument();
    
    // Click the reference to expand it
    const referenceElement = screen.getByText(mockReference.title);
    fireEvent.click(referenceElement);
    
    // Check if content is now visible
    expect(screen.getByText(mockReference.content)).toBeInTheDocument();
  });

  it('collapses when clicked again', () => {
    render(<Reference reference={mockReference} />);
    
    // Click to expand
    const referenceElement = screen.getByText(mockReference.title);
    fireEvent.click(referenceElement);
    
    // Content should be visible
    expect(screen.getByText(mockReference.content)).toBeInTheDocument();
    
    // Click again to collapse
    fireEvent.click(referenceElement);
    
    // Content should be hidden again
    expect(screen.queryByText(mockReference.content)).not.toBeInTheDocument();
  });

  it('shows an icon to indicate expandability', () => {
    render(<Reference reference={mockReference} />);
    
    // Check for the presence of an icon
    const iconElement = screen.getByTestId('reference-icon');
    expect(iconElement).toBeInTheDocument();
  });

  it('changes icon when expanded/collapsed', () => {
    render(<Reference reference={mockReference} />);
    
    const iconElement = screen.getByTestId('reference-icon');
    const initialClassName = iconElement.className;
    
    // Click to expand
    const referenceElement = screen.getByText(mockReference.title);
    fireEvent.click(referenceElement);
    
    // Check if icon class changed
    expect(iconElement.className).not.toBe(initialClassName);
    
    // Click to collapse
    fireEvent.click(referenceElement);
    
    // Check if icon class returned to initial state
    expect(iconElement.className).toBe(initialClassName);
  });

  it('handles references without content gracefully', () => {
    const referenceWithoutContent = {
      title: 'No Content Reference',
      url: 'https://example.com/no-content'
    };
    
    render(<Reference reference={referenceWithoutContent} />);
    
    // Click to expand
    const referenceElement = screen.getByText(referenceWithoutContent.title);
    fireEvent.click(referenceElement);
    
    // Should display a message indicating no content
    expect(screen.getByText(/no additional content available/i)).toBeInTheDocument();
  });

  it('handles references without URL gracefully', () => {
    const referenceWithoutUrl = {
      title: 'No URL Reference',
      content: 'This is content without a URL'
    };
    
    render(<Reference reference={referenceWithoutUrl} />);
    
    // Should not render a link tag
    expect(screen.queryByRole('link')).not.toBeInTheDocument();
    
    // Should still display the title as text
    expect(screen.getByText(referenceWithoutUrl.title)).toBeInTheDocument();
  });

  it('applies the correct CSS classes', () => {
    render(<Reference reference={mockReference} />);
    
    const containerElement = screen.getByTestId('reference-container');
    expect(containerElement).toHaveClass('reference-container');
    
    // Click to expand
    const referenceElement = screen.getByText(mockReference.title);
    fireEvent.click(referenceElement);
    
    // Check if expanded class is applied
    expect(containerElement).toHaveClass('expanded');
  });
}); 