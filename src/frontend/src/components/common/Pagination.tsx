import React from 'react';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface PaginationProps {
  currentPage: number;
  totalItems: number;
  itemsPerPage: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalItems,
  itemsPerPage,
  onPageChange,
  className = ''
}) => {
  const { i18n } = useTranslation();
  
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);
  
  // If less than one page, don't show pagination
  if (totalPages <= 1) return null;
  
  const goToFirst = () => onPageChange(1);
  const goToLast = () => onPageChange(totalPages);
  const goToPrevious = () => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1);
    }
  };
  const goToNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1);
    }
  };
  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      onPageChange(page);
    }
  };
  
  // Create visible pages array - improved algorithm for large datasets
  const getVisiblePages = () => {
    const pages = [];
    const maxVisiblePages = 7;
    
    if (totalPages <= maxVisiblePages) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 4) {
        pages.push(1, 2, 3, 4, 5, '...', totalPages);
      } else if (currentPage >= totalPages - 3) {
        pages.push(1, '...', totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
      } else {
        pages.push(1, '...', currentPage - 1, currentPage, currentPage + 1, '...', totalPages);
      }
    }
    
    return pages;
  };
  
  const visiblePages = getVisiblePages();
  const isRTL = i18n.language === 'he';
  
  // Format numbers with commas
  const formatNumber = (num: number): string => {
    return isRTL ? 
      num.toLocaleString('he-IL') : 
      num.toLocaleString('en-US');
  };
  
  return (
    <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : ''} ${className}`}>
      {/* Current items info */}
      <div className="text-sm text-gray-700 dark:text-green-400/70">
        {isRTL ? (
          <>מציג {formatNumber(startItem)}-{formatNumber(endItem)} מתוך {formatNumber(totalItems)} פריטים</>
        ) : (
          <>Showing {formatNumber(startItem)}-{formatNumber(endItem)} of {formatNumber(totalItems)} items</>
        )}
      </div>
      
      {/* Navigation buttons */}
      <div className={`flex items-center ${isRTL ? 'space-x-reverse space-x-1' : 'space-x-1'}`}>
        {/* First page button - only if more than 10 pages */}
        {totalPages > 10 && (
          <button
            onClick={goToFirst}
            disabled={currentPage === 1}
            className={`px-3 py-2 rounded-lg border transition-colors ${
              currentPage === 1
                ? 'bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-600 cursor-not-allowed border-gray-200 dark:border-gray-700'
                : 'bg-white dark:bg-black/50 text-gray-700 dark:text-green-400 hover:bg-gray-50 dark:hover:bg-green-500/10 border-gray-300 dark:border-green-500/30'
            }`}
            title={isRTL ? 'עמוד ראשון' : 'First page'}
          >
            {isRTL ? <ChevronsRight className="w-4 h-4" /> : <ChevronsLeft className="w-4 h-4" />}
          </button>
        )}
        
        {/* Previous page button */}
        <button
          onClick={goToPrevious}
          disabled={currentPage === 1}
          className={`px-3 py-2 rounded-lg border transition-colors ${
            currentPage === 1
              ? 'bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-600 cursor-not-allowed border-gray-200 dark:border-gray-700'
              : 'bg-white dark:bg-black/50 text-gray-700 dark:text-green-400 hover:bg-gray-50 dark:hover:bg-green-500/10 border-gray-300 dark:border-green-500/30'
          }`}
          title={isRTL ? 'עמוד קודם' : 'Previous page'}
        >
          {isRTL ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
        
        {/* Page numbers */}
        {visiblePages.map((page, index) => (
          page === '...' ? (
            <span
              key={`ellipsis-${index}`}
              className="px-3 py-2 text-gray-500 dark:text-green-400/50"
              aria-label={isRTL ? 'עמודים נוספים' : 'More pages'}
            >
              ...
            </span>
          ) : (
            <button
              key={page}
              onClick={() => goToPage(page as number)}
              className={`px-3 py-2 rounded-lg border transition-colors min-w-[2.5rem] ${
                page === currentPage
                  ? 'bg-green-500/20 text-green-600 dark:text-green-400 border-green-500/30 font-medium'
                  : 'bg-white dark:bg-black/50 text-gray-700 dark:text-green-400 hover:bg-gray-50 dark:hover:bg-green-500/10 border-gray-300 dark:border-green-500/30'
              }`}
              aria-label={isRTL ? `עבור לעמוד ${page}` : `Go to page ${page}`}
            >
              {formatNumber(page as number)}
            </button>
          )
        ))}
        
        {/* Next page button */}
        <button
          onClick={goToNext}
          disabled={currentPage === totalPages}
          className={`px-3 py-2 rounded-lg border transition-colors ${
            currentPage === totalPages
              ? 'bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-600 cursor-not-allowed border-gray-200 dark:border-gray-700'
              : 'bg-white dark:bg-black/50 text-gray-700 dark:text-green-400 hover:bg-gray-50 dark:hover:bg-green-500/10 border-gray-300 dark:border-green-500/30'
          }`}
          title={isRTL ? 'עמוד הבא' : 'Next page'}
        >
          {isRTL ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
        
        {/* Last page button - only if more than 10 pages */}
        {totalPages > 10 && (
          <button
            onClick={goToLast}
            disabled={currentPage === totalPages}
            className={`px-3 py-2 rounded-lg border transition-colors ${
              currentPage === totalPages
                ? 'bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-600 cursor-not-allowed border-gray-200 dark:border-gray-700'
                : 'bg-white dark:bg-black/50 text-gray-700 dark:text-green-400 hover:bg-gray-50 dark:hover:bg-green-500/10 border-gray-300 dark:border-green-500/30'
            }`}
            title={isRTL ? 'עמוד אחרון' : 'Last page'}
          >
            {isRTL ? <ChevronsLeft className="w-4 h-4" /> : <ChevronsRight className="w-4 h-4" />}
          </button>
        )}
      </div>
    </div>
  );
};

// Pagination management hook - optimized for large datasets
export const usePagination = (totalItems: number, itemsPerPage: number = 10) => {
  const [currentPage, setCurrentPage] = React.useState(1);
  
  // Calculate items for current page
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  
  // Get paginated items - optimized for large datasets
  const getPaginatedItems = React.useCallback((items: any[]) => {
    return items.slice(startIndex, endIndex);
  }, [startIndex, endIndex]);
  
  // Reset to first page when total items change
  React.useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(1);
    }
  }, [totalItems, itemsPerPage, currentPage, totalPages]);
  
  // Navigation helper functions
  const goToFirst = React.useCallback(() => setCurrentPage(1), []);
  const goToLast = React.useCallback(() => setCurrentPage(totalPages), [totalPages]);
  const goToNext = React.useCallback(() => {
    if (currentPage < totalPages) {
      setCurrentPage(prev => prev + 1);
    }
  }, [currentPage, totalPages]);
  const goToPrevious = React.useCallback(() => {
    if (currentPage > 1) {
      setCurrentPage(prev => prev - 1);
    }
  }, [currentPage]);
  
  return {
    currentPage,
    setCurrentPage,
    getPaginatedItems,
    totalPages,
    startIndex,
    endIndex,
    // Helper functions
    goToFirst,
    goToLast,
    goToNext,
    goToPrevious,
    // Additional useful info
    hasNextPage: currentPage < totalPages,
    hasPreviousPage: currentPage > 1,
    isFirstPage: currentPage === 1,
    isLastPage: currentPage === totalPages
  };
}; 