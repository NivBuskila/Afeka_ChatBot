import { useState } from 'react';
import type { Document } from '../../../config/supabase';
import { usePagination } from '../../common/Pagination';

interface UseDocumentTableProps {
  documents: Document[];
  searchQuery: string;
}

export function useDocumentTable({ documents, searchQuery }: UseDocumentTableProps) {
  const [itemsPerPage, setItemsPerPage] = useState(10);

  // Filter documents by search query
  const filteredDocuments = documents.filter(
    (doc) =>
      doc?.name?.toLowerCase()?.includes(searchQuery.toLowerCase()) || false
  );

  // Use pagination hook with dynamic itemsPerPage
  const { currentPage, setCurrentPage, getPaginatedItems } = usePagination(
    filteredDocuments.length,
    itemsPerPage
  );

  // Get documents for current page
  const paginatedDocuments = getPaginatedItems(filteredDocuments);

  // Handle items per page change
  const handleItemsPerPageChange = (newItemsPerPage: number) => {
    setItemsPerPage(newItemsPerPage);
    setCurrentPage(1); // Return to first page
  };

  const downloadFile = async (url: string, filename: string) => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error("Error downloading file:", error);
    }
  };

  const getFileType = (type: string): string => {
    const mimeMap: Record<string, string> = {
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
      "application/pdf": "PDF",
      "text/plain": "TXT",
      "application/msword": "DOC",
    };

    if (mimeMap[type]) {
      return mimeMap[type];
    }

    if (type.includes("/")) {
      return type.split("/")[1];
    }

    return type;
  };

  return {
    itemsPerPage,
    filteredDocuments,
    paginatedDocuments,
    currentPage,
    setCurrentPage,
    handleItemsPerPageChange,
    downloadFile,
    getFileType,
  };
} 