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
    <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20">
      <div className="p-4 border-b border-green-500/10">
        <div className="flex items-center gap-4">
          <div className="relative flex-1">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-green-400/50" />
            <input
              type="text"
              placeholder={t('documents.search')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-black/50 border border-green-500/30 rounded-lg px-4 py-2 pl-10 text-white focus:outline-none focus:ring-1 focus:ring-green-500/50"
            />
          </div>
          <select
            value={selectedFilter}
            onChange={(e) => setSelectedFilter(e.target.value)}
            className="bg-black/50 border border-green-500/30 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-1 focus:ring-green-500/50"
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
            <tr className="border-b border-green-500/10">
              <th className="text-center py-3 px-4 text-green-400/70">{t('table.document.name')}</th>
              <th className="text-center py-3 px-4 text-green-400/70">{t('table.category')}</th>
              <th className="text-center py-3 px-4 text-green-400/70">{t('table.upload.date')}</th>
              <th className="text-center py-3 px-4 text-green-400/70">{t('table.size')}</th>
              <th className="text-center py-3 px-4 text-green-400/70">{t('table.status')}</th>
              <th className="text-center py-3 px-4 text-green-400/70">{t('table.actions')}</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.id} className="border-b border-green-500/10">
                <td className="text-center py-3 px-4">{doc.title}</td>
                <td className="text-center py-3 px-4">{getFileType(doc.title, doc.category)}</td>
                <td className="text-center py-3 px-4">{doc.uploadDate}</td>
                <td className="text-center py-3 px-4">{doc.size}</td>
                <td className="text-center py-3 px-4">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    doc.status === 'active' 
                      ? 'bg-green-500/20 text-green-400' 
                      : 'bg-gray-500/20 text-gray-400'
                  }`}>
                    {doc.status === 'active' ? t('documents.status.active') : t('documents.status.archived')}
                  </span>
                </td>
                <td className="text-center py-3 px-4">
                  <div className="flex items-center justify-center gap-2">
                    <button 
                      onClick={() => onEdit(doc.id)}
                      className="p-1 hover:bg-green-500/10 rounded"
                    >
                      <Edit className="w-4 h-4 text-green-400" />
                    </button>
                    <button 
                      onClick={() => onDelete(doc.id)}
                      className="p-1 hover:bg-green-500/10 rounded"
                    >
                      <Trash2 className="w-4 h-4 text-green-400" />
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