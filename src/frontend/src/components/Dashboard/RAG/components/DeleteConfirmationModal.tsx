import React from 'react';
import { useTranslation } from 'react-i18next';
import { AlertCircle } from 'lucide-react';

interface ModalProfileData {
  id: string;
  name: string;
  isCustom: boolean;
}

interface DeleteConfirmationModalProps {
  isVisible: boolean;
  modalProfileData: ModalProfileData | null;
  isDeletingProfile: string | null;
  onConfirm: () => void;
  onCancel: () => void;
}

const DeleteConfirmationModal: React.FC<DeleteConfirmationModalProps> = ({
  isVisible,
  modalProfileData,
  isDeletingProfile,
  onConfirm,
  onCancel,
}) => {
  const { t } = useTranslation();

  if (!isVisible || !modalProfileData) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-black/80 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-red-500/30 max-w-md w-full shadow-2xl">
        <div className="p-6">
          <div className="flex items-center mb-4">
            <AlertCircle className="w-6 h-6 text-red-600 dark:text-red-400 mr-3" />
            <h3 className="text-lg font-semibold text-gray-800 dark:text-red-400">
              {t("rag.confirmDelete.title") || "אישור מחיקה"}
            </h3>
          </div>
          
          <div className="mb-6">
            <p className="text-gray-700 dark:text-gray-300 mb-3">
              {modalProfileData.isCustom 
                ? (t("rag.confirmDelete.customProfile", { profileName: modalProfileData.name }) || 
                   `האם אתה בטוח שברצונך למחוק את הפרופיל "${modalProfileData.name}"? פעולה זו אינה הפיכה.`)
                : (t("rag.confirmDelete.builtinProfile", { profileName: modalProfileData.name }) || 
                   `האם אתה בטוח שברצונך להסתיר את הפרופיל המובנה "${modalProfileData.name}"? ניתן לשחזר אותו מאוחר יותר.`)
              }
            </p>
            {!modalProfileData.isCustom && (
              <p className="text-sm text-gray-600 dark:text-gray-400 bg-yellow-50 dark:bg-yellow-500/10 border border-yellow-200 dark:border-yellow-500/20 rounded p-3">
                {t("rag.confirmDelete.builtinNote") || 
                 "פרופילים מובנים לא נמחקים לצמיתות - הם רק מוסתרים ויכולים להיות משוחזרים."
                }
              </p>
            )}
          </div>

          <div className="flex justify-end space-x-3">
            <button
              onClick={onCancel}
              disabled={isDeletingProfile === modalProfileData.id}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-600 rounded-lg transition-colors disabled:opacity-50"
            >
              {t("rag.cancel") || "ביטול"}
            </button>
            <button
              onClick={onConfirm}
              disabled={isDeletingProfile === modalProfileData.id}
              className="px-4 py-2 text-white bg-red-600 hover:bg-red-700 dark:bg-red-500/20 dark:hover:bg-red-500/30 dark:text-red-400 border border-red-600 dark:border-red-500/30 rounded-lg transition-colors disabled:opacity-50 flex items-center space-x-2"
            >
              {isDeletingProfile === modalProfileData.id ? (
                <>
                  <div className="w-4 h-4 border-2 border-white dark:border-red-400 border-t-transparent rounded-full animate-spin" />
                  <span>
                    {modalProfileData.isCustom 
                      ? (t("rag.deleting") || "מוחק...")
                      : (t("rag.hiding") || "מסתיר...")
                    }
                  </span>
                </>
              ) : (
                <span>
                  {modalProfileData.isCustom 
                    ? (t("rag.delete") || "מחק")
                    : (t("rag.hide") || "הסתר")
                  }
                </span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DeleteConfirmationModal; 