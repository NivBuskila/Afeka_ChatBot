import React from 'react';
import { X, Upload } from 'lucide-react';
import { translations } from '../translations';

type Language = 'he' | 'en';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  language: Language;
}

const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose, language }) => {
  const t = (key: string) => translations[key]?.[language] || key;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-black/90 border border-green-500/20 rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-green-400">{t('modal.upload.title')}</h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-green-500/10 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-green-400/70" />
          </button>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-green-400/70 mb-2">{t('modal.upload.document.name')}</label>
            <input
              type="text"
              className="w-full bg-black/50 border border-green-500/30 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-1 focus:ring-green-500/50"
            />
          </div>
          <div>
            <label className="block text-green-400/70 mb-2">{t('modal.upload.category')}</label>
            <select className="w-full bg-black/50 border border-green-500/30 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-1 focus:ring-green-500/50">
              <option value="תקנונים">{t('category.regulations')}</option>
              <option value="מדריכים">{t('category.guides')}</option>
              <option value="לוחות זמנים">{t('category.schedules')}</option>
            </select>
          </div>
          <div>
            <label className="block text-green-400/70 mb-2">{t('modal.upload.file')}</label>
            <div className="border-2 border-dashed border-green-500/30 rounded-lg p-4 text-center">
              <Upload className="w-8 h-8 text-green-400/50 mx-auto mb-2" />
              <p className="text-green-400/70 mb-2">{t('modal.upload.drag.file')}</p>
              <button className="bg-green-500/20 hover:bg-green-500/30 text-green-400 px-4 py-2 rounded-lg border border-green-500/30 transition-colors">
                {t('modal.upload.select.file')}
              </button>
            </div>
          </div>
        </div>
        <div className="flex justify-end gap-4 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 text-green-400/70 hover:text-green-400 transition-colors"
          >
            {t('modal.upload.cancel')}
          </button>
          <button className="px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg border border-green-500/30 transition-colors">
            {t('modal.upload.submit')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadModal; 