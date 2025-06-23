import React from 'react';
import { useRTL } from '../../hooks/useRTL';

interface ItemsPerPageSelectorProps {
  itemsPerPage: number;
  onItemsPerPageChange: (itemsPerPage: number) => void;
  options?: number[];
  className?: string;
}

export const ItemsPerPageSelector: React.FC<ItemsPerPageSelectorProps> = ({
  itemsPerPage,
  onItemsPerPageChange,
  options = [10, 25, 50, 100, 250, 500],
  className = ''
}) => {
  const { isRTL, spaceXClass } = useRTL();
  
  return (
    <div className={`flex items-center ${spaceXClass('space-x-2')} ${className}`}>
      <label className="text-sm text-gray-700 dark:text-green-400/70 whitespace-nowrap">
        {isRTL ? 'פריטים לעמוד:' : 'Items per page:'}
      </label>
      <select
        value={itemsPerPage}
        onChange={(e) => onItemsPerPageChange(Number(e.target.value))}
        className="bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg px-3 py-1 text-sm text-gray-800 dark:text-green-400 focus:outline-none focus:ring-1 focus:ring-green-500 min-w-[70px]"
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
}; 