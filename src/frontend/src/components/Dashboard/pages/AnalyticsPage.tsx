import React from "react";
import { useTranslation } from "react-i18next";
import { Trash2 } from "lucide-react";
import { AnalyticsOverview } from "../AnalyticsOverview";
import { Pagination } from "../../common/Pagination";
import { ItemsPerPageSelector } from "../../common/ItemsPerPageSelector";
import TokenUsageAnalytics from "../TokenUsageAnalytics";

type Language = "he" | "en";

interface AnalyticsPageProps {
  activeSubItem: string;
  language: Language;
  analytics: any;
  isRefreshing: boolean;
  usersItemsPerPage: number;
  usersCurrentPage: number;
  adminsItemsPerPage: number;
  adminsCurrentPage: number;
  setUsersItemsPerPage: (value: number) => void;
  setUsersCurrentPage: (value: number) => void;
  setAdminsItemsPerPage: (value: number) => void;
  setAdminsCurrentPage: (value: number) => void;
  handleDeleteUser: (user: any) => void;
}

export const AnalyticsPage: React.FC<AnalyticsPageProps> = ({
  activeSubItem,
  language,
  analytics,
  isRefreshing,
  usersItemsPerPage,
  usersCurrentPage,
  adminsItemsPerPage,
  adminsCurrentPage,
  setUsersItemsPerPage,
  setUsersCurrentPage,
  setAdminsItemsPerPage,
  setAdminsCurrentPage,
  handleDeleteUser,
}) => {
  const { t } = useTranslation();

  if (activeSubItem === "token-usage") {
    return <TokenUsageAnalytics language={language} />;
  }

  if (activeSubItem === "users") {
    // Filter only regular users (not admins)
    const regularUsers = analytics.recentUsers.filter((user: any) => {
      // Check if user is not in the admins list
      return !analytics.recentAdmins?.some(
        (admin: any) => admin.id === user.id
      );
    });

    // Pagination logic for users
    const startIndex = (usersCurrentPage - 1) * usersItemsPerPage;
    const endIndex = startIndex + usersItemsPerPage;
    const paginatedUsers = regularUsers.slice(startIndex, endIndex);

    return (
      <div className="p-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">
            {t("admin.sidebar.users")}
          </h2>
        </div>

        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 shadow-lg">
          {/* Header עם בחירת כמות פריטים */}
          <div className="border-b border-gray-300 dark:border-green-500/20 py-3 px-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-green-600 dark:text-green-400">
                {t("analytics.users")} ({regularUsers.length})
              </h3>

              {regularUsers.length > 10 && (
                <ItemsPerPageSelector
                  itemsPerPage={usersItemsPerPage}
                  onItemsPerPageChange={(newItemsPerPage) => {
                    setUsersItemsPerPage(newItemsPerPage);
                    setUsersCurrentPage(1);
                  }}
                  options={[10, 25, 50, 100]}
                />
              )}
            </div>
          </div>

          <div className="p-6 space-y-4">
            {paginatedUsers && paginatedUsers.length > 0 ? (
              paginatedUsers.map((user: any, index: number) => (
                <div
                  key={user.id || index}
                  className="flex items-center justify-between"
                >
                  <div>
                    <p className="font-medium text-gray-800 dark:text-green-400">
                      {user.email || user.name || "Unknown User"}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-green-400/50">
                      {user.created_at
                        ? new Date(user.created_at).toLocaleDateString()
                        : ""}
                    </p>
                  </div>
                  <div className="flex items-center">
                    <span className="text-sm text-gray-600 dark:text-green-400/70 mr-4">
                      user
                    </span>
                    <button
                      onClick={() => handleDeleteUser(user)}
                      className="p-1 text-red-500 dark:text-red-400 hover:text-red-600 dark:hover:text-red-300 hover:bg-red-100/20 dark:hover:bg-red-500/20 rounded-full transition-colors"
                      title={String(t("common.delete")) || "Delete"}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-600 dark:text-green-400/70">
                {t("analytics.noUsers")}
              </p>
            )}
          </div>

          {/* Pagination */}
          {regularUsers.length > usersItemsPerPage && (
            <div className="px-6 py-3 border-t border-gray-300 dark:border-green-500/20">
              <Pagination
                currentPage={usersCurrentPage}
                totalItems={regularUsers.length}
                itemsPerPage={usersItemsPerPage}
                onPageChange={setUsersCurrentPage}
              />
            </div>
          )}
        </div>
      </div>
    );
  }

  if (activeSubItem === "admins") {
    // Pagination logic for admins
    const adminsStartIndex = (adminsCurrentPage - 1) * adminsItemsPerPage;
    const adminsEndIndex = adminsStartIndex + adminsItemsPerPage;
    const paginatedAdmins = analytics.recentAdmins.slice(
      adminsStartIndex,
      adminsEndIndex
    );

    return (
      <div className="p-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">
            {t("admin.sidebar.administrators")}
          </h2>
        </div>

        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 shadow-lg">
          {/* Header עם בחירת כמות פריטים */}
          <div className="border-b border-gray-300 dark:border-green-500/20 py-3 px-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-green-600 dark:text-green-400">
                {t("analytics.activeAdmins")} ({analytics.recentAdmins.length})
              </h3>

              {analytics.recentAdmins.length > 10 && (
                <ItemsPerPageSelector
                  itemsPerPage={adminsItemsPerPage}
                  onItemsPerPageChange={(newItemsPerPage) => {
                    setAdminsItemsPerPage(newItemsPerPage);
                    setAdminsCurrentPage(1);
                  }}
                  options={[10, 25, 50, 100]}
                />
              )}
            </div>
          </div>

          <div className="p-6 space-y-4">
            {paginatedAdmins && paginatedAdmins.length > 0 ? (
              paginatedAdmins.map((admin: any, index: number) => (
                <div
                  key={admin.id || index}
                  className="flex items-center justify-between"
                >
                  <div>
                    <p className="font-medium text-gray-800 dark:text-green-400">
                      {admin.email || admin.name || "Unknown Admin"}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-green-400/50">
                      {admin.created_at
                        ? new Date(admin.created_at).toLocaleDateString()
                        : ""}
                    </p>
                  </div>
                  <span className="text-sm text-gray-600 dark:text-green-400/70">
                    admin {admin.department ? `(${admin.department})` : ""}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-gray-600 dark:text-green-400/70">
                {t("analytics.noAdmins")}
              </p>
            )}
          </div>

          {/* Pagination */}
          {analytics.recentAdmins.length > adminsItemsPerPage && (
            <div className="px-6 py-3 border-t border-gray-300 dark:border-green-500/20">
              <Pagination
                currentPage={adminsCurrentPage}
                totalItems={analytics.recentAdmins.length}
                itemsPerPage={adminsItemsPerPage}
                onPageChange={setAdminsCurrentPage}
              />
            </div>
          )}
        </div>
      </div>
    );
  }

  // Default: Overview
  return (
    <div>
      <div className="mb-6 px-6 pt-6">
        <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">
          {t("analytics.overview")}
        </h2>
      </div>
      <AnalyticsOverview analytics={analytics} isLoading={isRefreshing} />
    </div>
  );
}; 