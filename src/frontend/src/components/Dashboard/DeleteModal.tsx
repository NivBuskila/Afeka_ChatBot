import React from 'react';
import { useTranslation } from 'react-i18next';
import { AlertTriangle } from 'lucide-react';

interface DeleteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  documentName?: string;
}

export const DeleteModal: React.FC<DeleteModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  documentName
}) => {
  const { t, i18n } = useTranslation();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-black/80 rounded-lg border border-green-500/30 shadow-lg max-w-md w-full mx-4">
        <div className="p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-6 w-6 text-red-400" />
            </div>
            <div className="mr-3">
              <h3 className="text-lg font-medium text-green-400">
                {t('documents.confirmDelete')}
              </h3>
              <div className="mt-2">
                <p className="text-sm text-green-400/70">
                  {documentName 
                    ? i18n.language === 'he' 
                      ? `האם אתה בטוח שברצונך למחוק את "${documentName}"?` 
                      : `Are you sure you want to delete "${documentName}"?`
                    : t('documents.confirmDelete')}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end space-x-3 space-x-reverse p-4 border-t border-green-500/20">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-green-400 bg-black/50 border border-green-500/30 rounded-md hover:bg-green-500/10 transition-colors"
          >
            {t('common.cancel')}
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 text-sm font-medium text-white bg-red-500/30 border border-red-500/30 rounded-md hover:bg-red-500/40 transition-colors"
          >
            {t('common.delete')}
          </button>
        </div>
      </div>
    </div>
  );
}; 