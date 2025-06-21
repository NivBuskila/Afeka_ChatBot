import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { Trash2, ChevronLeft, ChevronRight } from "lucide-react";

interface User {
  id: number;
  email: string;
  name?: string;
  created_at?: string;
}

interface UserTableProps {
  users: User[];
  onDeleteUser: (user: User) => void;
}

export const UserTable: React.FC<UserTableProps> = ({
  users,
  onDeleteUser,
}) => {
  const { t } = useTranslation();
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Calculate pagination
  const totalPages = Math.ceil(users.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentUsers = users.slice(startIndex, endIndex);

  const goToPage = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const goToPrevious = () => {
    setCurrentPage((prev) => Math.max(1, prev - 1));
  };

  const goToNext = () => {
    setCurrentPage((prev) => Math.min(totalPages, prev + 1));
  };

  return (
    <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20">
      <div className="border-b border-green-500/20 py-3 px-6">
        <h3 className="text-lg font-semibold text-green-400">
          {t("analytics.users")} ({users.length})
        </h3>
      </div>

      <div className="p-6 space-y-4">
        {currentUsers && currentUsers.length > 0 ? (
          currentUsers.map((user, index) => (
            <div
              key={user.id || index}
              className="flex items-center justify-between p-3 bg-black/20 rounded-lg hover:bg-black/30 transition-colors"
            >
              <div>
                <p className="font-medium text-green-400">
                  {user.email || user.name || t("general.noName")}
                </p>
                <p className="text-sm text-green-400/50">
                  {user.created_at
                    ? new Date(user.created_at).toLocaleDateString()
                    : ""}
                </p>
              </div>
              <div className="flex items-center">
                <span className="text-sm text-green-400/70 mr-4">
                  {t("user.role") || "user"}
                </span>
                <button
                  onClick={() => onDeleteUser(user)}
                  className="p-1 text-red-400 hover:text-red-300 hover:bg-red-500/20 rounded-full transition-colors"
                  title={t("common.delete") || "Delete"}
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        ) : (
          <p className="text-green-400/70 text-center py-8">
            {t("analytics.noUsers")}
          </p>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="border-t border-green-500/20 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-green-400/70">
              {t("pagination.showing")} {startIndex + 1}-
              {Math.min(endIndex, users.length)} {t("pagination.of")}{" "}
              {users.length}
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={goToPrevious}
                disabled={currentPage === 1}
                className={`p-2 rounded-lg border transition-colors ${
                  currentPage === 1
                    ? "border-green-500/20 text-green-400/30 cursor-not-allowed"
                    : "border-green-500/30 text-green-400 hover:bg-green-500/10"
                }`}
              >
                <ChevronLeft className="w-4 h-4" />
              </button>

              <div className="flex items-center space-x-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                  (page) => (
                    <button
                      key={page}
                      onClick={() => goToPage(page)}
                      className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                        currentPage === page
                          ? "bg-green-500/20 text-green-400 border border-green-500/40"
                          : "text-green-400/70 hover:bg-green-500/10 hover:text-green-400"
                      }`}
                    >
                      {page}
                    </button>
                  )
                )}
              </div>

              <button
                onClick={goToNext}
                disabled={currentPage === totalPages}
                className={`p-2 rounded-lg border transition-colors ${
                  currentPage === totalPages
                    ? "border-green-500/20 text-green-400/30 cursor-not-allowed"
                    : "border-green-500/30 text-green-400 hover:bg-green-500/10"
                }`}
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
