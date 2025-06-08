import React from 'react';
import { useTranslation } from 'react-i18next';
import { FileText, Download, Trash2, Edit } from 'lucide-react';
import type { Document } from '../../config/supabase';
import ProcessingProgressBar from './ProcessingProgressBar';

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
  onEdit
}) => {
  const { t, i18n } = useTranslation();

  const getFileType = (type: string): string => {
    const mimeMap: Record<string, string> = {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'DOCX',
      'application/pdf': 'PDF',
      'text/plain': 'TXT',
      'application/msword': 'DOC'
    };
    
    if (mimeMap[type]) {
      return mimeMap[type];
    }
    
    if (type.includes('/')) {
      return type.split('/')[1];
    }
    
    return type;
  };
  
  const downloadFile = async (url: string, filename: string) => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  const filteredDocuments = documents.filter(doc =>
    doc.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg border border-gray-300 dark:border-green-500/20 rounded-lg shadow-lg">
      <div className="p-4 border-b border-gray-200 dark:border-green-500/20">
        <input
          type="text"
          placeholder={t('documents.search')}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-white focus:outline-none focus:ring-1 focus:ring-green-500"
        />
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-green-500/20">
          <thead className="bg-gray-100 dark:bg-black/50">
            <tr>
              <th className={`px-6 py-3 ${i18n.language === 'en' ? 'text-left' : 'text-right'} text-xs font-medium text-gray-700 dark:text-green-400/80 uppercase tracking-wider w-[30%]`}>
                {t('documents.name')}
              </th>
              <th className={`px-6 py-3 ${i18n.language === 'en' ? 'text-left' : 'text-right'} text-xs font-medium text-gray-700 dark:text-green-400/80 uppercase tracking-wider w-[20%]`}>
                {t('documents.type')}
              </th>
              <th className={`px-6 py-3 ${i18n.language === 'en' ? 'text-left' : 'text-right'} text-xs font-medium text-gray-700 dark:text-green-400/80 uppercase tracking-wider w-[15%]`}>
                {t('documents.size')}
              </th>
              <th className={`px-6 py-3 ${i18n.language === 'en' ? 'text-left' : 'text-right'} text-xs font-medium text-gray-700 dark:text-green-400/80 uppercase tracking-wider w-[20%]`}>
                {t('documents.date')}
              </th>
              <th className={`px-6 py-3 ${i18n.language === 'en' ? 'text-left' : 'text-right'} text-xs font-medium text-gray-700 dark:text-green-400/80 uppercase tracking-wider w-[20%]`}>
                {i18n.language === 'he' ? 'סטטוס' : 'Status'}
              </th>
              <th className={`px-6 py-3 ${i18n.language === 'en' ? 'text-left' : 'text-right'} text-xs font-medium text-gray-700 dark:text-green-400/80 uppercase tracking-wider w-[15%]`}>
                {t('documents.actions')}
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-black/20 divide-y divide-gray-100 dark:divide-green-500/20">
            {filteredDocuments.map((doc) => (
              <tr key={doc.id} className="hover:bg-gray-50 dark:hover:bg-green-500/5 transition-colors">
                <td className={`px-6 py-4 whitespace-nowrap ${i18n.language === 'en' ? 'text-left' : 'text-right'}`}>
                  <div className={`flex items-center ${i18n.language === 'en' ? 'flex-row' : 'flex-row-reverse'}`}>
                    <FileText className="h-5 w-5 text-gray-600 dark:text-green-400/70" />
                    <div className={i18n.language === 'en' ? 'ml-4' : 'mr-4'}>
                      <div className="text-sm font-medium text-gray-800 dark:text-green-400">{doc.name}</div>
                    </div>
                  </div>
                </td>
                <td className={`px-6 py-4 whitespace-nowrap ${i18n.language === 'en' ? 'text-left' : 'text-right'}`}>
                  <div className="text-sm text-gray-700 dark:text-green-400/80">
                    {getFileType(doc.type)}
                  </div>
                </td>
                <td className={`px-6 py-4 whitespace-nowrap ${i18n.language === 'en' ? 'text-left' : 'text-right'}`}>
                  <div className="text-sm text-gray-700 dark:text-green-400/80">
                    {(doc.size / 1024 / 1024).toFixed(2)} MB
                  </div>
                </td>
                <td className={`px-6 py-4 whitespace-nowrap ${i18n.language === 'en' ? 'text-left' : 'text-right'}`}>
                  <div className="text-sm text-gray-700 dark:text-green-400/80">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </div>
                </td>
                <td className={`px-6 py-4 whitespace-nowrap ${i18n.language === 'en' ? 'text-left' : 'text-right'}`}>
                  <ProcessingProgressBar documentId={doc.id} />
                </td>
                <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${i18n.language === 'en' ? 'text-left' : 'text-right'}`}>
                  <div className={`flex items-center ${i18n.language === 'en' ? 'space-x-4' : 'space-x-4 space-x-reverse'}`}>
                    <button
                      onClick={() => downloadFile(doc.url, doc.name)}
                      className="text-gray-600 dark:text-green-400/80 hover:text-gray-800 dark:hover:text-green-400 transition-colors"
                    >
                      <Download className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => onEdit(doc)}
                      className="text-yellow-600 dark:text-yellow-400/80 hover:text-yellow-700 dark:hover:text-yellow-400 transition-colors"
                    >
                      <Edit className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => onDelete(doc)}
                      className="text-red-600 dark:text-red-400/80 hover:text-red-700 dark:hover:text-red-400 transition-colors"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}; 