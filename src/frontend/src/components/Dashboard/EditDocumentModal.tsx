import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { X, Upload, FileText } from 'lucide-react';

// Define Document interface locally to avoid type errors
interface DocumentFile {
  id: number;
  name: string;
  type: string;
  size: number;
  url: string;
  created_at: string;
  updated_at: string;
}

interface EditDocumentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpdate: (document: DocumentFile, file: File) => void;
  document: DocumentFile | null;
}

export const EditDocumentModal: React.FC<EditDocumentModalProps> = ({
  isOpen,
  onClose,
  onUpdate,
  document
}) => {
  const { t, i18n } = useTranslation();
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  if (!isOpen || !document) return null;

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleSubmit = () => {
    if (file && document) {
      onUpdate(document, file);
      setFile(null);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white/90 dark:bg-black/80 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/30 max-w-lg w-full text-gray-800 dark:text-white shadow-2xl">
        <div className="flex items-center justify-between p-4 border-b border-gray-300 dark:border-green-500/30">
          <h2 className="text-xl font-semibold text-green-600 dark:text-green-400">
            {t('documents.edit')}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 dark:text-green-400/70 hover:text-gray-700 dark:hover:text-green-400"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6">
          {/* Current document info */}
          <div className="mb-4 p-4 bg-gray-100 dark:bg-black/50 border border-gray-300 dark:border-green-500/20 rounded-lg">
            <div className="flex items-center gap-3">
              <FileText className="h-6 w-6 text-gray-600 dark:text-green-400/70" />
              <div className="min-w-0 flex-1">
                <p className="font-medium text-gray-800 dark:text-green-400 break-words" title={document.name}>
                  {document.name}
                </p>
                <p className="text-sm text-gray-600 dark:text-green-400/70">
                  {(document.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
          </div>

          <p className="text-sm text-gray-600 dark:text-green-400/80 mb-4">
            {t('documents.replaceInstructions')}
          </p>

          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragging 
                ? 'border-green-500 bg-green-500/10' 
                : 'border-gray-300 dark:border-green-500/30 hover:border-green-500 dark:hover:border-green-500/50'}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => window.document.getElementById('edit-file-input')?.click()}
          >
            <input
              id="edit-file-input"
              type="file"
              className="hidden"
              onChange={handleFileSelect}
              accept=".pdf,.doc,.docx,.xls,.xlsx,.txt"
            />
            <Upload className="w-12 h-12 text-green-600 dark:text-green-400/70 mx-auto mb-4" />
            <p className="text-lg font-medium text-green-600 dark:text-green-400 mb-2">
              {isDragging
                ? (i18n.language === 'he' ? 'שחרר כאן' : 'Drop Here')
                : (i18n.language === 'he' ? 'לחץ או גרור קובץ לכאן' : 'Click or drag file here')}
            </p>
            <p className="text-sm text-gray-600 dark:text-green-400/70">
              {i18n.language === 'he' 
                ? 'פורמטים נתמכים: PDF, DOC, DOCX, XLS, XLSX, TXT' 
                : 'Supported formats: PDF, DOC, DOCX, XLS, XLSX, TXT'}
            </p>
          </div>

          {file && (
            <div className="mt-4 p-4 bg-gray-100 dark:bg-black/50 border border-gray-300 dark:border-green-500/20 rounded-lg">
              <div className="flex items-start justify-between">
                <div className="min-w-0 flex-1 mr-3">
                  <p className="font-medium text-gray-800 dark:text-green-400 break-words leading-tight" title={file.name}>
                    {file.name}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-green-400/70 mt-1">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <button
                  onClick={() => setFile(null)}
                  className="text-red-500 dark:text-red-400/80 hover:text-red-600 dark:hover:text-red-400 flex-shrink-0 mt-1"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end space-x-3 space-x-reverse p-4 border-t border-gray-300 dark:border-green-500/30">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-green-400/80 bg-gray-200 dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-md hover:bg-gray-300 dark:hover:bg-green-500/10"
          >
            {t('common.cancel')}
          </button>
          <button
            onClick={handleSubmit}
            disabled={!file}
            className={`px-4 py-2 text-sm font-medium rounded-md
              ${file
                ? 'bg-green-500 hover:bg-green-600 text-white'
                : 'bg-gray-300 dark:bg-green-500/20 text-gray-500 dark:text-green-400/50 cursor-not-allowed'}`}
          >
            {t('common.update')}
          </button>
        </div>
      </div>
    </div>
  );
};
