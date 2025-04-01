import React, { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Upload, FileText } from 'lucide-react';
import { useDropzone } from 'react-dropzone';

interface UploadAreaProps {
  onUpload: (file: File) => void;
}

export const UploadArea: React.FC<UploadAreaProps> = ({ onUpload }) => {
  const { t } = useTranslation();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0]);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/plain': ['.txt']
    },
    maxFiles: 1
  });

  return (
    <div className="bg-black/30 backdrop-blur-lg border border-green-500/20 rounded-lg p-6">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-green-500 bg-green-500/10' : 'border-green-500/30 hover:border-green-500/50'}`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center">
          <Upload className="w-12 h-12 text-green-400 mb-4" />
          <p className="text-lg font-medium text-green-400 mb-2">
            {isDragActive
              ? t('documents.dropHere')
              : t('documents.uploadInstructions')}
          </p>
          <p className="text-sm text-green-400/70">
            {t('documents.supportedFormats')}
          </p>
        </div>
      </div>

      <div className="mt-6">
        <h3 className="text-lg font-medium text-green-400 mb-4">
          {t('documents.supportedTypes', 'Supported File Types')}
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {['PDF', 'DOC', 'DOCX', 'XLS', 'XLSX', 'TXT'].map((type) => (
            <div
              key={type}
              className="flex items-center space-x-2 space-x-reverse p-3 bg-black/50 rounded-lg"
            >
              <FileText className="w-5 h-5 text-green-400/70" />
              <span className="text-sm text-green-400/80">{type}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}; 