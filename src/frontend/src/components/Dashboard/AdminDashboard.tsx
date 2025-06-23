import React, { useMemo } from "react";
import { useTranslation } from "react-i18next";
import "./AdminDashboard.css";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { UploadModal } from "./UploadModal";
import { EditDocumentModal } from "./EditDocumentModal";
import { DeleteModal } from "./DeleteModal";
import LoadingScreen from "../LoadingScreen";
import { useAdminState } from "../../hooks/useAdminState";
import { useDataManagement } from "../../hooks/useDataManagement";
import { 
  ChatbotPage, 
  AnalyticsPage, 
  DocumentsPage, 
  RAGPage, 
  SettingsPage 
} from "./pages";
import { NotificationToast, UserDeleteModal } from "./components";

interface AdminDashboardProps {
  onLogout: () => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ onLogout }) => {
  const { t } = useTranslation();
  
  // Use extracted hooks
  const adminState = useAdminState();
  const dataManagement = useDataManagement({ 
    state: adminState, 
    actions: adminState 
  });

  // Destructure state and actions for easier access
  const {
    isSidebarCollapsed,
    activeItem,
    activeSubItem,
    searchQuery,
    showUploadModal,
    showDeleteModal,
    showDeleteUserModal,
    showEditDocumentModal,
    selectedUser,
    selectedDocument,
    documents,
    analytics,
    isInitialLoading,
    isRefreshing,
    language,
    theme,
    successMessage,
    errorMessage,
    usersItemsPerPage,
    usersCurrentPage,
    adminsItemsPerPage,
    adminsCurrentPage,
    setIsSidebarCollapsed,
    setActiveItem,
    setActiveSubItem,
    setSearchQuery,
    setShowUploadModal,
    setShowDeleteModal,
    setShowEditDocumentModal,
    setShowDeleteUserModal,
    handleItemClick,
    handleSubItemClick,
    handleLanguageChange,
    handleThemeChange,
    setUsersItemsPerPage,
    setUsersCurrentPage,
    setAdminsItemsPerPage,
    setAdminsCurrentPage,
  } = adminState;

      const {
    handleUpload,
    handleUpdateDocument,
    handleDelete,
    handleEditDocument,
    handleDeleteDocument,
    handleDeleteUser,
    handleDeleteUserConfirm,
  } = dataManagement;

  // Memoized content renderer for better performance
  const renderContent = useMemo(() => {
    switch (activeItem) {
      case "chatbot":
        return <ChatbotPage onLogout={onLogout} />;
      case "analytics":
          return (
          <AnalyticsPage
            activeSubItem={activeSubItem || "overview"}
            language={language}
                analytics={analytics}
            isRefreshing={isRefreshing}
            usersItemsPerPage={usersItemsPerPage}
            usersCurrentPage={usersCurrentPage}
            adminsItemsPerPage={adminsItemsPerPage}
            adminsCurrentPage={adminsCurrentPage}
            setUsersItemsPerPage={setUsersItemsPerPage}
            setUsersCurrentPage={setUsersCurrentPage}
            setAdminsItemsPerPage={setAdminsItemsPerPage}
            setAdminsCurrentPage={setAdminsCurrentPage}
            handleDeleteUser={handleDeleteUser}
          />
        );
      case "documents":
        return (
          <DocumentsPage
            activeSubItem={activeSubItem || "active"}
                documents={documents}
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
            setShowUploadModal={setShowUploadModal}
            handleEditDocument={handleEditDocument}
            handleDeleteDocument={handleDeleteDocument}
              />
        );
      case "rag":
        return <RAGPage activeSubItem={activeSubItem || "profiles"} language={language} />;
      case "settings":
        return (
          <SettingsPage
            language={language}
            theme={theme}
            handleLanguageChange={handleLanguageChange}
            handleThemeChange={handleThemeChange}
          />
        );
      default:
        return null;
    }
  }, [
    activeItem,
    activeSubItem,
    onLogout,
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
    documents,
    searchQuery,
    setSearchQuery,
    setShowUploadModal,
    handleEditDocument,
    handleDeleteDocument,
    theme,
    handleLanguageChange,
    handleThemeChange,
  ]);

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
      {/* Notifications */}
      {successMessage && (
        <NotificationToast
          message={successMessage}
          type="success"
        />
      )}

      {errorMessage && (
        <NotificationToast
          message={errorMessage}
          type="error"
        />
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
          {renderContent}
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

      <UserDeleteModal
        isOpen={showDeleteUserModal}
        onClose={() => setShowDeleteUserModal(false)}
        onConfirm={handleDeleteUserConfirm}
        selectedUser={selectedUser}
      />
    </div>
  );
};

export default AdminDashboard;
