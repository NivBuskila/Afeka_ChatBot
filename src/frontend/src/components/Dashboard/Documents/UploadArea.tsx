import React from 'react';
import { Upload } from 'lucide-react';
import { translations } from '../translations';

type Language = 'he' | 'en';

interface UploadAreaProps {
  language: Language;
}

const UploadArea: React.FC<UploadAreaProps> = ({ language }) => {
  const t = (key: string) => translations[key]?.[language] || key;

  return (
    <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-8">
      <div className="flex flex-col items-center justify-center h-[400px] border-2 border-dashed border-green-500/30 rounded-lg">
        <Upload className="w-12 h-12 text-green-400/50 mb-4" />
        <p className="text-green-400/70 mb-4">{t('documents.drag.drop')}</p>
        <button className="bg-green-500/20 hover:bg-green-500/30 text-green-400 px-6 py-2 rounded-lg border border-green-500/30 transition-colors">
          {t('documents.select.files')}
        </button>
      </div>
    </div>
  );
};

export default UploadArea; 