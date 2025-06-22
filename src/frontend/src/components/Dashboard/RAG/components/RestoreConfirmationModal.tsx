import React from 'react';
import { useTranslation } from 'react-i18next';
import { RotateCcw } from 'lucide-react';

interface ModalProfileData {
  id: string;
  name: string;
  isCustom: boolean;
}

interface RestoreConfirmationModalProps {
  isVisible: boolean;
  modalProfileData: ModalProfileData | null;
  isRestoringProfile: string | null;
  onConfirm: () => void;
  onCancel: () => void;
}

const RestoreConfirmationModal: React.FC<RestoreConfirmationModalProps> = ({
  isVisible,
  modalProfileData,
  isRestoringProfile,
  onConfirm,
  onCancel,
}) => {
  const { t } = useTranslation();

  if (!isVisible || !modalProfileData) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-black/80 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-orange-500/30 max-w-md w-full shadow-2xl">
        <div className="p-6">
          <div className="flex items-center mb-4">
            <RotateCcw className="w-6 h-6 text-orange-600 dark:text-orange-400 mr-3" />
            <h3 className="text-lg font-semibold text-gray-800 dark:text-orange-400">
              {t("rag.confirmRestore.title") || "אישור שחזור"}
            </h3>
          </div>
          
          <div className="mb-6">
            <p className="text-gray-700 dark:text-gray-300 mb-3">
              {t("rag.confirmRestore.message", { profileName: modalProfileData.name }) || 
               `האם אתה בטוח שברצונך לשחזר את הפרופיל "${modalProfileData.name}"?`
              }
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400 bg-orange-50 dark:bg-orange-500/10 border border-orange-200 dark:border-orange-500/20 rounded p-3">
              {t("rag.confirmRestore.note") || 
               "הפרופיל יחזור להיות זמין ברשימת הפרופילים הפעילים."
              }
            </p>
          </div>

          <div className="flex justify-end space-x-3">
            <button
              onClick={onCancel}
              disabled={isRestoringProfile === modalProfileData.id}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-600 rounded-lg transition-colors disabled:opacity-50"
            >
              {t("rag.cancel") || "ביטול"}
            </button>
            <button
              onClick={onConfirm}
              disabled={isRestoringProfile === modalProfileData.id}
              className="px-4 py-2 text-white bg-orange-600 hover:bg-orange-700 dark:bg-orange-500/20 dark:hover:bg-orange-500/30 dark:text-orange-400 border border-orange-600 dark:border-orange-500/30 rounded-lg transition-colors disabled:opacity-50 flex items-center space-x-2"
            >
              {isRestoringProfile === modalProfileData.id ? (
                <>
                  <div className="w-4 h-4 border-2 border-white dark:border-orange-400 border-t-transparent rounded-full animate-spin" />
                  <span>{t("rag.restoring") || "משחזר..."}</span>
                </>
              ) : (
                <>
                  <RotateCcw className="w-4 h-4" />
                  <span>{t("rag.restore") || "שחזר"}</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RestoreConfirmationModal; 