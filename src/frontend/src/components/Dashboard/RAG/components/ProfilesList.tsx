import React from 'react';
import { useTranslation } from 'react-i18next';
import { CheckCircle, Trash2, RotateCcw } from 'lucide-react';
import { RAGProfile } from '../RAGService';
import { Pagination } from '../../../common/Pagination';
import { ItemsPerPageSelector } from '../../../common/ItemsPerPageSelector';

type Language = "he" | "en";

interface ProfilesListProps {
  profiles: RAGProfile[];
  paginatedProfiles: RAGProfile[];
  hiddenProfiles: string[];
  showHiddenProfiles: boolean;
  language: Language;
  loading: boolean;
  isDeletingProfile: string | null;
  isRestoringProfile: string | null;
  
  // Pagination
  itemsPerPage: number;
  currentPage: number;
  totalPages: number;
  
  // Actions
  onProfileChange: (profileId: string) => void;
  onDeleteProfile: (profileId: string, profileName: string, isCustom: boolean) => void;
  onRestoreProfile: (profileId: string, profileName: string) => void;
  onCreateProfile: () => void;
  onToggleHiddenProfiles: () => void;
  setItemsPerPage: (value: number) => void;
  setCurrentPage: (value: number) => void;
}

const ProfilesList: React.FC<ProfilesListProps> = ({
  profiles,
  paginatedProfiles,
  hiddenProfiles,
  showHiddenProfiles,
  language,
  loading,
  isDeletingProfile,
  isRestoringProfile,
  itemsPerPage,
  currentPage,
  totalPages,
  onProfileChange,
  onDeleteProfile,
  onRestoreProfile,
  onCreateProfile,
  onToggleHiddenProfiles,
  setItemsPerPage,
  setCurrentPage,
}) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-6">
      {/* Header with controls */}
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-semibold text-gray-800 dark:text-green-400">
          {t("rag.available.profiles") || "פרופילים זמינים"} ({profiles.length})
        </h3>
        
        <div className="flex items-center space-x-4">
          {profiles.length > 6 && (
            <ItemsPerPageSelector
              itemsPerPage={itemsPerPage}
              onItemsPerPageChange={(newItemsPerPage) => {
                setItemsPerPage(newItemsPerPage);
                setCurrentPage(1);
              }}
              options={[6, 12, 18, 24]}
            />
          )}
          
          <button
            onClick={onToggleHiddenProfiles}
            className="bg-gray-100 dark:bg-gray-500/20 hover:bg-gray-200 dark:hover:bg-gray-500/30 text-gray-800 dark:text-gray-400 font-medium py-2 px-4 rounded-lg border border-gray-300 dark:border-gray-500/30 transition-colors flex items-center space-x-2"
          >
            <span>{showHiddenProfiles ? "👁️" : "👁️‍🗨️"}</span>
            <span>
              {showHiddenProfiles 
                ? (language === 'he' ? "הסתר פרופילים נסתרים" : "Hide Hidden Profiles")
                : (language === 'he' ? "הצג פרופילים נסתרים" : "Show Hidden Profiles")
              }
            </span>
          </button>
          
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onCreateProfile();
            }}
            className="bg-green-100 dark:bg-green-500/20 hover:bg-green-200 dark:hover:bg-green-500/30 text-green-800 dark:text-green-400 font-medium py-2 px-4 rounded-lg border border-green-300 dark:border-green-500/30 transition-colors flex items-center space-x-2"
          >
            <span>+</span>
            <span>{t("rag.create.profile") || "צור פרופיל חדש"}</span>
          </button>
        </div>
      </div>

      {/* Hidden Profiles Section */}
      {showHiddenProfiles && hiddenProfiles.length > 0 && (
        <div className="bg-orange-50 dark:bg-orange-500/10 backdrop-blur-lg rounded-lg border border-orange-200 dark:border-orange-500/20 shadow-lg">
          <div className="p-6">
            <h4 className="text-lg font-semibold text-orange-600 dark:text-orange-400 mb-4">
              {language === 'he' ? "פרופילים נסתרים" : "Hidden Profiles"}
            </h4>
            <div className="space-y-3">
              {hiddenProfiles.map((profileId) => (
                <div
                  key={profileId}
                  className="flex items-center justify-between p-3 bg-orange-100/50 dark:bg-orange-500/5 rounded border border-orange-200 dark:border-orange-500/10"
                >
                  <span className="text-orange-800 dark:text-orange-300 font-medium">
                    {profileId}
                  </span>
                  <button
                    onClick={() => onRestoreProfile(profileId, profileId)}
                    disabled={isRestoringProfile === profileId}
                    className="bg-orange-200 dark:bg-orange-500/20 hover:bg-orange-300 dark:hover:bg-orange-500/30 text-orange-800 dark:text-orange-400 px-3 py-1 rounded border border-orange-300 dark:border-orange-500/30 transition-colors flex items-center space-x-1 disabled:opacity-50"
                  >
                    <RotateCcw className="w-4 h-4" />
                    <span>
                      {isRestoringProfile === profileId
                        ? (language === 'he' ? "משחזר..." : "Restoring...")
                        : (language === 'he' ? "שחזר" : "Restore")
                      }
                    </span>
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Profiles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {paginatedProfiles.map((profile) => (
          <div
            key={profile.id}
            className={`bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border shadow-lg transition-all duration-200 ${
              profile.isActive
                ? "border-green-500 dark:border-green-500/50 ring-2 ring-green-500/20"
                : "border-gray-300 dark:border-green-500/20 hover:border-green-400 dark:hover:border-green-500/40"
            }`}
          >
            <div className="p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h4 className="text-lg font-semibold text-gray-800 dark:text-green-300 mb-1">
                    {profile.name}
                    {profile.isActive && (
                      <CheckCircle className="inline w-5 h-5 text-green-600 dark:text-green-400 ml-2" />
                    )}
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-green-400/70 mb-3">
                    {profile.description}
                  </p>
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2 ml-2">
                  {profile.isCustom && (
                    <button
                      onClick={() => onDeleteProfile(profile.id, profile.name, true)}
                      disabled={isDeletingProfile === profile.id}
                      className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 p-1 rounded transition-colors disabled:opacity-50"
                      title={language === 'he' ? "מחק פרופיל" : "Delete Profile"}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                  
                  {!profile.isCustom && (
                    <button
                      onClick={() => onDeleteProfile(profile.id, profile.name, false)}
                      disabled={isDeletingProfile === profile.id}
                      className="text-orange-600 dark:text-orange-400 hover:text-orange-800 dark:hover:text-orange-300 p-1 rounded transition-colors disabled:opacity-50"
                      title={language === 'he' ? "הסתר פרופיל" : "Hide Profile"}
                    >
                      <span className="text-sm">🙈</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Configuration */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-xs text-gray-500 dark:text-green-400/50 uppercase tracking-wide">
                    {t("rag.settings") || "הגדרות"}
                  </p>
                  <div className="space-y-1 mt-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-green-400/70">
                        {t("rag.similarity.threshold") || "סף דמיון"}:
                      </span>
                      <span className="text-gray-800 dark:text-green-300">
                        {profile.config.similarityThreshold}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-green-400/70">
                        {t("rag.chunks") || "צ'אנקים"}:
                      </span>
                      <span className="text-gray-800 dark:text-green-300">
                        {profile.config.maxChunks}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-green-400/70">
                        {t("rag.temperature") || "טמפרטורה"}:
                      </span>
                      <span className="text-gray-800 dark:text-green-300">
                        {profile.config.temperature}
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <p className="text-xs text-gray-500 dark:text-green-400/50 uppercase tracking-wide">
                    {t("rag.characteristics") || "מאפיינים"}
                  </p>
                  <div className="space-y-1 mt-2">
                    <div className="text-sm">
                      <span className="text-gray-600 dark:text-green-400/70">
                        {t("rag.focus") || "מיקוד"}:
                      </span>
                      <p className="text-gray-800 dark:text-green-300 text-xs mt-1 line-clamp-2">
                        {profile.characteristics.focus}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Activate Button */}
              {!profile.isActive && (
                <button
                  onClick={() => onProfileChange(profile.id)}
                  disabled={loading}
                  className="w-full bg-green-100 dark:bg-green-500/20 hover:bg-green-200 dark:hover:bg-green-500/30 text-green-800 dark:text-green-400 font-medium py-2 px-4 rounded border border-green-300 dark:border-green-500/30 transition-colors disabled:opacity-50"
                >
                  {loading ? (
                    <span>{t("rag.activating") || "מפעיל..."}</span>
                  ) : (
                    <span>{t("rag.activate") || "הפעל פרופיל"}</span>
                  )}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center mt-8">
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
          />
        </div>
      )}
    </div>
  );
};

export default ProfilesList; 