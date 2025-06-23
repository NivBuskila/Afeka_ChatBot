import React from "react";
import { useTranslation } from "react-i18next";
import { AlertTriangle } from "lucide-react";

interface ActiveProfileErrorModalProps {
  isVisible: boolean;
  profileName: string;
  onClose: () => void;
}

const ActiveProfileErrorModal: React.FC<ActiveProfileErrorModalProps> = ({
  isVisible,
  profileName,
  onClose,
}) => {
  const { t } = useTranslation();

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-black/80 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-yellow-500/30 max-w-md w-full shadow-2xl">
        <div className="p-6">
          <div className="flex items-center mb-4">
            <AlertTriangle className="w-6 h-6 text-yellow-600 dark:text-yellow-400 mr-3" />
            <h3 className="text-lg font-semibold text-gray-800 dark:text-yellow-400">
              {t("rag.errors.activeProfileTitle")}
            </h3>
          </div>

          <div className="mb-6">
            <p className="text-gray-700 dark:text-gray-300 mb-3">
              {t("rag.errors.activeProfileMessage", { profileName })}
            </p>
            <div className="bg-yellow-50 dark:bg-yellow-500/10 border border-yellow-200 dark:border-yellow-500/20 rounded p-3">
              <p className="text-sm text-yellow-800 dark:text-yellow-400">
                💡 {t("rag.errors.howToDelete")}
              </p>
              <ol className="text-sm text-yellow-800 dark:text-yellow-400 mt-2 mr-4">
                <li>1. {t("rag.errors.step1")}</li>
                <li>2. {t("rag.errors.step2")}</li>
              </ol>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 text-white bg-yellow-600 hover:bg-yellow-700 dark:bg-yellow-500/20 dark:hover:bg-yellow-500/30 dark:text-yellow-400 border border-yellow-600 dark:border-yellow-500/30 rounded-lg transition-colors"
            >
              {t("rag.errors.understood")}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActiveProfileErrorModal;
