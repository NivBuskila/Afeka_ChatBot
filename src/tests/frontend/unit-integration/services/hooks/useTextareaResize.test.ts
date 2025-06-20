import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useRef } from 'react';
import { useTextareaResize } from '../../../src/hooks/useTextareaResize';

// Mock textarea element
const createMockTextarea = (scrollHeight: number = 100) => ({
  style: { height: '' },
  scrollHeight,
  current: null as HTMLTextAreaElement | null,
});

describe('useTextareaResize', () => {
  let mockTextarea: ReturnType<typeof createMockTextarea>;

  beforeEach(() => {
    mockTextarea = createMockTextarea();
  });

  it('should return handleResize function', () => {
    const mockRef = { current: null };
    const { result } = renderHook(() => useTextareaResize(mockRef));

    expect(typeof result.current.handleResize).toBe('function');
  });

  it('should resize textarea based on scroll height', () => {
    const mockElement = {
      style: { height: '' },
      scrollHeight: 80,
    } as HTMLTextAreaElement;

    const mockRef = { current: mockElement };
    const { result } = renderHook(() => useTextareaResize(mockRef, 150));

    result.current.handleResize();

    expect(mockElement.style.height).toBe('80px');
  });

  it('should respect max height limit', () => {
    const mockElement = {
      style: { height: '' },
      scrollHeight: 200,
    } as HTMLTextAreaElement;

    const mockRef = { current: mockElement };
    const { result } = renderHook(() => useTextareaResize(mockRef, 150));

    result.current.handleResize();

    expect(mockElement.style.height).toBe('150px');
  });

  it('should handle null textarea ref', () => {
    const mockRef = { current: null };
    const { result } = renderHook(() => useTextareaResize(mockRef));

    // Should not throw an error
    expect(() => result.current.handleResize()).not.toThrow();
  });

  it('should reset height to auto before calculating', () => {
    const mockElement = {
      style: { height: '50px' },
      scrollHeight: 80,
    } as HTMLTextAreaElement;

    const mockRef = { current: mockElement };
    const { result } = renderHook(() => useTextareaResize(mockRef));

    result.current.handleResize();

    // Should have been set to 'auto' and then to the new height
    expect(mockElement.style.height).toBe('80px');
  });

  it('should use default maxHeight when not provided', () => {
    const mockElement = {
      style: { height: '' },
      scrollHeight: 200,
    } as HTMLTextAreaElement;

    const mockRef = { current: mockElement };
    const { result } = renderHook(() => useTextareaResize(mockRef)); // No maxHeight provided

    result.current.handleResize();

    // Default maxHeight is 150
    expect(mockElement.style.height).toBe('150px');
  });

  it('should handle small content correctly', () => {
    const mockElement = {
      style: { height: '' },
      scrollHeight: 20,
    } as HTMLTextAreaElement;

    const mockRef = { current: mockElement };
    const { result } = renderHook(() => useTextareaResize(mockRef, 150));

    result.current.handleResize();

    expect(mockElement.style.height).toBe('20px');
  });

  it('should update when maxHeight changes', () => {
    const mockElement = {
      style: { height: '' },
      scrollHeight: 100,
    } as HTMLTextAreaElement;

    const mockRef = { current: mockElement };
    const { result, rerender } = renderHook(
      ({ maxHeight }) => useTextareaResize(mockRef, maxHeight),
      { initialProps: { maxHeight: 150 } }
    );

    result.current.handleResize();
    expect(mockElement.style.height).toBe('100px');

    // Change maxHeight to smaller value
    rerender({ maxHeight: 80 });
    result.current.handleResize();
    expect(mockElement.style.height).toBe('80px');
  });
}); 