import React from 'react';
import { useTranslation } from 'react-i18next';
import { AlertTriangle } from 'lucide-react';
import { ModalWrapper } from './ModalWrapper';

interface UserDeleteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  selectedUser: any;
}

export const UserDeleteModal: React.FC<UserDeleteModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  selectedUser,
}) => {
  const { t } = useTranslation();

  return (
    <ModalWrapper
      isOpen={isOpen}
      onClose={onClose}
      title={t("users.confirmDelete") || "Confirm User Deletion"}
    >
      <div className="flex items-center mb-4 text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/30 p-3 rounded-lg">
        <AlertTriangle className="w-5 h-5 mr-2" />
        <p className="text-sm">
          {t("users.deleteWarning") ||
            "This action cannot be undone. The user will be permanently deleted."}
        </p>
      </div>
      
      <p className="text-gray-600 dark:text-green-400/80 mb-6">
        {t("users.deleteConfirmText") ||
          "Are you sure you want to delete the user:"}{" "}
        <span className="font-semibold text-gray-900 dark:text-green-400">
          {selectedUser?.email || selectedUser?.name || "Unknown User"}
        </span>
        ?
      </p>
      
      <div className="flex justify-end space-x-3">
        <button
          onClick={onClose}
          className="px-4 py-2 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-700 dark:text-green-400 hover:bg-gray-50 dark:hover:bg-green-500/20 transition-colors"
        >
          {t("Cancel")}
        </button>
        <button
          onClick={onConfirm}
          className="px-4 py-2 bg-red-50 dark:bg-red-500/20 border border-red-300 dark:border-red-500/30 rounded-lg text-red-700 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-500/30 transition-colors"
        >
          {t("common.delete")}
        </button>
      </div>
    </ModalWrapper>
  );
}; 