import { RefObject, useCallback } from 'react';

export const useTextareaResize = (
  textareaRef: RefObject<HTMLTextAreaElement>,
  maxHeight: number = 150
) => {
  // Handle resizing the textarea
  const handleResize = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    
    // Reset height to calculate the new scroll height
    textarea.style.height = 'auto';
    
    // Set the new height based on scroll height (with max height limit)
    const newHeight = Math.min(textarea.scrollHeight, maxHeight);
    textarea.style.height = `${newHeight}px`;
  }, [textareaRef, maxHeight]);

  return { handleResize };
}; 