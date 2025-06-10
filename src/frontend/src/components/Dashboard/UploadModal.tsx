import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { X, Upload } from 'lucide-react';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (file: File) => void;
}

export const UploadModal: React.FC<UploadModalProps> = ({
  isOpen,
  onClose,
  onUpload
}) => {
  const { t, i18n } = useTranslation();
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  if (!isOpen) return null;

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
    if (file) {
      onUpload(file);
      setFile(null);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white/90 dark:bg-black/80 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/30 max-w-lg w-full text-gray-800 dark:text-white shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-gray-300 dark:border-green-500/30">
          <h2 className="text-xl font-semibold text-green-600 dark:text-green-400 truncate mr-4">
            {i18n.language === 'he' ? 'העלאת מסמך' : 'Upload Document'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 dark:text-green-400/70 hover:text-gray-700 dark:hover:text-green-400 flex-shrink-0"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(100vh-200px)]">
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragging 
                ? 'border-green-500 bg-green-500/10' 
                : 'border-gray-300 dark:border-green-500/30 hover:border-green-500 dark:hover:border-green-500/50'}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input')?.click()}
          >
            <input
              id="file-input"
              type="file"
              className="hidden"
              onChange={handleFileSelect}
              accept=".pdf,.doc,.docx,.xls,.xlsx,.txt"
            />
            <Upload className="w-12 h-12 text-green-600 dark:text-green-400/70 mx-auto mb-4" />
            <p className="text-lg font-medium text-green-600 dark:text-green-400 mb-2 break-words">
              {isDragging
                ? (i18n.language === 'he' ? 'שחרר כאן' : 'Drop Here')
                : (i18n.language === 'he' ? 'לחץ או גרור קובץ לכאן' : 'Click or drag file here')}
            </p>
            <p className="text-sm text-gray-600 dark:text-green-400/70 break-words">
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
            {i18n.language === 'he' ? 'ביטול' : 'Cancel'}
          </button>
          <button
            onClick={handleSubmit}
            disabled={!file}
            className={`px-4 py-2 text-sm font-medium rounded-md
              ${file
                ? 'bg-green-500 hover:bg-green-600 text-white'
                : 'bg-gray-300 dark:bg-green-500/20 text-gray-500 dark:text-green-400/50 cursor-not-allowed'}`}
          >
            {i18n.language === 'he' ? 'העלאה' : 'Upload'}
          </button>
        </div>
      </div>
    </div>
  );
}; 