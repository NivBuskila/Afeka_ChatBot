import React from "react";
import { useTranslation } from "react-i18next";
import type { Document } from "../../config/supabase";
import { Pagination } from "../common/Pagination";
import { ItemsPerPageSelector } from "../common/ItemsPerPageSelector";
import DocumentRow from "./components/DocumentRow";
import { useDocumentTable } from "./hooks/useDocumentTable";

interface DocumentTableProps {
  documents: Document[];
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  onDelete: (document: Document) => void;
  onEdit: (document: Document) => void;
}

export const DocumentTable: React.FC<DocumentTableProps> = ({
  documents,
  searchQuery,
  setSearchQuery,
  onDelete,
  onEdit,
}) => {
  const { t, i18n } = useTranslation();
  
  const {
    itemsPerPage,
    filteredDocuments,
    paginatedDocuments,
    currentPage,
    setCurrentPage,
    handleItemsPerPageChange,
    downloadFile,
    getFileType,
  } = useDocumentTable({ documents, searchQuery });

  return (
    <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg border border-gray-300 dark:border-green-500/20 rounded-lg shadow-lg">
      {/* Header עם חיפוש ובחירת כמות פריטים */}
      <div className="p-4 border-b border-gray-200 dark:border-green-500/20">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <input
            type="text"
            placeholder={t("documents.search") || "Search documents"}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full sm:flex-1 px-4 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-white focus:outline-none focus:ring-1 focus:ring-green-500"
          />

          <ItemsPerPageSelector
            itemsPerPage={itemsPerPage}
            onItemsPerPageChange={handleItemsPerPageChange}
            options={[10, 25, 50, 100, 250]}
          />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-green-500/20">
          <thead className="bg-gray-100 dark:bg-black/50">
            <tr>
              <th
                className={`px-6 py-3 ${
                  i18n.language === "en" ? "text-left" : "text-right"
                } text-xs font-medium text-gray-700 dark:text-green-400/80 uppercase tracking-wider w-[30%]`}
              >
                {t("documents.name")}
              </th>
              <th
                className={`px-6 py-3 ${
                  i18n.language === "en" ? "text-left" : "text-right"
                } text-xs font-medium text-gray-700 dark:text-green-400/80 uppercase tracking-wider w-[20%]`}
              >
                {t("documents.type")}
              </th>
              <th
                className={`px-6 py-3 ${
                  i18n.language === "en" ? "text-left" : "text-right"
                } text-xs font-medium text-gray-700 dark:text-green-400/80 uppercase tracking-wider w-[15%]`}
              >
                {t("documents.size")}
              </th>
              <th
                className={`px-6 py-3 ${
                  i18n.language === "en" ? "text-left" : "text-right"
                } text-xs font-medium text-gray-700 dark:text-green-400/80 uppercase tracking-wider w-[20%]`}
              >
                {t("documents.date")}
              </th>
              <th
                className={`px-6 py-3 ${
                  i18n.language === "en" ? "text-left" : "text-right"
                } text-xs font-medium text-gray-700 dark:text-green-400/80 uppercase tracking-wider w-[20%]`}
              >
                {i18n.language === "he" ? "סטטוס" : "Status"}
              </th>
              <th
                className={`px-6 py-3 ${
                  i18n.language === "en" ? "text-left" : "text-right"
                } text-xs font-medium text-gray-700 dark:text-green-400/80 uppercase tracking-wider w-[15%]`}
              >
                {t("documents.actions")}
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-black/20 divide-y divide-gray-100 dark:divide-green-500/20">
            {paginatedDocuments.length === 0 ? (
              <tr>
                <td
                  colSpan={6}
                  className="px-6 py-4 text-center text-gray-500 dark:text-green-400/70"
                >
                  {filteredDocuments.length === 0
                    ? documents.length === 0
                      ? "אין מסמכים במערכת"
                      : "לא נמצאו מסמכים התואמים לחיפוש"
                    : "אין מסמכים לעמוד זה"}
                </td>
              </tr>
            ) : (
              paginatedDocuments.map((doc) => (
                <DocumentRow
                  key={doc.id}
                  document={doc}
                  getFileType={getFileType}
                  onDownload={downloadFile}
                  onEdit={onEdit}
                  onDelete={onDelete}
                />
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination בתחתית הטבלה */}
      {filteredDocuments.length > 0 && (
        <div className="px-4 py-3 border-t border-gray-200 dark:border-green-500/20">
          <Pagination
            currentPage={currentPage}
            totalItems={filteredDocuments.length}
            itemsPerPage={itemsPerPage}
            onPageChange={setCurrentPage}
          />
        </div>
      )}
    </div>
  );
};
