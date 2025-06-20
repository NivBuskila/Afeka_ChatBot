import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import {
  Trash2,
  Plus,
  X,
  AlertTriangle,
  CheckCircle,
  AlertCircle,
  Sun,
  Moon,
  Globe,
} from "lucide-react";
import "./AdminDashboard.css";
import ChatWindow from "../Chat/ChatWindow";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { AnalyticsOverview } from "./AnalyticsOverview";
import { DocumentTable } from "./DocumentTable";
import { UploadArea } from "./UploadArea";
import { UploadModal } from "./UploadModal";
import { EditDocumentModal } from "./EditDocumentModal";
import { DeleteModal } from "./DeleteModal";
import { RAGManagement } from "./RAG/RAGManagement";
import { documentService } from "../../services/documentService";
import { userService } from "../../services/userService";
import {
  analyticsService,
  DashboardAnalytics,
} from "../../services/analyticsService";
import { Pagination } from "../common/Pagination";
import { ItemsPerPageSelector } from "../common/ItemsPerPageSelector";
import { useTheme } from "../../contexts/ThemeContext";
import TokenUsageAnalytics from "./TokenUsageAnalytics";
import type { Document } from "../../config/supabase";
import { supabase } from "../../config/supabase";
import { cacheService } from "../../services/cacheService";
import LoadingScreen from "../LoadingScreen";

type Language = "he" | "en";

