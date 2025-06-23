import React from 'react';
import { Search, Edit, Trash2 } from 'lucide-react';
import { translations } from '../translations';

type Language = 'he' | 'en';

interface Document {
  id: number;
  title: string;
  category: string;
  uploadDate: string;
  size: string;
  status: 'active' | 'archived';
}

interface DocumentTableProps {
  documents: Document[];
  searchQuery: string;
  setSearchQuery: (value: string) => void;
  selectedFilter: string;
  setSelectedFilter: (value: string) => void;
  language: Language;
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
}

const DocumentTable: React.FC<DocumentTableProps> = ({
  documents,
  searchQuery,
  setSearchQuery,
  selectedFilter,
  setSelectedFilter,
  language,
  onEdit,
  onDelete
}) => {
  const t = (key: string) => translations[key]?.[language] || key;
  const getFileType = (title: string, category: string): string => {
    const mimeMap: Record<string, string> = {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'DOCX',
      'application/pdf': 'PDF',
      'text/plain': 'TXT',
      'application/msword': 'DOC'
    };
    if (mimeMap[category]) {
      return mimeMap[category];
    }
    const parts = title.split('.');
    return parts.length > 1 ? parts.pop()!.toUpperCase() : category;
  };

  return (
    <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 shadow-lg">
      <div className="p-4 border-b border-gray-200 dark:border-green-500/10">
        <div className="flex items-center gap-4">
          <div className="relative flex-1">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 dark:text-green-400/50" />
            <input
              type="text"
              placeholder={t('documents.search')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg px-4 py-2 pl-10 text-gray-800 dark:text-white focus:outline-none focus:ring-1 focus:ring-green-500"
            />
          </div>
          <select
            value={selectedFilter}
            onChange={(e) => setSelectedFilter(e.target.value)}
            className="bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg px-4 py-2 text-gray-800 dark:text-white focus:outline-none focus:ring-1 focus:ring-green-500"
          >
            <option value="all">{t('documents.all.categories')}</option>
            <option value="active">{t('documents.status.active')}</option>
            <option value="archived">{t('documents.status.archived')}</option>
          </select>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 dark:border-green-500/10">
              <th className="text-center py-3 px-4 text-gray-700 dark:text-green-400/70">{t('table.document.name')}</th>
              <th className="text-center py-3 px-4 text-gray-700 dark:text-green-400/70">{t('table.category')}</th>
              <th className="text-center py-3 px-4 text-gray-700 dark:text-green-400/70">{t('table.upload.date')}</th>
              <th className="text-center py-3 px-4 text-gray-700 dark:text-green-400/70">{t('table.size')}</th>
              <th className="text-center py-3 px-4 text-gray-700 dark:text-green-400/70">{t('table.status')}</th>
              <th className="text-center py-3 px-4 text-gray-700 dark:text-green-400/70">{t('table.actions')}</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.id} className="border-b border-gray-100 dark:border-green-500/10 hover:bg-gray-50 dark:hover:bg-green-500/5">
                <td className="text-center py-3 px-4 text-gray-800 dark:text-green-300">{doc.title}</td>
                <td className="text-center py-3 px-4 text-gray-700 dark:text-green-400">{getFileType(doc.title, doc.category)}</td>
                <td className="text-center py-3 px-4 text-gray-700 dark:text-green-400">{doc.uploadDate}</td>
                <td className="text-center py-3 px-4 text-gray-700 dark:text-green-400">{doc.size}</td>
                <td className="text-center py-3 px-4">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    doc.status === 'active' 
                      ? 'bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-400' 
                      : 'bg-gray-100 dark:bg-gray-500/20 text-gray-700 dark:text-gray-400'
                  }`}>
                    {doc.status === 'active' ? t('documents.status.active') : t('documents.status.archived')}
                  </span>
                </td>
                <td className="text-center py-3 px-4">
                  <div className="flex items-center justify-center gap-2">
                    <button 
                      onClick={() => onEdit(doc.id)}
                      className="p-1 hover:bg-gray-200 dark:hover:bg-green-500/10 rounded transition-colors"
                    >
                      <Edit className="w-4 h-4 text-gray-600 dark:text-green-400" />
                    </button>
                    <button 
                      onClick={() => onDelete(doc.id)}
                      className="p-1 hover:bg-gray-200 dark:hover:bg-green-500/10 rounded transition-colors"
                    >
                      <Trash2 className="w-4 h-4 text-gray-600 dark:text-green-400" />
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

export default DocumentTable; 