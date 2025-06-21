import React from "react";
import { useTranslation } from "react-i18next";
import { AlertTriangle } from "lucide-react";
import { useTheme } from "../../contexts/ThemeContext";

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
  documentName,
}) => {
  const { t, i18n } = useTranslation();
  const { theme } = useTheme();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 px-4">
      <div className="bg-white dark:bg-black/80 rounded-lg border border-gray-300 dark:border-green-500/30 shadow-xl max-w-md w-full">
        <div className="p-6">
          <div className="flex items-start">
            <div className="flex-shrink-0 mt-0.5">
              <AlertTriangle className="h-6 w-6 text-red-600 dark:text-red-400" />
            </div>
            <div className="mr-3 min-w-0 flex-1">
              <h3 className="text-lg font-medium text-gray-900 dark:text-green-400 mb-3">
                {t("documents.confirmDelete")}
              </h3>
              <div className="mt-2">
                <p className="text-sm text-gray-700 dark:text-green-400/70 break-words leading-relaxed">
                  {documentName
                    ? i18n.language === "he"
                      ? `האם אתה בטוח שברצונך למחוק את "${documentName}"?`
                      : `Are you sure you want to delete "${documentName}"?`
                    : t("documents.confirmDelete")}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end space-x-3 space-x-reverse p-4 border-t border-gray-200 dark:border-green-500/20">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-green-400 bg-gray-100 dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-md hover:bg-gray-200 dark:hover:bg-green-500/10 transition-colors"
          >
            {t("common.cancel")}
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 dark:bg-red-500/30 border border-red-600 dark:border-red-500/30 rounded-md hover:bg-red-700 dark:hover:bg-red-500/40 transition-colors"
          >
            {t("common.delete")}
          </button>
        </div>
      </div>
    </div>
  );
};
