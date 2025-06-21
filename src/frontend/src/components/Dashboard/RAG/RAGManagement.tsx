import React, { useState, useEffect, useCallback, useRef } from "react";
import { useTranslation } from "react-i18next";
import {
  Brain,
  Cpu,
  TrendingUp,
  Search,
  Check,
  CheckCircle,
  AlertCircle,
  Clock,
} from "lucide-react";
import { ragService, RAGProfile, RAGTestResult } from "./RAGService";
import { Pagination } from "../../common/Pagination";
import { ItemsPerPageSelector } from "../../common/ItemsPerPageSelector";
import AIResponseRenderer from "../../common/AIResponseRenderer";

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
  const [loading, setLoading] = useState(false);
  // Removed unused currentProfile state
  const [profiles, setProfiles] = useState<RAGProfile[]>([]);
  const [testQuery, setTestQuery] = useState("");
  const [testResult, setTestResult] = useState<RAGTestResult | null>(null);
  const [isRunningTest, setIsRunningTest] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreateProfile, setShowCreateProfile] = useState(false);
  const [isCreatingProfile, setIsCreatingProfile] = useState(false);
  const [isDeletingProfile, setIsDeletingProfile] = useState<string | null>(
    null
  );
  const [showFullChunk, setShowFullChunk] = useState(false);
  const [showHiddenProfiles, setShowHiddenProfiles] = useState(false);
  const [hiddenProfiles, setHiddenProfiles] = useState<string[]>([]);
  const [isRestoringProfile, setIsRestoringProfile] = useState<string | null>(null);
  
  // Modal states
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showRestoreModal, setShowRestoreModal] = useState(false);
  const [modalProfileData, setModalProfileData] = useState<{
    id: string;
    name: string;
    isCustom: boolean;
  } | null>(null);

  // Pagination state for profiles
  const [profilesItemsPerPage, setProfilesItemsPerPage] = useState(10);
  const [profilesCurrentPage, setProfilesCurrentPage] = useState(1);

  // Add debounce ref to prevent rapid successive calls
  const fetchTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastFetchTime = useRef<number>(0);
  const MIN_FETCH_INTERVAL = 1000; // Minimum 1 second between fetches

  const fetchProfiles = useCallback(async () => {
    const now = Date.now();
    const timeSinceLastFetch = now - lastFetchTime.current;
    
    // If too soon since last fetch, debounce
    if (timeSinceLastFetch < MIN_FETCH_INTERVAL) {
      if (fetchTimeoutRef.current) {
        clearTimeout(fetchTimeoutRef.current);
      }
      
      fetchTimeoutRef.current = setTimeout(async () => {
        lastFetchTime.current = Date.now();
        const controller = new AbortController();
        
        try {
          setLoading(true);
  
          const profilesData = await ragService.getAllProfiles(language);
          
          if (!controller.signal.aborted) {
            setProfiles(profilesData);
          }
        } catch (error) {
          if (!controller.signal.aborted) {
            console.error("Error fetching profiles:", error);
            setError("Failed to fetch profiles");
          }
        } finally {
          if (!controller.signal.aborted) {
            setLoading(false);
          }
        }
      }, MIN_FETCH_INTERVAL - timeSinceLastFetch);
      return;
    }
    
    lastFetchTime.current = now;
    const controller = new AbortController();
    
    try {
      setLoading(true);
      const profilesData = await ragService.getAllProfiles(language);
      
      // Only update state if not aborted
      if (!controller.signal.aborted) {
        setProfiles(profilesData);
      }
    } catch (error) {
      if (!controller.signal.aborted) {
        console.error("Error fetching profiles:", error);
        setError("Failed to fetch profiles");
      }
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
      }
    }
    
    return () => controller.abort();
  }, [language]);

  const fetchHiddenProfiles = useCallback(async () => {
    const controller = new AbortController();
    
          try {
      const hiddenProfilesData = await ragService.getHiddenProfiles();
      
      // Only update state if not aborted
      if (!controller.signal.aborted) {

        setHiddenProfiles(hiddenProfilesData);
      }
    } catch (error) {
      if (!controller.signal.aborted) {
        console.error("Error fetching hidden profiles:", error);
        setHiddenProfiles([]);
      }
    }
    
    return () => controller.abort();
  }, []);

  useEffect(() => {
    // Only fetch if we haven't already or if language changed
    
    let mounted = true;
    
    const loadData = async () => {
      if (mounted) {
        await fetchProfiles();
        await fetchHiddenProfiles();
      }
    };
    
    loadData();
    
    return () => {
      mounted = false;
      if (fetchTimeoutRef.current) {
        clearTimeout(fetchTimeoutRef.current);
      }
    };
  }, [fetchProfiles, fetchHiddenProfiles]);

  // Pagination reset effect
  useEffect(() => {
    const totalPages = Math.ceil(profiles.length / profilesItemsPerPage);
    if (profilesCurrentPage > totalPages && totalPages > 0) {
      setProfilesCurrentPage(1);
    }
  }, [profiles.length, profilesItemsPerPage, profilesCurrentPage]);

  const handleProfileChange = async (profileId: string) => {
    setLoading(true);
    setError(null);
    try {
      await ragService.activateProfile(profileId);
      

      // Reload profiles to get updated status
      await fetchProfiles();
    } catch (error) {
      console.error("Error switching profile:", error);
      setError(`Failed to switch to profile: ${profileId}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRunTest = async () => {
    if (!testQuery.trim()) return;

    setIsRunningTest(true);
    setError(null);
    setShowFullChunk(false); // Reset chunk display
    try {
      

      const testResponse = await ragService.testQuery(testQuery);
      setTestResult(testResponse);
    } catch (error) {
      console.error("Error running test:", error);
      setError("Failed to run test query");
    } finally {
      setIsRunningTest(false);
    }
  };

  const renderOverview = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-6 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-green-600 dark:text-green-400">
            {t("rag.current.profile") || "פרופיל נוכחי"}
          </h3>
          <Brain className="w-6 h-6 text-green-600 dark:text-green-500" />
        </div>
        <div className="space-y-3">
          <div>
            <p className="text-gray-800 dark:text-green-300 font-semibold text-xl">
              {profiles.find((p) => p.isActive)?.name || "לא נמצא"}
            </p>
            <p className="text-gray-600 dark:text-green-400/70 text-sm">
              {profiles.find((p) => p.isActive)?.description || ""}
            </p>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-green-400/60 text-sm">
                {t("rag.similarity.threshold") || "סף דמיון"}:
              </span>
              <span className="text-gray-800 dark:text-green-300 text-sm">
                {profiles.find((p) => p.isActive)?.config.similarityThreshold ||
                  "N/A"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-green-400/60 text-sm">
                {t("rag.max.chunks") || "צ'אנקים מקס"}:
              </span>
              <span className="text-gray-800 dark:text-green-300 text-sm">
                {profiles.find((p) => p.isActive)?.config.maxChunks || "N/A"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-green-400/60 text-sm">
                {t("rag.temperature") || "טמפרטורה"}:
              </span>
              <span className="text-gray-800 dark:text-green-300 text-sm">
                {profiles.find((p) => p.isActive)?.config.temperature || "N/A"}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-blue-500/20 p-6 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-blue-600 dark:text-blue-400">
            {t("rag.profileCharacteristics") || "מאפיינים"}
          </h3>
          <TrendingUp className="w-6 h-6 text-blue-600 dark:text-blue-500" />
        </div>
        <div className="space-y-3">
          <div>
            <p className="text-gray-600 dark:text-blue-400/70 text-sm">
              {t("rag.focus")}:
            </p>
            <p className="text-gray-800 dark:text-blue-300 text-sm">
              {profiles.find((p) => p.isActive)?.characteristics.focus ||
                t("rag.notAvailable")}
            </p>
          </div>
          <div>
            <p className="text-gray-600 dark:text-blue-400/70 text-sm">
              {t("rag.expectedSpeed")}:
            </p>
            <p className="text-gray-800 dark:text-blue-300 text-sm">
              {profiles.find((p) => p.isActive)?.characteristics
                .expectedSpeed || t("rag.notAvailable")}
            </p>
          </div>
          <div>
            <p className="text-gray-600 dark:text-blue-400/70 text-sm">
              {t("rag.expectedQuality")}:
            </p>
            <p className="text-gray-800 dark:text-blue-300 text-sm">
              {profiles.find((p) => p.isActive)?.characteristics
                .expectedQuality || t("rag.notAvailable")}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-purple-500/20 p-6 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-purple-600 dark:text-purple-400">
            {t("rag.configuration") || "קונפיגורציה מתקדמת"}
          </h3>
          <Cpu className="w-6 h-6 text-purple-600 dark:text-purple-500" />
        </div>
        <div className="space-y-2">
          {profiles.find((p) => p.isActive)?.config.chunkSize && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-purple-400/60 text-sm">
                {t("rag.chunkSize") || "גודל צ'אנק"}:
              </span>
              <span className="text-gray-800 dark:text-purple-300 text-sm">
                {profiles.find((p) => p.isActive)?.config.chunkSize}
              </span>
            </div>
          )}
          {profiles.find((p) => p.isActive)?.config.chunkOverlap && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-purple-400/60 text-sm">
                {t("rag.chunkOverlap") || "חפיפת צ'אנקים"}:
              </span>
              <span className="text-gray-800 dark:text-purple-300 text-sm">
                {profiles.find((p) => p.isActive)?.config.chunkOverlap}
              </span>
            </div>
          )}
          {profiles.find((p) => p.isActive)?.config.maxContextTokens && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-purple-400/60 text-sm">
                {t("rag.maxContext") || "קונטקסט מקס"}:
              </span>
              <span className="text-gray-800 dark:text-purple-300 text-sm">
                {profiles.find((p) => p.isActive)?.config.maxContextTokens}
              </span>
            </div>
          )}
          {profiles.find((p) => p.isActive)?.config.hybridSemanticWeight && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-purple-400/60 text-sm">
                {t("rag.semanticWeight") || "משקל סמנטי"}:
              </span>
              <span className="text-gray-800 dark:text-purple-300 text-sm">
                {profiles.find((p) => p.isActive)?.config.hybridSemanticWeight}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const handleCreateProfile = async (profileData: Partial<RAGProfile>) => {
    setIsCreatingProfile(true);
    setError(null);
    try {
      await ragService.createProfile(profileData);
      
      setShowCreateProfile(false);
      await fetchProfiles(); // רענון הרשימה
    } catch (error) {
      console.error("Error creating profile:", error);
      setError("Failed to create profile");
    } finally {
      setIsCreatingProfile(false);
    }
  };

  const handleDeleteProfile = (
    profileId: string,
    profileName: string,
    isCustom: boolean = true
  ) => {
    setModalProfileData({ id: profileId, name: profileName, isCustom });
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    if (!modalProfileData) return;

    const { id: profileId, isCustom } = modalProfileData;
    
    setIsDeletingProfile(profileId);
    setError(null);
    setShowDeleteModal(false);
    
    try {
      // עבור פרופילים מובנים, נשלח force=true
      await ragService.deleteProfile(profileId, !isCustom);
      
      await fetchProfiles(); // רענון הרשימה
      await fetchHiddenProfiles(); // רענון רשימת הנסתרים
    } catch (error) {
      console.error("Error deleting profile:", error);
      setError(
        `Failed to delete profile: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    } finally {
      setIsDeletingProfile(null);
      setModalProfileData(null);
    }
  };

  const handleRestoreProfile = (profileId: string, profileName: string) => {
    setModalProfileData({ id: profileId, name: profileName, isCustom: false });
    setShowRestoreModal(true);
  };

  const handleConfirmRestore = async () => {
    if (!modalProfileData) return;

    const { id: profileId } = modalProfileData;
    
    setIsRestoringProfile(profileId);
    setError(null);
    setShowRestoreModal(false);
    
    try {
      await ragService.restoreProfile(profileId);
      
      await fetchProfiles(); // רענון הרשימה
      await fetchHiddenProfiles(); // רענון רשימת הנסתרים
    } catch (error) {
      console.error("Error restoring profile:", error);
      setError(
        `Failed to restore profile: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    } finally {
      setIsRestoringProfile(null);
      setModalProfileData(null);
    }
  };

  const renderProfiles = () => {
    // Pagination logic for profiles
    const startIndex = (profilesCurrentPage - 1) * profilesItemsPerPage;
    const endIndex = startIndex + profilesItemsPerPage;
    const paginatedProfiles = profiles.slice(startIndex, endIndex);

    return (
      <div className="space-y-6">
        {/* Header with Create button and pagination controls */}
        <div className="flex justify-between items-center">
          <h3 className="text-xl font-semibold text-gray-800 dark:text-green-400">
            {t("rag.available.profiles") || "פרופילים זמינים"} (
            {profiles.length})
          </h3>
          <div className="flex items-center space-x-4">
            {profiles.length > 6 && (
              <ItemsPerPageSelector
                itemsPerPage={profilesItemsPerPage}
                onItemsPerPageChange={(newItemsPerPage) => {
                  setProfilesItemsPerPage(newItemsPerPage);
                  setProfilesCurrentPage(1);
                }}
                options={[6, 12, 18, 24]}
              />
            )}
            <button
              onClick={() => {
          
                setShowHiddenProfiles(!showHiddenProfiles);
              }}
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
              onClick={() => setShowCreateProfile(true)}
              className="bg-green-100 dark:bg-green-500/20 hover:bg-green-200 dark:hover:bg-green-500/30 text-green-800 dark:text-green-400 font-medium py-2 px-4 rounded-lg border border-green-300 dark:border-green-500/30 transition-colors flex items-center space-x-2"
            >
              <span>+</span>
              <span>{t("rag.create.profile") || "צור פרופיל חדש"}</span>
            </button>
          </div>
        </div>

        {/* מודאל יצירת פרופיל */}
        {showCreateProfile && (
          <CreateProfileModal
            language={language}
            onSubmit={handleCreateProfile}
            onCancel={() => setShowCreateProfile(false)}
            isCreating={isCreatingProfile}
          />
        )}

        {/* Hidden Profiles Section */}
        {showHiddenProfiles && (
          <div className="bg-orange-50 dark:bg-orange-500/10 backdrop-blur-lg rounded-lg border border-orange-200 dark:border-orange-500/20 shadow-lg mb-6">
            <div className="p-6">
              <h4 className="text-lg font-semibold text-orange-800 dark:text-orange-400 mb-4">
                {language === 'he' ? `פרופילים נסתרים (${hiddenProfiles.length})` : `Hidden Profiles (${hiddenProfiles.length})`}
              </h4>
              {hiddenProfiles.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-orange-600 dark:text-orange-400/70">
                    {language === 'he' ? "אין פרופילים נסתרים כרגע" : "No hidden profiles at the moment"}
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {hiddenProfiles.map((profileId) => (
                  <div
                    key={`hidden-${profileId}`}
                    className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-orange-300 dark:border-orange-500/30 p-4 transition-all shadow-lg opacity-75"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h5 className="text-md font-semibold text-orange-800 dark:text-orange-400">
                          {profileId.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </h5>
                        <p className="text-sm text-orange-600 dark:text-orange-400/70 mt-1">
                          {language === 'he' ? "פרופיל מוסתר" : "Hidden profile"}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2 bg-orange-100 dark:bg-orange-500/20 px-2 py-1 rounded-full">
                        <span className="text-xs text-orange-800 dark:text-orange-400">
                          {language === 'he' ? "מוסתר" : "Hidden"}
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex justify-end">
                      <button
                        onClick={() => handleRestoreProfile(profileId, profileId.replace('_', ' '))}
                        disabled={isRestoringProfile === profileId}
                        className="bg-green-100 dark:bg-green-500/20 hover:bg-green-200 dark:hover:bg-green-500/30 text-green-800 dark:text-green-400 font-medium py-2 px-4 rounded-lg border border-green-300 dark:border-green-500/30 transition-colors disabled:opacity-50 flex items-center space-x-2"
                      >
                        {isRestoringProfile === profileId ? (
                          <>
                            <span className="animate-spin">⏳</span>
                            <span>{language === 'he' ? "משחזר..." : "Restoring..."}</span>
                          </>
                        ) : (
                          <>
                            <span>↩️</span>
                            <span>{language === 'he' ? "שחזר פרופיל" : "Restore Profile"}</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Profiles Grid */}
        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 shadow-lg">
          <div className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {paginatedProfiles.map((profile) => (
                <div
                  key={profile.id}
                  className={`bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border p-6 transition-all shadow-lg ${
                    profile.isActive
                      ? "border-green-500 dark:border-green-500/50 bg-green-50 dark:bg-green-500/5"
                      : "border-gray-300 dark:border-green-500/20 hover:border-green-400 dark:hover:border-green-500/30"
                  }`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-green-800 dark:text-green-400">
                        {profile.name}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-green-400/70 mt-1">
                        {profile.description}
                      </p>
                    </div>
                    {profile.isActive && (
                      <div className="flex items-center space-x-2 bg-green-100 dark:bg-green-500/20 px-3 py-1 rounded-full">
                        <Check className="w-4 h-4 text-green-600 dark:text-green-500" />
                        <span className="text-sm text-green-800 dark:text-green-400">
                          {t("rag.profile.active")}
                        </span>
                      </div>
                    )}
                  </div>

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
                            {t("rag.focus")}:
                          </span>
                          <p className="text-gray-800 dark:text-green-300 text-xs mt-1">
                            {profile.characteristics.focus}
                          </p>
                        </div>
                        <div className="text-sm">
                          <span className="text-gray-600 dark:text-green-400/70">
                            {t("rag.bestFor")}:
                          </span>
                          <p className="text-gray-800 dark:text-green-300 text-xs mt-1">
                            {profile.characteristics.bestFor}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    {!profile.isActive && (
                      <button
                        onClick={() => handleProfileChange(profile.id)}
                        disabled={loading}
                        className="flex-1 bg-green-100 dark:bg-green-500/20 hover:bg-green-200 dark:hover:bg-green-500/30 text-green-800 dark:text-green-400 font-medium py-2 px-4 rounded-lg border border-green-300 dark:border-green-500/30 transition-colors disabled:opacity-50"
                      >
                        {loading
                          ? t("rag.switching") || "מחליף..."
                          : t("rag.apply.profile")}
                      </button>
                    )}
                    {!profile.isActive && (
                      <button
                        onClick={() =>
                          handleDeleteProfile(
                            profile.id,
                            profile.name,
                            profile.isCustom || false
                          )
                        }
                        disabled={isDeletingProfile === profile.id}
                        className={`font-medium py-2 px-4 rounded-lg border transition-colors disabled:opacity-50 ${
                          profile.isCustom
                            ? "bg-red-100 dark:bg-red-500/20 hover:bg-red-200 dark:hover:bg-red-500/30 text-red-800 dark:text-red-400 border-red-300 dark:border-red-500/30"
                            : "bg-gray-100 dark:bg-gray-500/20 hover:bg-gray-200 dark:hover:bg-gray-500/30 text-gray-800 dark:text-gray-400 border-gray-300 dark:border-gray-500/30"
                        }`}
                        title={
                          profile.isCustom
                            ? t("rag.delete.profile") || "מחק פרופיל"
                            : t("rag.hide.profile") || "הסתר פרופיל"
                        }
                      >
                        {isDeletingProfile === profile.id
                          ? "..."
                          : profile.isCustom
                          ? "🗑️"
                          : "👁️‍🗨️"}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Pagination */}
          {profiles.length > profilesItemsPerPage && (
            <div className="px-6 py-3 border-t border-gray-300 dark:border-green-500/20">
              <Pagination
                currentPage={profilesCurrentPage}
                totalItems={profiles.length}
                itemsPerPage={profilesItemsPerPage}
                onPageChange={setProfilesCurrentPage}
              />
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderPerformance = () => (
    <div className="space-y-6">
      <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-6 shadow-lg">
        <h3 className="text-lg font-semibold text-green-600 dark:text-green-400 mb-4">
          {t("rag.currentProfileConfig") || "קונפיגורציה פרופיל נוכחי"}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-2">
              {profiles.find((p) => p.isActive)?.config.similarityThreshold ||
                "N/A"}
            </div>
            <p className="text-sm text-gray-600 dark:text-green-400/70">
              {t("rag.similarity.threshold") || "סף דמיון"}
            </p>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-2">
              {profiles.find((p) => p.isActive)?.config.maxChunks || "N/A"}
            </div>
            <p className="text-sm text-gray-600 dark:text-green-400/70">
              {t("rag.max.chunks") || "צ'אנקים מקסימליים"}
            </p>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-2">
              {profiles.find((p) => p.isActive)?.config.temperature || "N/A"}
            </div>
            <p className="text-sm text-gray-600 dark:text-green-400/70">
              {t("rag.temperature") || "טמפרטורה"}
            </p>
          </div>
        </div>

        <div className="mt-6 bg-gray-50 dark:bg-black/40 rounded-lg p-4">
          <h4 className="text-md font-semibold text-gray-800 dark:text-green-400 mb-3">
            {t("rag.expectedBehavior") || "התנהגות צפויה"}
          </h4>
          <div className="space-y-2">
            <p className="text-gray-800 dark:text-green-300 text-sm">
              <span className="text-gray-600 dark:text-green-400/70">
                {t("rag.focus")}:
              </span>{" "}
              {profiles.find((p) => p.isActive)?.characteristics.focus}
            </p>
            <p className="text-gray-800 dark:text-green-300 text-sm">
              <span className="text-gray-600 dark:text-green-400/70">
                {t("rag.expectedSpeed")}:
              </span>{" "}
              {profiles.find((p) => p.isActive)?.characteristics.expectedSpeed}
            </p>
            <p className="text-gray-800 dark:text-green-300 text-sm">
              <span className="text-gray-600 dark:text-green-400/70">
                {t("rag.expectedQuality")}:
              </span>{" "}
              {
                profiles.find((p) => p.isActive)?.characteristics
                  .expectedQuality
              }
            </p>
            <p className="text-gray-800 dark:text-green-300 text-sm">
              <span className="text-gray-600 dark:text-green-400/70">
                {t("rag.bestFor")}:
              </span>{" "}
              {profiles.find((p) => p.isActive)?.characteristics.bestFor}
            </p>
            <p className="text-orange-800 dark:text-yellow-300 text-sm">
              <span className="text-orange-600 dark:text-yellow-400/70">
                {t("rag.tradeoffs")}:
              </span>{" "}
              {profiles.find((p) => p.isActive)?.characteristics.tradeoffs}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-6 shadow-lg">
        <h3 className="text-lg font-semibold text-green-600 dark:text-green-400 mb-4">
          {t("rag.profilesComparison") || "השוואת פרופילים"}
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-300 dark:border-green-500/20">
                <th
                  className={`py-3 text-gray-800 dark:text-green-400 ${
                    language === "he" ? "text-right" : "text-left"
                  }`}
                >
                  {t("rag.profileName") || "שם פרופיל"}
                </th>
                <th
                  className={`py-3 text-gray-800 dark:text-green-400 ${
                    language === "he" ? "text-right" : "text-left"
                  }`}
                >
                  {t("rag.similarity.threshold") || "סף דמיון"}
                </th>
                <th
                  className={`py-3 text-gray-800 dark:text-green-400 ${
                    language === "he" ? "text-right" : "text-left"
                  }`}
                >
                  {t("rag.max.chunks") || "צ'אנקים מקס"}
                </th>
                <th
                  className={`py-3 text-gray-800 dark:text-green-400 ${
                    language === "he" ? "text-right" : "text-left"
                  }`}
                >
                  {t("rag.focus") || "מיקוד"}
                </th>
                <th
                  className={`py-3 text-gray-800 dark:text-green-400 ${
                    language === "he" ? "text-right" : "text-left"
                  }`}
                >
                  {t("rag.status") || "סטטוס"}
                </th>
              </tr>
            </thead>
            <tbody>
              {profiles.map((profile) => (
                <tr
                  key={profile.id}
                  className="border-b border-gray-200 dark:border-green-500/10"
                >
                  <td
                    className={`py-3 text-gray-800 dark:text-green-300 ${
                      language === "he" ? "text-right" : "text-left"
                    }`}
                  >
                    {profile.name}
                  </td>
                  <td
                    className={`py-3 text-gray-600 dark:text-green-400/70 ${
                      language === "he" ? "text-right" : "text-left"
                    }`}
                  >
                    {profile.config.similarityThreshold}
                  </td>
                  <td
                    className={`py-3 text-gray-600 dark:text-green-400/70 ${
                      language === "he" ? "text-right" : "text-left"
                    }`}
                  >
                    {profile.config.maxChunks}
                  </td>
                  <td
                    className={`py-3 text-gray-600 dark:text-green-400/70 ${
                      language === "he" ? "text-right" : "text-left"
                    } max-w-xs truncate`}
                  >
                    {profile.characteristics.focus}
                  </td>
                  <td
                    className={`py-3 ${
                      language === "he" ? "text-right" : "text-left"
                    }`}
                  >
                    {profile.isActive ? (
                      <span className="text-green-600 dark:text-green-500">
                        {t("rag.profile.active") || "פעיל"}
                      </span>
                    ) : (
                      <span className="text-gray-500 dark:text-green-400/50">
                        {t("rag.profile.inactive") || "לא פעיל"}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderTestCenter = () => (
    <div className="space-y-6">
      <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-6 shadow-lg">
        <h3 className="text-lg font-semibold text-green-600 dark:text-green-400 mb-4">
          {t("rag.test.center")}
        </h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
              {t("rag.test.query")}
            </label>
            <input
              type="text"
              value={testQuery}
              onChange={(e) => setTestQuery(e.target.value)}
              placeholder={t("rag.test.placeholder") || "הכנס שאילתה לבדיקה..."}
              className="w-full px-4 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-green-300 placeholder-gray-500 dark:placeholder-green-400/50 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none transition-colors"
              dir="rtl"
            />
          </div>

          <button
            onClick={handleRunTest}
            disabled={!testQuery.trim() || isRunningTest}
            className="bg-green-100 dark:bg-green-500/20 hover:bg-green-200 dark:hover:bg-green-500/30 text-green-800 dark:text-green-400 font-medium py-2 px-6 rounded-lg border border-green-300 dark:border-green-500/30 transition-colors disabled:opacity-50 flex items-center space-x-2"
          >
            {isRunningTest ? (
              <>
                <Clock className="w-4 h-4 animate-spin" />
                <span>{t("rag.runningTest") || "מריץ בדיקה..."}</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>{t("rag.run.test")}</span>
              </>
            )}
          </button>
        </div>

        {testResult && (
          <div className="mt-6 bg-gray-50 dark:bg-black/50 rounded-lg p-4 border border-gray-200 dark:border-green-500/20">
            <h4 className="text-md font-semibold text-gray-800 dark:text-green-400 mb-3">
              {t("rag.test.results") || "תוצאות הבדיקה"}
            </h4>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600 dark:text-green-400/70">
                  {t("rag.query") || "שאילתה"}:
                </p>
                <div className="text-gray-800 dark:text-green-300" dir="rtl">
                  {testResult.query}
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-green-400/70">
                  {t("rag.answer") || "תשובה"}:
                </p>
                <AIResponseRenderer 
                  content={testResult.answer}
                  className="text-gray-800 dark:text-green-300"
                />
              </div>

              {testResult.chunkText && (
                <div>
                  <p className="text-sm text-gray-600 dark:text-green-400/70 mb-2">
                    {t("rag.chunkSource") || "מקור הטקסט (צ'אנק):"}
                  </p>
                  <div className="bg-white dark:bg-black/30 border border-gray-300 dark:border-green-500/30 rounded-lg p-3">
                    <div
                      className="text-gray-800 dark:text-green-300 text-sm leading-relaxed"
                      dir="rtl"
                      style={{
                        whiteSpace: "pre-wrap",
                        wordBreak: "break-word",
                        fontFamily: "inherit",
                      }}
                    >
                      {showFullChunk
                        ? testResult.chunkText
                        : `${testResult.chunkText.substring(0, 200)}${
                            testResult.chunkText.length > 200 ? "..." : ""
                          }`}
                    </div>
                    {testResult.chunkText.length > 200 && (
                      <button
                        onClick={() => setShowFullChunk(!showFullChunk)}
                        className="mt-2 text-green-600 dark:text-green-400 hover:text-green-800 dark:hover:text-green-300 text-sm font-medium flex items-center gap-1 transition-colors"
                      >
                        {showFullChunk ? (
                          <>
                            <span>{t("rag.showLess") || "הצג פחות"}</span>
                            <svg
                              className="w-4 h-4 transform rotate-180"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M19 9l-7 7-7-7"
                              />
                            </svg>
                          </>
                        ) : (
                          <>
                            <span>{t("rag.viewMore") || "הצג עוד"}</span>
                            <svg
                              className="w-4 h-4"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M19 9l-7 7-7-7"
                              />
                            </svg>
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-3 gap-4 mt-4">
                <div>
                  <p className="text-xs text-gray-500 dark:text-green-400/50">
                    {t("rag.response.timeShort") || "זמן תגובה"}
                  </p>
                  <p className="text-gray-800 dark:text-green-300 font-semibold">
                    {testResult.responseTime}ms
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-green-400/50">
                    {t("rag.sourcesFound") || "מקורות נמצאו"}
                  </p>
                  <p className="text-gray-800 dark:text-green-300 font-semibold">
                    {testResult.sourcesFound}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-green-400/50">
                    {t("rag.chunks") || "צ'אנקים"}
                  </p>
                  <p className="text-gray-800 dark:text-green-300 font-semibold">
                    {testResult.chunks}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeSubItem) {
      case "profiles":
        return renderProfiles();
      case "performance":
        return renderPerformance();
      case "test":
        return renderTestCenter();
      default:
        return renderOverview();
    }
  };

  if (loading && profiles.length === 0) {
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
                : ""}
            </span>
          )}
        </h2>
      </div>

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

      {renderContent()}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && modalProfileData && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-black/80 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-red-500/30 max-w-md w-full shadow-2xl">
            <div className="p-6">
              <div className="flex items-center mb-4">
                <AlertCircle className="w-6 h-6 text-red-600 dark:text-red-400 mr-3" />
                <h3 className="text-lg font-semibold text-gray-800 dark:text-red-400">
                  {t("rag.confirmDelete.title")}
                </h3>
              </div>
              
              <div className="mb-6">
                <p className="text-gray-700 dark:text-gray-300 mb-3">
                  {modalProfileData.isCustom 
                    ? t("rag.confirmDelete.customProfile", { profileName: modalProfileData.name })
                    : t("rag.confirmDelete.builtinProfile", { profileName: modalProfileData.name })
                  }
                </p>
                {!modalProfileData.isCustom && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 bg-yellow-50 dark:bg-yellow-500/10 border border-yellow-200 dark:border-yellow-500/20 rounded p-3">
                    {t("rag.confirmDelete.builtinNote")}
                  </p>
                )}
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowDeleteModal(false);
                    setModalProfileData(null);
                  }}
                  className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
                >
                  {t("rag.confirmDelete.cancelButton")}
                </button>
                <button
                  onClick={handleConfirmDelete}
                  disabled={isDeletingProfile === modalProfileData.id}
                  className="px-4 py-2 text-white bg-red-600 hover:bg-red-700 disabled:opacity-50 rounded-lg transition-colors"
                >
                  {isDeletingProfile === modalProfileData.id ? (
                    "..."
                  ) : modalProfileData.isCustom ? (
                    t("rag.confirmDelete.confirmButton")
                  ) : (
                    t("rag.confirmDelete.hideButton")
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Restore Confirmation Modal */}
      {showRestoreModal && modalProfileData && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-black/80 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/30 max-w-md w-full shadow-2xl">
            <div className="p-6">
              <div className="flex items-center mb-4">
                <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400 mr-3" />
                <h3 className="text-lg font-semibold text-gray-800 dark:text-green-400">
                  {t("rag.confirmRestore.title")}
                </h3>
              </div>
              
              <div className="mb-6">
                <p className="text-gray-700 dark:text-gray-300">
                  {t("rag.confirmRestore.message", { profileName: modalProfileData.name })}
                </p>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowRestoreModal(false);
                    setModalProfileData(null);
                  }}
                  className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
                >
                  {t("rag.confirmRestore.cancelButton")}
                </button>
                <button
                  onClick={handleConfirmRestore}
                  disabled={isRestoringProfile === modalProfileData.id}
                  className="px-4 py-2 text-white bg-green-600 hover:bg-green-700 disabled:opacity-50 rounded-lg transition-colors"
                >
                  {isRestoringProfile === modalProfileData.id ? "..." : t("rag.confirmRestore.confirmButton")}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// קומפונט ליצירת פרופיל חדש
interface CreateProfileModalProps {
  language: Language;
  onSubmit: (profileData: Partial<RAGProfile>) => void;
  onCancel: () => void;
  isCreating: boolean;
}

const CreateProfileModal: React.FC<CreateProfileModalProps> = ({
  onSubmit,
  onCancel,
  isCreating,
}) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    config: {
      similarityThreshold: 0.4,
      maxChunks: 15,
      temperature: 0.1,
      modelName: "gemini-2.0-flash",
      chunkSize: 1500,
      chunkOverlap: 200,
      maxContextTokens: 8000,
      targetTokensPerChunk: 300,
      hybridSemanticWeight: 0.7,
      hybridKeywordWeight: 0.3,
    },
    characteristics: {
      focus: "",
      expectedSpeed: "",
      expectedQuality: "",
      bestFor: "",
      tradeoffs: "",
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) return;

    onSubmit({
      id: formData.name.toLowerCase().replace(/\s+/g, "_"),
      name: formData.name,
      description: formData.description,
      config: formData.config,
      characteristics: formData.characteristics,
      isActive: false,
    });
  };

  const handleConfigChange = (key: string, value: number | string) => {
    setFormData((prev) => ({
      ...prev,
      config: {
        ...prev.config,
        [key]: value,
      },
    }));
  };

  const handleCharacteristicChange = (key: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      characteristics: {
        ...prev.characteristics,
        [key]: value,
      },
    }));
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-black/80 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/30 max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-gray-800 dark:text-green-400">
              {t("rag.create.new.profile") || "יצירת פרופיל חדש"}
            </h3>
            <button
              onClick={onCancel}
              className="text-gray-600 dark:text-green-400/70 hover:text-gray-800 dark:hover:text-green-400 text-xl"
            >
              ✕
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* פרטי פרופיל בסיסיים */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
                  {t("rag.profileFormName") || "שם הפרופיל"}
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, name: e.target.value }))
                  }
                  className="w-full px-4 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-green-300 placeholder-gray-500 dark:placeholder-green-400/50 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  placeholder={
                    t("rag.profileFormNamePlaceholder") || "הכנס שם לפרופיל..."
                  }
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
                  {t("rag.profileFormDescription") || "תיאור"}
                </label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      description: e.target.value,
                    }))
                  }
                  className="w-full px-4 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-green-300 placeholder-gray-500 dark:placeholder-green-400/50 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  placeholder={
                    t("rag.profileFormDescriptionPlaceholder") ||
                    "תיאור הפרופיל..."
                  }
                />
              </div>
            </div>

            {/* הגדרות קונפיגורציה */}
            <div className="bg-gray-100 dark:bg-black/30 rounded-lg p-4 border border-gray-300 dark:border-green-500/20">
              <h4 className="text-lg font-medium text-gray-800 dark:text-green-400 mb-4">
                {t("rag.configurationSettings") || "הגדרות קונפיגורציה"}
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm text-gray-600 dark:text-green-400/70 mb-2">
                    {t("rag.similarity.threshold") || "סף דמיון"} (0.0-1.0)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={formData.config.similarityThreshold}
                    onChange={(e) =>
                      handleConfigChange(
                        "similarityThreshold",
                        parseFloat(e.target.value)
                      )
                    }
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 dark:text-green-400/70 mb-2">
                    {t("rag.max.chunks") || "צ'אנקים מקסימליים"}
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={formData.config.maxChunks}
                    onChange={(e) =>
                      handleConfigChange("maxChunks", parseInt(e.target.value))
                    }
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 dark:text-green-400/70 mb-2">
                    {t("rag.temperature") || "טמפרטורה"} (0.0-1.0)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={formData.config.temperature}
                    onChange={(e) =>
                      handleConfigChange(
                        "temperature",
                        parseFloat(e.target.value)
                      )
                    }
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 dark:text-green-400/70 mb-2">
                    {t("rag.chunkSize") || "גודל צ'אנק"}
                  </label>
                  <input
                    type="number"
                    min="500"
                    max="5000"
                    value={formData.config.chunkSize}
                    onChange={(e) =>
                      handleConfigChange("chunkSize", parseInt(e.target.value))
                    }
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 dark:text-green-400/70 mb-2">
                    {t("rag.chunkOverlap") || "חפיפת צ'אנקים"}
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="1000"
                    value={formData.config.chunkOverlap}
                    onChange={(e) =>
                      handleConfigChange(
                        "chunkOverlap",
                        parseInt(e.target.value)
                      )
                    }
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 dark:text-green-400/70 mb-2">
                    {t("rag.maxContext") || "קונטקסט מקסימלי"}
                  </label>
                  <input
                    type="number"
                    min="1000"
                    max="20000"
                    value={formData.config.maxContextTokens}
                    onChange={(e) =>
                      handleConfigChange(
                        "maxContextTokens",
                        parseInt(e.target.value)
                      )
                    }
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  />
                </div>
              </div>
            </div>

            {/* מאפיינים */}
            <div className="bg-gray-100 dark:bg-black/30 rounded-lg p-4 border border-gray-300 dark:border-green-500/20">
              <h4 className="text-lg font-medium text-gray-800 dark:text-green-400 mb-4">
                {t("rag.characteristics") || "מאפיינים"}
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-600 dark:text-green-400/70 mb-2">
                    {t("rag.focus") || "מיקוד"}
                  </label>
                  <input
                    type="text"
                    value={formData.characteristics.focus}
                    onChange={(e) =>
                      handleCharacteristicChange("focus", e.target.value)
                    }
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                    placeholder={
                      t("rag.focusPlaceholder") || "על מה הפרופיל מתמקד..."
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 dark:text-green-400/70 mb-2">
                    {t("rag.bestFor") || "הכי טוב עבור"}
                  </label>
                  <input
                    type="text"
                    value={formData.characteristics.bestFor}
                    onChange={(e) =>
                      handleCharacteristicChange("bestFor", e.target.value)
                    }
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                    placeholder={
                      t("rag.bestForPlaceholder") || "מתאים ביותר עבור..."
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 dark:text-green-400/70 mb-2">
                    {t("rag.expectedSpeed") || "מהירות צפויה"}
                  </label>
                  <input
                    type="text"
                    value={formData.characteristics.expectedSpeed}
                    onChange={(e) =>
                      handleCharacteristicChange(
                        "expectedSpeed",
                        e.target.value
                      )
                    }
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                    placeholder={
                      t("rag.expectedSpeedPlaceholder") || "מהיר/בינוני/איטי..."
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 dark:text-green-400/70 mb-2">
                    {t("rag.expectedQuality") || "איכות צפויה"}
                  </label>
                  <input
                    type="text"
                    value={formData.characteristics.expectedQuality}
                    onChange={(e) =>
                      handleCharacteristicChange(
                        "expectedQuality",
                        e.target.value
                      )
                    }
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                    placeholder={
                      t("rag.expectedQualityPlaceholder") ||
                      "גבוה/בינוני/בסיסי..."
                    }
                  />
                </div>
              </div>
              <div className="mt-4">
                <label className="block text-sm text-gray-600 dark:text-green-400/70 mb-2">
                  {t("rag.tradeoffs") || "פשרות"}
                </label>
                <textarea
                  value={formData.characteristics.tradeoffs}
                  onChange={(e) =>
                    handleCharacteristicChange("tradeoffs", e.target.value)
                  }
                  className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  placeholder={
                    t("rag.tradeoffsPlaceholder") || "מה הפשרות בפרופיל הזה..."
                  }
                  rows={3}
                />
              </div>
            </div>

            {/* כפתורי פעולה */}
            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={onCancel}
                className="px-6 py-2 border border-gray-300 dark:border-green-500/30 text-gray-700 dark:text-green-400 rounded-lg hover:bg-gray-100 dark:hover:bg-green-500/10 transition-colors"
              >
                {t("rag.cancel") || "ביטול"}
              </button>
              <button
                type="submit"
                disabled={isCreating || !formData.name.trim()}
                className="px-6 py-2 bg-green-100 dark:bg-green-500/20 border border-green-300 dark:border-green-500/30 text-green-800 dark:text-green-400 rounded-lg hover:bg-green-200 dark:hover:bg-green-500/30 transition-colors disabled:opacity-50 flex items-center space-x-2"
              >
                {isCreating ? (
                  <>
                    <Clock className="w-4 h-4 animate-spin" />
                    <span>{t("rag.creating") || "יוצר..."}</span>
                  </>
                ) : (
                  <span>{t("rag.create.profile") || "צור פרופיל"}</span>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
