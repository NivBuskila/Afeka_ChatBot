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
  const { t } = useTranslation();
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
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-black/80 backdrop-blur-lg rounded-lg border border-green-500/30 max-w-md w-full mx-4 text-white">
        <div className="flex items-center justify-between p-4 border-b border-green-500/30">
          <h2 className="text-xl font-semibold text-green-400">
            {t('documents.upload')}
          </h2>
          <button
            onClick={onClose}
            className="text-green-400/70 hover:text-green-400"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6">
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragging ? 'border-green-500 bg-green-500/10' : 'border-green-500/30 hover:border-green-500/50'}`}
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
            <Upload className="w-12 h-12 text-green-400/70 mx-auto mb-4" />
            <p className="text-lg font-medium text-green-400 mb-2">
              {isDragging
                ? t('documents.dropHere')
                : t('documents.uploadInstructions')}
            </p>
            <p className="text-sm text-green-400/70">
              {t('documents.supportedFormats')}
            </p>
          </div>

          {file && (
            <div className="mt-4 p-4 bg-black/50 border border-green-500/20 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-green-400">{file.name}</p>
                  <p className="text-sm text-green-400/70">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <button
                  onClick={() => setFile(null)}
                  className="text-red-400/80 hover:text-red-400"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end space-x-3 space-x-reverse p-4 border-t border-green-500/30">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-green-400/80 bg-black/50 border border-green-500/30 rounded-md hover:bg-green-500/10"
          >
            {t('common.cancel')}
          </button>
          <button
            onClick={handleSubmit}
            disabled={!file}
            className={`px-4 py-2 text-sm font-medium text-white rounded-md
              ${file
                ? 'bg-green-500/70 hover:bg-green-500/90'
                : 'bg-green-500/20 text-green-400/50 cursor-not-allowed'}`}
          >
            {t('documents.upload')}
          </button>
        </div>
      </div>
    </div>
  );
}; 