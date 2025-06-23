import React from "react";
import { useTranslation } from "react-i18next";
import { AlertCircle, Clock } from "lucide-react";

// Custom hooks
import { useRAGProfiles } from "./hooks/useRAGProfiles";
import { useRAGTesting } from "./hooks/useRAGTesting";
import { useRAGModals } from "./hooks/useRAGModals";

// Components
import RAGOverview from "./components/RAGOverview";
import ProfilesList from "./components/ProfilesList";
import TestCenter from "./components/TestCenter";
import PerformanceDashboard from "./components/PerformanceDashboard";
import CreateProfileModal from "./components/CreateProfileModal";
import DeleteConfirmationModal from "./components/DeleteConfirmationModal";
import RestoreConfirmationModal from "./components/RestoreConfirmationModal";
import ActiveProfileErrorModal from "./components/ActiveProfileErrorModal";
import { SystemPromptManagement } from "./components/SystemPromptManagement";

type Language = "he" | "en";

interface RAGManagementProps {
  activeSubItem: string | null;
  language: Language;
}

export const RAGManagement: React.FC<RAGManagementProps> = ({
  activeSubItem,
  language,
}) => {
  const { t } = useTranslation();

  // Custom hooks
  const ragProfiles = useRAGProfiles(language);
  const ragTesting = useRAGTesting();
  const ragModals = useRAGModals();

  // Combined error handling
  const error = ragProfiles.error;
  const setError = ragProfiles.setError;

  // Modal handlers that integrate with profile actions
  const handleDeleteProfile = (
    profileId: string,
    profileName: string,
    isCustom: boolean
  ) => {
    ragModals.openDeleteModal(profileId, profileName, isCustom);
  };

  const handleConfirmDelete = async () => {
    if (!ragModals.modalProfileData) return;

    ragModals.closeDeleteModal();
    await ragProfiles.handleDeleteProfile(
      ragModals.modalProfileData.id,
      !ragModals.modalProfileData.isCustom,
      (profileName: string) => ragModals.openActiveProfileError(profileName)
    );
  };

  const handleRestoreProfile = (profileId: string, profileName: string) => {
    ragModals.openRestoreModal(profileId, profileName);
  };

  const handleConfirmRestore = async () => {
    if (!ragModals.modalProfileData) return;

    ragModals.closeRestoreModal();
    await ragProfiles.handleRestoreProfile(ragModals.modalProfileData.id);
  };

  const handleCreateProfile = async (profileData: any) => {
    try {
      await ragProfiles.handleCreateProfile(profileData);
      ragModals.closeCreateModal(); // Close modal only after successful creation
    } catch (error) {
      console.error("Error creating profile:", error);
      // Keep modal open on error so user can try again
    }
  };

  // Content rendering logic
  const renderContent = () => {
    switch (activeSubItem) {
      case "profiles":
        return (
          <ProfilesList
            profiles={ragProfiles.profiles}
            paginatedProfiles={ragProfiles.paginatedProfiles}
            hiddenProfiles={ragProfiles.hiddenProfiles}
            showHiddenProfiles={ragProfiles.showHiddenProfiles}
            language={language}
            loading={ragProfiles.loading}
            isDeletingProfile={ragProfiles.isDeletingProfile}
            isRestoringProfile={ragProfiles.isRestoringProfile}
            itemsPerPage={ragProfiles.profilesItemsPerPage}
            currentPage={ragProfiles.profilesCurrentPage}
            totalPages={Math.ceil(
              ragProfiles.profiles.length / ragProfiles.profilesItemsPerPage
            )}
            onProfileChange={ragProfiles.handleProfileChange}
            onDeleteProfile={handleDeleteProfile}
            onRestoreProfile={handleRestoreProfile}
            onCreateProfile={() => ragModals.setShowCreateProfile(true)}
            onToggleHiddenProfiles={() =>
              ragProfiles.setShowHiddenProfiles(!ragProfiles.showHiddenProfiles)
            }
            setItemsPerPage={ragProfiles.setProfilesItemsPerPage}
            setCurrentPage={ragProfiles.setProfilesCurrentPage}
          />
        );

      case "test":
        return (
          <TestCenter
            testQuery={ragTesting.testQuery}
            setTestQuery={ragTesting.setTestQuery}
            testResult={ragTesting.testResult}
            isRunningTest={ragTesting.isRunningTest}
            showFullChunk={ragTesting.showFullChunk}
            onRunTest={ragTesting.handleRunTest}
            onToggleChunk={() =>
              ragTesting.setShowFullChunk(!ragTesting.showFullChunk)
            }
            language={language}
          />
        );

      case "performance":
        return (
          <PerformanceDashboard
            profiles={ragProfiles.profiles}
            language={language}
          />
        );

      case "system-prompt":
        return <SystemPromptManagement language={language} />;

      default:
        return <RAGOverview currentProfile={ragProfiles.currentProfile} />;
    }
  };

  // Loading state
  if (ragProfiles.loading && ragProfiles.profiles.length === 0) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="text-gray-700 dark:text-green-400">
          <Clock className="w-8 h-8 animate-spin mx-auto mb-2" />
          <p>{t("rag.loading") || "טוען נתוני RAG..."}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-green-400">
          {t("rag.management")}
          {activeSubItem && activeSubItem !== "overview" && (
            <span className="text-gray-600 dark:text-green-400/70 mr-2">
              /{" "}
              {activeSubItem === "profiles"
                ? t("rag.profile.selector")
                : activeSubItem === "performance"
                ? t("rag.performanceMonitor")
                : activeSubItem === "test"
                ? t("rag.test.center")
                : activeSubItem === "system-prompt"
                ? t("rag.system.prompt")
                : ""}
            </span>
          )}
        </h2>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 bg-red-100 dark:bg-red-500/20 border border-red-300 dark:border-red-500/30 rounded-lg p-4 flex items-center">
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mr-3" />
          <span className="text-red-800 dark:text-red-400">{error}</span>
          <button
            onClick={() => setError(null)}
            className="mr-auto text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
          >
            ✕
          </button>
        </div>
      )}

      {/* Main Content */}
      {renderContent()}

      {/* Modals */}
      {ragModals.showCreateProfile && (
        <CreateProfileModal
          language={language}
          onSubmit={handleCreateProfile}
          onCancel={ragModals.closeCreateModal}
          isCreating={ragProfiles.isCreatingProfile}
        />
      )}

      <DeleteConfirmationModal
        isVisible={ragModals.showDeleteModal}
        modalProfileData={ragModals.modalProfileData}
        isDeletingProfile={ragProfiles.isDeletingProfile}
        onConfirm={handleConfirmDelete}
        onCancel={ragModals.closeDeleteModal}
      />

      <RestoreConfirmationModal
        isVisible={ragModals.showRestoreModal}
        modalProfileData={ragModals.modalProfileData}
        isRestoringProfile={ragProfiles.isRestoringProfile}
        onConfirm={handleConfirmRestore}
        onCancel={ragModals.closeRestoreModal}
      />

      <ActiveProfileErrorModal
        isVisible={ragModals.showActiveProfileError}
        profileName={ragModals.activeProfileErrorData?.profileName || ""}
        onClose={ragModals.closeActiveProfileError}
      />
    </div>
  );
};
