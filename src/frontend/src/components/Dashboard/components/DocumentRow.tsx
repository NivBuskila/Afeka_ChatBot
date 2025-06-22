import React from 'react';
import { useTranslation } from 'react-i18next';
import { FileText, Download, Edit, Trash2 } from 'lucide-react';
import type { Document } from '../../../config/supabase';
import ProcessingProgressBar from '../ProcessingProgressBar';

interface DocumentRowProps {
  document: Document;
  getFileType: (type: string) => string;
  onDownload: (url: string, filename: string) => void;
  onEdit: (document: Document) => void;
  onDelete: (document: Document) => void;
}

const DocumentRow: React.FC<DocumentRowProps> = ({
  document,
  getFileType,
  onDownload,
  onEdit,
  onDelete,
}) => {
  const { i18n } = useTranslation();

  return (
    <tr className="hover:bg-gray-50 dark:hover:bg-green-500/5 transition-colors">
      <td
        className={`px-6 py-4 whitespace-nowrap ${
          i18n.language === "en" ? "text-left" : "text-right"
        }`}
      >
        <div
          className={`flex items-center ${
            i18n.language === "en" ? "flex-row" : "flex-row-reverse"
          }`}
        >
          <FileText className="h-5 w-5 text-gray-600 dark:text-green-400/70" />
          <div className={i18n.language === "en" ? "ml-4" : "mr-4"}>
            <div className="text-sm font-medium text-gray-800 dark:text-green-400">
              {document.name}
            </div>
          </div>
        </div>
      </td>
      <td
        className={`px-6 py-4 whitespace-nowrap ${
          i18n.language === "en" ? "text-left" : "text-right"
        }`}
      >
        <div className="text-sm text-gray-700 dark:text-green-400/80">
          {getFileType(document.type)}
        </div>
      </td>
      <td
        className={`px-6 py-4 whitespace-nowrap ${
          i18n.language === "en" ? "text-left" : "text-right"
        }`}
      >
        <div className="text-sm text-gray-700 dark:text-green-400/80">
          {(document.size / 1024 / 1024).toFixed(2)} MB
        </div>
      </td>
      <td
        className={`px-6 py-4 whitespace-nowrap ${
          i18n.language === "en" ? "text-left" : "text-right"
        }`}
      >
        <div className="text-sm text-gray-700 dark:text-green-400/80">
          {new Date(document.created_at).toLocaleDateString()}
        </div>
      </td>
      <td
        className={`px-6 py-4 whitespace-nowrap ${
          i18n.language === "en" ? "text-left" : "text-right"
        }`}
      >
        <ProcessingProgressBar documentId={document.id} />
      </td>
      <td
        className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
          i18n.language === "en" ? "text-left" : "text-right"
        }`}
      >
        <div
          className={`flex items-center ${
            i18n.language === "en"
              ? "space-x-4"
              : "space-x-4 space-x-reverse"
          }`}
        >
          <button
            onClick={() => onDownload(document.url, document.name)}
            className="text-gray-600 dark:text-green-400/80 hover:text-gray-800 dark:hover:text-green-400 transition-colors"
          >
            <Download className="h-5 w-5" />
          </button>
          <button
            onClick={() => onEdit(document)}
            className="text-yellow-600 dark:text-yellow-400/80 hover:text-yellow-700 dark:hover:text-yellow-400 transition-colors"
          >
            <Edit className="h-5 w-5" />
          </button>
          <button
            onClick={() => onDelete(document)}
            className="text-red-600 dark:text-red-400/80 hover:text-red-700 dark:hover:text-red-400 transition-colors"
          >
            <Trash2 className="h-5 w-5" />
          </button>
        </div>
      </td>
    </tr>
  );
};

export default DocumentRow; 