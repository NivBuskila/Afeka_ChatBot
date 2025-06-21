import { useCallback, useEffect, useMemo } from 'react'
import { DocumentHandlerService, type DocumentHandlerCallbacks } from '../services/handlers/DocumentHandlerService'
import { UserHandlerService, type UserHandlerCallbacks } from '../services/handlers/UserHandlerService'
import { DataRefreshService, type DataRefreshCallbacks } from '../services/handlers/DataRefreshService'
import type { Document } from '../config/supabase'
import type { AdminState, AdminStateActions } from './useAdminState'

interface UseDataManagementProps {
  state: AdminState
  actions: AdminStateActions
}

export const useDataManagement = ({ state, actions }: UseDataManagementProps) => {
  const {
    selectedDocument,
    selectedUser,
    isInitialLoading,
    isRefreshing,
    activeItem,
  } = state

  const {
    setDocuments,
    setAnalytics,
    setIsInitialLoading,
    setIsRefreshing,
    setShowUploadModal,
    setShowDeleteModal,
    setShowDeleteUserModal,
    setShowEditDocumentModal,
    setSelectedDocument,
    setSelectedUser,
    showSuccessMessage,
    showErrorMessage,
  } = actions
  
  // Create callback objects for the handler services
  const documentCallbacks: DocumentHandlerCallbacks = useMemo(() => ({
    onSuccess: showSuccessMessage,
    onError: showErrorMessage,
    onDocumentsUpdate: setDocuments,
    onLoadingChange: setIsRefreshing,
    onModalClose: (modalType) => {
      switch (modalType) {
        case 'upload':
          setShowUploadModal(false);
          break;
        case 'edit':
          setShowEditDocumentModal(false);
          break;
        case 'delete':
          setShowDeleteModal(false);
          break;
      }
    },
    onSelectedDocumentChange: setSelectedDocument,
  }), [
    showSuccessMessage, 
    showErrorMessage, 
    setDocuments, 
    setIsRefreshing,
    setShowUploadModal,
    setShowEditDocumentModal,
    setShowDeleteModal,
    setSelectedDocument
  ]);

  const dataRefreshCallbacks: DataRefreshCallbacks = useMemo(() => ({
    onSuccess: showSuccessMessage,
    onError: showErrorMessage,
    onDocumentsUpdate: setDocuments,
    onAnalyticsUpdate: setAnalytics,
    onInitialLoadingChange: setIsInitialLoading,
    onRefreshingChange: setIsRefreshing,
  }), [
    showSuccessMessage, 
    showErrorMessage, 
    setDocuments, 
    setAnalytics,
    setIsInitialLoading,
    setIsRefreshing
  ]);

  // Create service instances
  const documentHandlerService = useMemo(() => 
    new DocumentHandlerService(documentCallbacks), 
    [documentCallbacks]
  );

  const dataRefreshService = useMemo(() => 
    new DataRefreshService(dataRefreshCallbacks), 
    [dataRefreshCallbacks]
  );

  // Create stable analytics refresh function
  const handleAnalyticsRefresh = useCallback(async () => {
    await dataRefreshService.fetchAnalyticsOnly();
  }, [dataRefreshService]);

  // Now create userCallbacks with stable analytics refresh function
  const userCallbacks: UserHandlerCallbacks = useMemo(() => ({
    onSuccess: showSuccessMessage,
    onError: showErrorMessage,
    onLoadingChange: setIsRefreshing,
    onModalClose: (modalType) => {
      if (modalType === 'deleteUser') {
        setShowDeleteUserModal(false);
      }
    },
    onSelectedUserChange: setSelectedUser,
    onAnalyticsRefresh: handleAnalyticsRefresh,
  }), [
    showSuccessMessage, 
    showErrorMessage, 
    setIsRefreshing,
    setShowDeleteUserModal,
    setSelectedUser,
    handleAnalyticsRefresh
  ]);

  const userHandlerService = useMemo(() => 
    new UserHandlerService(userCallbacks), 
    [userCallbacks]
  );

  // Wrapper functions to maintain the same interface
  const fetchInitialData = useCallback(async () => {
    await dataRefreshService.fetchInitialData();
  }, [dataRefreshService]);

  const fetchAnalyticsOnly = useCallback(async () => {
    if (isRefreshing) return; // Prevent duplicate calls
    await dataRefreshService.fetchAnalyticsOnly();
  }, [dataRefreshService, isRefreshing]);

  const refreshData = useCallback(async () => {
    await dataRefreshService.refreshAllData();
  }, [dataRefreshService]);

  // Document handlers
  const handleEditDocument = useCallback((document: Document) => {
    setSelectedDocument(document);
    setShowEditDocumentModal(true);
  }, [setSelectedDocument, setShowEditDocumentModal]);

  const handleDeleteDocument = useCallback((document: Document) => {
    setSelectedDocument(document);
    setShowDeleteModal(true);
  }, [setSelectedDocument, setShowDeleteModal]);

  const handleUpload = useCallback(async (file: File) => {
    await documentHandlerService.uploadDocument(file);
  }, [documentHandlerService]);

  const handleUpdateDocument = useCallback(async (document: any, file: File) => {
    await documentHandlerService.updateDocument(document, file);
  }, [documentHandlerService]);

  const handleDelete = useCallback(async () => {
    if (!selectedDocument) return;
    await documentHandlerService.deleteDocument(selectedDocument);
  }, [documentHandlerService, selectedDocument]);

  // User handlers
  const handleDeleteUser = useCallback((user: any) => {
    setSelectedUser(user);
    setShowDeleteUserModal(true);
  }, [setSelectedUser, setShowDeleteUserModal]);

  const handleDeleteUserConfirm = useCallback(async () => {
    if (!selectedUser) return;
    await userHandlerService.confirmDeleteUser(selectedUser);
  }, [userHandlerService, selectedUser]);

  // Effects - with proper dependency management
  useEffect(() => {
    // Set up data listeners and fetch initial data
    const cleanup = dataRefreshService.setupDataListeners();
    fetchInitialData();

    return cleanup;
  }, [dataRefreshService, fetchInitialData]);

  // Separate useEffect for analytics refresh when navigating to analytics section
  // Use a ref to track if we've already fetched analytics for this session
  const hasInitializedRef = useCallback(() => {
    let hasInitialized = false;
    return {
      get: () => hasInitialized,
      set: (value: boolean) => { hasInitialized = value; }
    };
  }, [])();

  useEffect(() => {
    // Only fetch analytics when specifically viewing analytics sections
    // and not during initial load, and only once per navigation
    if (activeItem === 'analytics' && !isInitialLoading && !hasInitializedRef.get()) {
      hasInitializedRef.set(true);
      fetchAnalyticsOnly();
    } else if (activeItem !== 'analytics') {
      // Reset the flag when leaving analytics section
      hasInitializedRef.set(false);
    }
  }, [activeItem, isInitialLoading]); // Removed fetchAnalyticsOnly from dependencies

  return {
    // Data operations
    refreshData,
    fetchInitialData,
    fetchAnalyticsOnly,
    
    // Document operations
    handleUpload,
    handleUpdateDocument,
    handleDelete,
    handleEditDocument,
    handleDeleteDocument,
    
    // User operations
    handleDeleteUser,
    handleDeleteUserConfirm,

    // Service instances (for advanced usage)
    documentHandlerService,
    userHandlerService,
    dataRefreshService,
  }
}