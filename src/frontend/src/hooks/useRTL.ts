import { useTranslation } from 'react-i18next';
import { useMemo } from 'react';

/**
 * Custom hook for RTL (Right-to-Left) support
 * Provides consistent RTL logic across the entire application
 */
export const useRTL = () => {
  const { i18n } = useTranslation();
  
  const isRTL = useMemo(() => i18n.language === 'he', [i18n.language]);
  const direction = useMemo(() => isRTL ? 'rtl' : 'ltr', [isRTL]);
  const textAlign = useMemo(() => isRTL ? 'text-right' : 'text-left', [isRTL]);
  const textAlignClass = useMemo(() => isRTL ? 'text-right' : 'text-left', [isRTL]);
  
  // Flex direction utilities
  const flexRowReverse = useMemo(() => isRTL ? 'flex-row-reverse' : '', [isRTL]);
  const flexDirection = useMemo(() => isRTL ? 'flex-row-reverse' : 'flex-row', [isRTL]);
  
  // Spacing utilities for RTL
  const marginLeft = useMemo(() => isRTL ? 'mr' : 'ml', [isRTL]);
  const marginRight = useMemo(() => isRTL ? 'ml' : 'mr', [isRTL]);
  const paddingLeft = useMemo(() => isRTL ? 'pr' : 'pl', [isRTL]);
  const paddingRight = useMemo(() => isRTL ? 'pl' : 'pr', [isRTL]);
  
  // Position utilities for RTL
  const left = useMemo(() => isRTL ? 'right' : 'left', [isRTL]);
  const right = useMemo(() => isRTL ? 'left' : 'right', [isRTL]);
  const leftClass = useMemo(() => isRTL ? 'right-' : 'left-', [isRTL]);
  const rightClass = useMemo(() => isRTL ? 'left-' : 'right-', [isRTL]);
  
  // Space utilities for Tailwind CSS
  const spaceX = useMemo(() => isRTL ? 'space-x-reverse' : '', [isRTL]);
  const spaceXClass = (spacing: string) => isRTL ? `space-x-reverse ${spacing}` : spacing;
  
  // Border utilities
  const borderLeft = useMemo(() => isRTL ? 'border-r' : 'border-l', [isRTL]);
  const borderRight = useMemo(() => isRTL ? 'border-l' : 'border-r', [isRTL]);
  
  // Transform utilities for icons that need flipping in RTL
  const flipIcon = useMemo(() => isRTL ? 'transform scale-x-[-1]' : '', [isRTL]);
  
  // Utility function to get direction-aware class
  const dirClass = (ltrClass: string, rtlClass: string) => isRTL ? rtlClass : ltrClass;
  
  // Utility function to get spacing class with RTL awareness
  const spacingClass = (prefix: 'ml' | 'mr' | 'pl' | 'pr', value: string) => {
    const map = {
      'ml': isRTL ? 'mr' : 'ml',
      'mr': isRTL ? 'ml' : 'mr', 
      'pl': isRTL ? 'pr' : 'pl',
      'pr': isRTL ? 'pl' : 'pr'
    };
    return `${map[prefix]}-${value}`;
  };
  
  return {
    // Core RTL properties
    isRTL,
    direction,
    textAlign,
    textAlignClass,
    
    // Flex utilities
    flexRowReverse,
    flexDirection,
    
    // Spacing utilities
    marginLeft,
    marginRight,
    paddingLeft,
    paddingRight,
    spacingClass,
    
    // Position utilities
    left,
    right,
    leftClass,
    rightClass,
    
    // Space utilities
    spaceX,
    spaceXClass,
    
    // Border utilities
    borderLeft,
    borderRight,
    
    // Transform utilities
    flipIcon,
    
    // Helper functions
    dirClass
  };
};

export default useRTL; 