interface AdminDashboardProps {
  onLogout: () => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ onLogout }) => {
  const { t, i18n } = useTranslation();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [activeItem, setActiveItem] = useState("chatbot");
  const [activeSubItem, setActiveSubItem] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showDeleteUserModal, setShowDeleteUserModal] = useState(false);
  const [showEditDocumentModal, setShowEditDocumentModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<any>(null);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(
    null
  );
  const [documents, setDocuments] = useState<Document[]>([]);
  const [analytics, setAnalytics] = useState<DashboardAnalytics>({
    totalDocuments: 0,
    totalUsers: 0,
    totalAdmins: 0,
    recentDocuments: [],
    recentUsers: [],
    recentAdmins: [],
  });
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [language, setLanguage] = useState<Language>(i18n.language as Language);
  const { theme, setTheme } = useTheme();

  // הוספת מערכת הודעות
  const [successMessage, setSuccessMessage] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string>("");

  // Pagination state for users and admins
  const [usersItemsPerPage, setUsersItemsPerPage] = useState(10);
  const [usersCurrentPage, setUsersCurrentPage] = useState(1);
  const [adminsItemsPerPage, setAdminsItemsPerPage] = useState(10);
  const [adminsCurrentPage, setAdminsCurrentPage] = useState(1);

  // פונקציות להצגת הודעות
  const showSuccessMessage = (message: string) => {
    setSuccessMessage(message);
    setErrorMessage("");
    // הסתרת ההודעה אחרי 3 שניות
    setTimeout(() => setSuccessMessage(""), 3000);
  };

  const showErrorMessage = (message: string) => {
    setErrorMessage(message);
    setSuccessMessage("");
    // הסתרת ההודעה אחרי 5 שניות
    setTimeout(() => setErrorMessage(""), 5000);
  };

  // Pagination reset effects
  useEffect(() => {
    const regularUsers = analytics.recentUsers.filter((user) => {
      return !analytics.recentAdmins?.some((admin) => admin.id === user.id);
    });
    const totalPages = Math.ceil(regularUsers.length / usersItemsPerPage);
    if (usersCurrentPage > totalPages && totalPages > 0) {
      setUsersCurrentPage(1);
    }
  }, [
    analytics.recentUsers,
    analytics.recentAdmins,
    usersItemsPerPage,
    usersCurrentPage,
  ]);

  useEffect(() => {
    const adminsTotalPages = Math.ceil(
      analytics.recentAdmins.length / adminsItemsPerPage
    );
    if (adminsCurrentPage > adminsTotalPages && adminsTotalPages > 0) {
      setAdminsCurrentPage(1);
    }
  }, [analytics.recentAdmins.length, adminsItemsPerPage, adminsCurrentPage]);

  useEffect(() => {
    document.documentElement.lang = language;
    document.documentElement.dir = language === "he" ? "rtl" : "ltr";
    i18n.changeLanguage(language);
  }, [language, i18n]);

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setIsRefreshing(true);

        // Get analytics data from service
        const analyticsData = await analyticsService.getDashboardAnalytics();

        setAnalytics(analyticsData);
      } catch (error) {
        console.error("Error fetching analytics:", error);
      } finally {
        setIsRefreshing(false);
      }
    };

    // Only fetch analytics when specifically viewing analytics sections
    // and prevent unnecessary calls when switching between sub-items
    if (activeItem === "analytics" && !isRefreshing) {
      fetchAnalytics();
    }
  }, [activeItem]); // Removed activeSubItem to prevent duplicate calls

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Check if cache is stale or needs refresh
        const forceRefresh = cacheService.isCacheStale("documents");

        const [docs, analyticsData] = await Promise.all([
          documentService.getAllDocuments(),
          analyticsService.getDashboardAnalytics(),
        ]);

        setDocuments(docs);
        setAnalytics(analyticsData);
      } catch (error) {
        console.error("Error fetching data:", error);
        console.error("🚨 [DEBUG] Failed to fetch documents");
      } finally {
        setIsInitialLoading(false);
      }
    };

    fetchData();

    // Listen for cache changes to refresh data when needed
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "documents_cache_invalidated") {
        fetchData();
      }
    };

    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
    };
  }, []);

  // Manual data refresh function
  const refreshData = async () => {
    setIsRefreshing(true);
    try {
      const [docs, analyticsData] = await Promise.all([
        documentService.getAllDocuments(),
        analyticsService.getDashboardAnalytics(),
      ]);

      setDocuments(docs);
      setAnalytics(analyticsData);
    } catch (error) {
      console.error("Error refreshing data:", error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleItemClick = (itemId: string) => {
    setActiveItem(itemId);

    if (itemId === "analytics") {
      setActiveSubItem("overview");
    } else if (itemId === "documents") {
      setActiveSubItem("active");
    } else if (itemId === "rag") {
      setActiveSubItem("overview");
    } else {
      setActiveSubItem(null);
    }
  };

  const handleSubItemClick = (itemId: string, subItemId: string) => {
    setActiveItem(itemId);
    setActiveSubItem(subItemId);
  };

  const handleEditDocument = (document: Document) => {
    setSelectedDocument(document);
    setShowEditDocumentModal(true);
  };

  const handleDeleteDocument = (document: Document) => {
    setSelectedDocument(document);
    setShowDeleteModal(true);
  };

  const handleUpload = async (file: File) => {
    try {
      // Verify user is authenticated before upload
      const { data: authData } = await supabase.auth.getSession();
      if (!authData.session) {
        console.error("User not authenticated");
        showErrorMessage("יש להתחבר מחדש למערכת");
        return;
      }

      // Check if user exists in users table
      const { data: userData, error: userError } = await supabase
        .from("users")
        .select("id")
        .eq("id", authData.session.user.id)
        .single();

      // If user doesn't exist, try creating them (may fail due to RLS)
      if (userError || !userData) {
        console.error("User not found in database:", userError);

        // Try creating a new user record
        try {
          const { error: insertError } = await supabase.from("users").insert({
            id: authData.session.user.id,
            email: authData.session.user.email || "",
            name: authData.session.user.email?.split("@")[0] || "User",
            status: "active",
          });

                      if (insertError) {
              console.error("Failed to insert user record:", insertError);
              // Continue despite error, as we're already trying to bypass restrictions
            } else {
              // Created new user record

            // Check if user should be admin and add to admins table
            if (
              authData.session.user.user_metadata?.is_admin ||
              authData.session.user.user_metadata?.role === "admin"
            ) {
              try {
                const { error: adminError } = await supabase
                  .from("admins")
                  .insert({
                    user_id: authData.session.user.id,
                  });

                                  if (adminError) {
                    console.error("Failed to insert admin record:", adminError);
                  } else {
                    // Created new admin record
                  }
              } catch (adminError) {
                console.error("Error creating admin record:", adminError);
              }
            }
          }
        } catch (createError) {
          console.error("Error creating user record:", createError);
          // Continue despite error
        }
              } else {
          // Found existing user
        }

      // Create safe filename without Hebrew characters
      const fileExt = file.name.split(".").pop() || "";
      const safeFileName = `${Date.now()}.${fileExt}`;
              const path = `documents/${safeFileName}`;

        try {
        // Upload the file - direct access without RPC
        const { data: uploadData, error: uploadError } = await supabase.storage
          .from("documents")
          .upload(path, file);

        if (uploadError) {
          console.error("Error uploading file:", uploadError);
          showErrorMessage(`שגיאה בהעלאת הקובץ: ${uploadError.message}`);
          return;
                  }

          // Get public URL
                  const { data: urlData } = supabase.storage
            .from("documents")
            .getPublicUrl(path);

          try {
          // Create document record directly (not through RPC)
          const { data: docData, error: docError } = await supabase
            .from("documents")
            .insert({
              name: file.name,
              type: file.type,
              size: file.size,
              url: urlData.publicUrl,
            })
            .select()
            .single();

          if (docError) {
            console.error("Error creating document record:", docError);
            showErrorMessage(`שגיאה ביצירת רשומת מסמך: ${docError.message}`);
            return;
                      }

            // Attempt to add analytics record (may fail due to RLS)
          try {
            const { error: analyticsError } = await supabase
              .from("document_analytics")
              .insert({
                document_id: docData.id,
                user_id: authData.session.user.id,
                action: "upload",
              });

            if (analyticsError) {
              console.error("Error adding analytics record:", analyticsError);
              // Continue despite error
            }
          } catch (analyticsError) {
            console.error("Failed to add analytics record:", analyticsError);
            // Continue despite error
          }

          setDocuments((prev) => [docData, ...prev]);
          setShowUploadModal(false);
        } catch (docError) {
          console.error("Error in document creation:", docError);
          showErrorMessage("אירעה שגיאה ביצירת רשומת המסמך");
        }
      } catch (uploadError) {
        console.error("Error in file upload process:", uploadError);
        showErrorMessage("אירעה שגיאה בתהליך העלאת הקובץ");
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      showErrorMessage("אירעה שגיאה בתהליך ההעלאה");
    }
  };

  const handleUpdateDocument = async (document: any, file: File) => {
    try {
      setIsRefreshing(true);

      // First delete the old file from storage
      const storagePathMatch = document.url.match(/\/documents\/([^\/]+)$/);
      const storagePath = storagePathMatch ? storagePathMatch[1] : null;

      if (storagePath) {
        try {
          // Delete the old file from storage
          const { error: removeError } = await supabase.storage
            .from("documents")
            .remove([`documents/${storagePath}`]);

          if (removeError) {
            console.error("Error removing old file:", removeError);
            // Continue anyway to try to upload the new file
          }
        } catch (removeError) {
          console.error("Error in file removal process:", removeError);
          // Continue anyway
        }
      }

      // Upload the new file
      const timestamp = Date.now();
      const fileExtension = file.name.split(".").pop() || "";
      const filePath = `documents/${timestamp}.${fileExtension}`;

      const { data: uploadData, error: uploadError } = await supabase.storage
        .from("documents")
        .upload(filePath, file);

      if (uploadError) {
        throw new Error(`Error uploading file: ${uploadError.message}`);
      }

      // Get URL for the uploaded file
      const {
        data: { publicUrl },
      } = supabase.storage.from("documents").getPublicUrl(uploadData.path);

      // Update document record with new file information
      const { data: updatedDoc, error: updateError } = await supabase
        .from("documents")
        .update({
          name: file.name,
          type: file.type,
          size: file.size,
          url: publicUrl,
          updated_at: new Date().toISOString(),
        })
        .eq("id", document.id)
        .select()
        .single();

      if (updateError) {
        throw new Error(`Error updating document: ${updateError.message}`);
      }

      // Update documents list
      setDocuments((prev) =>
        prev.map((doc) => (doc.id === document.id ? updatedDoc : doc))
      );

      // Close modal
      setShowEditDocumentModal(false);
      setSelectedDocument(null);

      showSuccessMessage(
        t("documents.updateSuccess") || "Document updated successfully"
      );
    } catch (error) {
      console.error("Error updating document:", error);
      showErrorMessage(t("documents.updateError") || "Error updating document");
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleDelete = async () => {
    try {
      // First set loading status
      setIsRefreshing(true);

      // Delete the document
      await documentService.deleteDocument(Number(selectedDocument!.id));

      // Update document list by removing the deleted document
      setDocuments(documents.filter((doc) => doc.id !== selectedDocument!.id));

      // Close the dialog
      setShowDeleteModal(false);

      // User notification
      showSuccessMessage(t("admin.documents.deleteSuccess"));

      // After deletion, reload all documents from server
      // to ensure view is synced with server
      try {
        const updatedDocs = await documentService.getAllDocuments();
        setDocuments(updatedDocs);
      } catch (refreshError) {
        console.error("Error refreshing documents after delete:", refreshError);
        // If refresh fails, at least the document was removed from view above
      }
    } catch (error) {
      console.error("Error deleting document:", error);
      showErrorMessage(t("admin.documents.deleteError"));
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleDeleteUser = (user: any) => {
    setSelectedUser(user);
    setShowDeleteUserModal(true);
  };

  const handleDeleteUserConfirm = async () => {
    try {
      setIsRefreshing(true);

      // Delete user via user service
      await userService.deleteUser(selectedUser.id);

      // Close dialog
      setShowDeleteUserModal(false);

      // User notification
      showSuccessMessage(t("The user was successfully deleted."));

      // Refresh data after deletion
      await refreshData();
    } catch (error) {
      console.error("Error deleting user:", error);
      showErrorMessage(t("The user was not deleted successfully."));
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleLanguageChange = (newLanguage: Language) => {
    setLanguage(newLanguage);
    i18n.changeLanguage(newLanguage);
    document.documentElement.lang = newLanguage;
    document.documentElement.dir = newLanguage === "he" ? "rtl" : "ltr";
  };

  const handleThemeChange = (newTheme: "dark" | "light") => {
    setTheme(newTheme);
  };

  const renderContent = () => {
    switch (activeItem) {
      case "chatbot":
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-green-600 dark:text-green-400 mb-4">
              {t("admin.sidebar.chatbotPreview")}
            </h2>
            <div className="bg-gray-100/30 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300/20 dark:border-green-500/20 p-4 h-[calc(100vh-200px)] overflow-auto">
              <div className="h-full relative">
                <ChatWindow onLogout={onLogout} />
              </div>
            </div>
          </div>
        );
      case "analytics":
        if (activeSubItem === "token-usage") {
          return <TokenUsageAnalytics language={language} />;
        } else if (activeSubItem === "users") {
          // Filter only regular users (not admins)
          const regularUsers = analytics.recentUsers.filter((user) => {
            // Check if user is not in the admins list
            return !analytics.recentAdmins?.some(
              (admin) => admin.id === user.id
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
                {/* Header עם bchירת כמות פריטים */}
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
                            title={t("users.delete") || "Delete user"}
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
        } else if (activeSubItem === "admins") {
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
                      {t("analytics.activeAdmins")} (
                      {analytics.recentAdmins.length})
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
                          admin{" "}
                          {admin.department ? `(${admin.department})` : ""}
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
        } else {
          // sub-category overview - show general data
          return (
            <div>
              <div className="mb-6 px-6 pt-6">
                <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {t("analytics.overview")}
                </h2>
              </div>
              <AnalyticsOverview
                analytics={analytics}
                isLoading={isRefreshing}
              />
            </div>
          );
        }
      case "documents":
        return (
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">
                {activeSubItem === "upload"
                  ? t("admin.sidebar.uploadDocuments")
                  : t("admin.sidebar.activeDocuments")}
              </h2>
              {activeSubItem === "active" && (
                <button
                  onClick={() => setShowUploadModal(true)}
                  className="bg-green-500/20 hover:bg-green-500/30 text-green-400 font-medium py-2 px-4 rounded-lg border border-green-500/30 transition-colors flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>{t("documents.add")}</span>
                </button>
              )}
            </div>

            {activeSubItem === "upload" ? (
              <UploadArea onUpload={() => setShowUploadModal(true)} />
            ) : (
              <DocumentTable
                documents={documents}
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
                onEdit={handleEditDocument}
                onDelete={handleDeleteDocument}
              />
            )}
          </div>
        );
      case "rag":
        return (
          <RAGManagement activeSubItem={activeSubItem} language={language} />
        );
      case "settings":
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-green-600 dark:text-green-400 mb-6">
              {t("admin.sidebar.settings")}
            </h2>
            <div className="bg-gray-100/30 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300/20 dark:border-green-500/20 p-6 space-y-8">
              {/* Theme Section */}
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-green-50 dark:bg-green-900/20 flex items-center justify-center">
                    {theme === "dark" ? (
                      <Moon className="w-4 h-4 text-green-600 dark:text-green-400" />
                    ) : (
                      <Sun className="w-4 h-4 text-green-600 dark:text-green-400" />
                    )}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-green-400">
                    {t("settings.theme") || "Theme"}
                  </h3>
                </div>

                <div className="relative">
                  <div className="flex p-1 bg-gray-200/50 dark:bg-black/50 rounded-xl border border-gray-300/30 dark:border-green-500/30">
                    <button
                      onClick={() => handleThemeChange("light")}
                      className={`flex-1 flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                        theme === "light"
                          ? "bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/30"
                          : "text-gray-600 dark:text-green-400/70 hover:text-gray-800 dark:hover:text-green-400 hover:bg-gray-100/20 dark:hover:bg-green-500/10"
                      }`}
                    >
                      <Sun className="w-4 h-4 mr-2" />
                      {language === "he" ? "בהיר" : "Light"}
                    </button>
                    <button
                      onClick={() => handleThemeChange("dark")}
                      className={`flex-1 flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                        theme === "dark"
                          ? "bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/30"
                          : "text-gray-600 dark:text-green-400/70 hover:text-gray-800 dark:hover:text-green-400 hover:bg-gray-100/20 dark:hover:bg-green-500/10"
                      }`}
                    >
                      <Moon className="w-4 h-4 mr-2" />
                      {language === "he" ? "כהה" : "Dark"}
                    </button>
                  </div>
                </div>
              </div>

              {/* Language Section */}
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-green-50 dark:bg-green-900/20 flex items-center justify-center">
                    <Globe className="w-4 h-4 text-green-600 dark:text-green-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-green-400">
                    {t("settings.language") || "Language"}
                  </h3>
                </div>

                <div className="relative">
                  <div className="flex p-1 bg-gray-200/50 dark:bg-black/50 rounded-xl border border-gray-300/30 dark:border-green-500/30">
                    <button
                      onClick={() => handleLanguageChange("he")}
                      className={`flex-1 flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                        language === "he"
                          ? "bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/30"
                          : "text-gray-600 dark:text-green-400/70 hover:text-gray-800 dark:hover:text-green-400 hover:bg-gray-100/20 dark:hover:bg-green-500/10"
                      }`}
                    >
                      עברית
                    </button>
                    <button
                      onClick={() => handleLanguageChange("en")}
                      className={`flex-1 flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                        language === "en"
                          ? "bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/30"
                          : "text-gray-600 dark:text-green-400/70 hover:text-gray-800 dark:hover:text-green-400 hover:bg-gray-100/20 dark:hover:bg-green-500/10"
                      }`}
                    >
                      English
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  if (isInitialLoading) {
    return (
      <LoadingScreen
        message={t("admin.loading") || "Loading Dashboard"}
        subMessage={
          t("admin.loadingPermissions") || "Initializing admin permissions..."
        }
      />
    );
  }

  return (
    <div className="flex h-screen bg-white dark:bg-black text-gray-900 dark:text-white transition-colors duration-300">
      {/* Success message */}
      {successMessage && (
        <div className="fixed top-4 right-4 z-50 bg-green-50 dark:bg-green-900/20 border-l-4 border-green-500 p-4 rounded shadow-md max-w-md animate-fadeIn">
          <div className="flex items-center">
            <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 mr-2" />
            <p className="text-green-700 dark:text-green-300">
              {successMessage}
            </p>
          </div>
        </div>
      )}

      {/* Error message */}
      {errorMessage && (
        <div className="fixed top-4 right-4 z-50 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4 rounded shadow-md max-w-md animate-fadeIn">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mr-2" />
            <p className="text-red-700 dark:text-red-300">{errorMessage}</p>
          </div>
        </div>
      )}

      <Sidebar
        isSidebarCollapsed={isSidebarCollapsed}
        setIsSidebarCollapsed={setIsSidebarCollapsed}
        activeItem={activeItem}
        setActiveItem={setActiveItem}
        activeSubItem={activeSubItem}
        setActiveSubItem={setActiveSubItem}
        language={language}
        onLogout={onLogout}
        onItemClick={handleItemClick}
        onSubItemClick={handleSubItemClick}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar language={language} />

        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-white dark:bg-black p-6 transition-colors duration-300">
          {renderContent()}
        </main>
      </div>

      <UploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onUpload={handleUpload}
      />

      <DeleteModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={handleDelete}
        documentName={selectedDocument?.name}
      />

      <EditDocumentModal
        isOpen={showEditDocumentModal}
        onClose={() => setShowEditDocumentModal(false)}
        document={
          selectedDocument
            ? {
                id: Number(selectedDocument.id),
                name: selectedDocument.name,
                type: selectedDocument.type,
                size: selectedDocument.size,
                url: selectedDocument.url,
                created_at: selectedDocument.created_at,
                updated_at: selectedDocument.updated_at || "",
              }
            : null
        }
        onUpdate={handleUpdateDocument}
      />

      {/* Delete user modal */}
      {showDeleteUserModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm dark:bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-black border border-gray-300 dark:border-green-500/30 rounded-lg p-6 w-full max-w-md shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-900 dark:text-green-400">
                {t("users.confirmDelete") || "Confirm User Deletion"}
              </h3>
              <button
                onClick={() => setShowDeleteUserModal(false)}
                className="text-gray-500 dark:text-green-400 hover:text-gray-700 dark:hover:text-green-300 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
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
                onClick={() => setShowDeleteUserModal(false)}
                className="px-4 py-2 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-700 dark:text-green-400 hover:bg-gray-50 dark:hover:bg-green-500/20 transition-colors"
              >
                {t("Cancel")}
              </button>
              <button
                onClick={handleDeleteUserConfirm}
                className="px-4 py-2 bg-red-50 dark:bg-red-500/20 border border-red-300 dark:border-red-500/30 rounded-lg text-red-700 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-500/30 transition-colors"
              >
                {t("users.delete") || t("Delete")}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
