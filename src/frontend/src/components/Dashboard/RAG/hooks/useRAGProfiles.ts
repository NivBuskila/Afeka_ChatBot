import { useState, useEffect, useCallback, useRef } from 'react';
import { ragService, RAGProfile } from '../RAGService';

type Language = "he" | "en";

export function useRAGProfiles(language: Language) {
  const [loading, setLoading] = useState(false);
  const [profiles, setProfiles] = useState<RAGProfile[]>([]);
  const [hiddenProfiles, setHiddenProfiles] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [showHiddenProfiles, setShowHiddenProfiles] = useState(false);
  const [isCreatingProfile, setIsCreatingProfile] = useState(false);
  const [isDeletingProfile, setIsDeletingProfile] = useState<string | null>(null);
  const [isRestoringProfile, setIsRestoringProfile] = useState<string | null>(null);

  // Pagination state
  const [profilesItemsPerPage, setProfilesItemsPerPage] = useState(10);
  const [profilesCurrentPage, setProfilesCurrentPage] = useState(1);

  // Debounce ref to prevent rapid successive calls
  const fetchTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastFetchTime = useRef<number>(0);
  const MIN_FETCH_INTERVAL = 1000;

  const fetchProfiles = useCallback(async () => {
    const now = Date.now();
    const timeSinceLastFetch = now - lastFetchTime.current;
    
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
      await fetchProfiles();
    } catch (error) {
      console.error("Error switching profile:", error);
      setError(`Failed to switch to profile: ${profileId}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProfile = async (profileData: Partial<RAGProfile>) => {
    setIsCreatingProfile(true);
    setError(null);
    try {
      await ragService.createProfile(profileData);
      await fetchProfiles();
    } catch (error) {
      console.error("Error creating profile:", error);
      setError("Failed to create profile");
    } finally {
      setIsCreatingProfile(false);
    }
  };

  const handleDeleteProfile = async (profileId: string, force: boolean = false) => {
    setIsDeletingProfile(profileId);
    setError(null);
    
    try {
      await ragService.deleteProfile(profileId, force);
      await fetchProfiles();
      await fetchHiddenProfiles();
    } catch (error) {
      console.error("Error deleting profile:", error);
      setError(
        `Failed to delete profile: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    } finally {
      setIsDeletingProfile(null);
    }
  };

  const handleRestoreProfile = async (profileId: string) => {
    setIsRestoringProfile(profileId);
    setError(null);
    
    try {
      await ragService.restoreProfile(profileId);
      await fetchProfiles();
      await fetchHiddenProfiles();
    } catch (error) {
      console.error("Error restoring profile:", error);
      setError(
        `Failed to restore profile: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    } finally {
      setIsRestoringProfile(null);
    }
  };

  const currentProfile = profiles.find((p) => p.isActive);

  // Pagination for profiles
  const startIndex = (profilesCurrentPage - 1) * profilesItemsPerPage;
  const endIndex = startIndex + profilesItemsPerPage;
  const paginatedProfiles = profiles.slice(startIndex, endIndex);

  return {
    loading,
    profiles,
    paginatedProfiles,
    hiddenProfiles,
    currentProfile,
    error,
    setError,
    showHiddenProfiles,
    setShowHiddenProfiles,
    isCreatingProfile,
    isDeletingProfile,
    isRestoringProfile,
    profilesItemsPerPage,
    setProfilesItemsPerPage,
    profilesCurrentPage,
    setProfilesCurrentPage,
    handleProfileChange,
    handleCreateProfile,
    handleDeleteProfile,
    handleRestoreProfile,
    fetchProfiles,
    fetchHiddenProfiles,
  };
} 