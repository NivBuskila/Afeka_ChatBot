import React from "react";
import { useTranslation } from "react-i18next";
import { Plus } from "lucide-react";
import { DocumentTable } from "../DocumentTable";
import { UploadArea } from "../UploadArea";
import type { Document } from "../../../config/supabase";

interface DocumentsPageProps {
  activeSubItem: string;
  documents: Document[];
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  setShowUploadModal: (show: boolean) => void;
  handleEditDocument: (document: Document) => void;
  handleDeleteDocument: (document: Document) => void;
}

export const DocumentsPage: React.FC<DocumentsPageProps> = ({
  activeSubItem,
  documents,
  searchQuery,
  setSearchQuery,
  setShowUploadModal,
  handleEditDocument,
  handleDeleteDocument,
}) => {
  const { t } = useTranslation();

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">
          {activeSubItem === "upload"
            ? t("admin.sidebar.uploadDocuments")
            : t("admin.sidebar.activeDocuments")}
        </h2>
        {activeSubItem === "active" && (
          <button
            onClick={() => setShowUploadModal(true)}
            className="bg-green-500/20 hover:bg-green-500/30 text-green-400 font-medium py-2 px-4 rounded-lg border border-green-500/30 transition-colors flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>{t("documents.add")}</span>
          </button>
        )}
      </div>

      {activeSubItem === "upload" ? (
        <UploadArea onUpload={() => setShowUploadModal(true)} />
      ) : (
        <DocumentTable
          documents={documents}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          onEdit={handleEditDocument}
          onDelete={handleDeleteDocument}
        />
      )}
    </div>
  );
}; 