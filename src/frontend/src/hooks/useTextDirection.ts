import { useState, useEffect, useMemo } from 'react';

/**
 * Hook for automatic text direction detection
 * Detects if text is RTL (Hebrew/Arabic) or LTR (English/other languages)
 */
export const useTextDirection = (text: string = '') => {
  const [dynamicDirection, setDynamicDirection] = useState<'rtl' | 'ltr'>('ltr');

  // Hebrew Unicode ranges: \u0590-\u05FF (Hebrew), \u200F (RTL Mark)
  // Arabic Unicode ranges: \u0600-\u06FF, \u0750-\u077F, \u08A0-\u08FF
  const isRTLText = useMemo(() => {
    if (!text.trim()) return false;
    
    // Count RTL characters (Hebrew and Arabic)
    const rtlRegex = /[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/g;
    const rtlMatches = text.match(rtlRegex) || [];
    
    // Count LTR characters (Latin, numbers, etc.)
    const ltrRegex = /[A-Za-z0-9]/g;
    const ltrMatches = text.match(ltrRegex) || [];
    
    // If we have RTL characters and they're more than or equal to LTR, use RTL
    if (rtlMatches.length > 0) {
      return rtlMatches.length >= ltrMatches.length;
    }
    
    return false;
  }, [text]);

  useEffect(() => {
    const newDirection = isRTLText ? 'rtl' : 'ltr';
    setDynamicDirection(newDirection);
  }, [isRTLText]);

  // Helper function to get text alignment based on detected direction
  const getTextAlign = () => {
    return dynamicDirection === 'rtl' ? 'text-right' : 'text-left';
  };

  // Helper function to get padding direction for input with button
  const getInputPadding = (hasButton: boolean = false) => {
    if (!hasButton) return '';
    return dynamicDirection === 'rtl' ? 'pl-14' : 'pr-14';
  };

  // Helper function to get button position
  const getButtonPosition = () => {
    return dynamicDirection === 'rtl' ? 'left-3' : 'right-3';
  };

  return {
    direction: dynamicDirection,
    isRTL: dynamicDirection === 'rtl',
    textAlign: getTextAlign(),
    inputPadding: getInputPadding,
    buttonPosition: getButtonPosition,
    detectDirection: (inputText: string) => {
      const rtlRegex = /[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/g;
      const rtlMatches = inputText.match(rtlRegex) || [];
      const ltrRegex = /[A-Za-z0-9]/g;
      const ltrMatches = inputText.match(ltrRegex) || [];
      
      if (rtlMatches.length > 0) {
        return rtlMatches.length >= ltrMatches.length ? 'rtl' : 'ltr';
      }
      return 'ltr';
    }
  };
}; 