import React from 'react';
import { X } from 'lucide-react';
import { translations } from '../translations';

type Language = 'he' | 'en';

interface DeleteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  language: Language;
}

const DeleteModal: React.FC<DeleteModalProps> = ({ isOpen, onClose, onConfirm, language }) => {
  const t = (key: string) => translations[key]?.[language] || key;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-black/90 border border-green-500/20 rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-green-400">{t('modal.delete.title')}</h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-green-500/10 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-green-400/70" />
          </button>
        </div>
        <p className="text-green-400/70 mb-6">
          {t('modal.delete.message')}
        </p>
        <div className="flex justify-end gap-4">
          <button
            onClick={onClose}
            className="px-4 py-2 text-green-400/70 hover:text-green-400 transition-colors"
          >
            {t('modal.delete.cancel')}
          </button>
          <button 
            onClick={onConfirm}
            className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg border border-red-500/30 transition-colors"
          >
            {t('modal.delete.confirm')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteModal; 