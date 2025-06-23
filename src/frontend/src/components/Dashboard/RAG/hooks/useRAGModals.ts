import { useState } from 'react';

interface ModalProfileData {
  id: string;
  name: string;
  isCustom: boolean;
}

export function useRAGModals() {
  const [showCreateProfile, setShowCreateProfile] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showRestoreModal, setShowRestoreModal] = useState(false);
  const [showActiveProfileError, setShowActiveProfileError] = useState(false);
  const [modalProfileData, setModalProfileData] = useState<ModalProfileData | null>(null);
  const [activeProfileErrorData, setActiveProfileErrorData] = useState<{ profileName: string } | null>(null);

  const openDeleteModal = (profileId: string, profileName: string, isCustom: boolean = true) => {
    setModalProfileData({ id: profileId, name: profileName, isCustom });
    setShowDeleteModal(true);
  };

  const openRestoreModal = (profileId: string, profileName: string) => {
    setModalProfileData({ id: profileId, name: profileName, isCustom: false });
    setShowRestoreModal(true);
  };

  const closeDeleteModal = () => {
    setShowDeleteModal(false);
    setModalProfileData(null);
  };

  const closeRestoreModal = () => {
    setShowRestoreModal(false);
    setModalProfileData(null);
  };

  const closeCreateModal = () => {
    setShowCreateProfile(false);
  };

  const openCreateModal = () => {
    setShowCreateProfile(true);
  };

  const openActiveProfileError = (profileName: string) => {
    setActiveProfileErrorData({ profileName });
    setShowActiveProfileError(true);
  };

  const closeActiveProfileError = () => {
    setShowActiveProfileError(false);
    setActiveProfileErrorData(null);
  };

  return {
    showCreateProfile,
    setShowCreateProfile,
    showDeleteModal,
    showRestoreModal,
    showActiveProfileError,
    modalProfileData,
    activeProfileErrorData,
    openDeleteModal,
    openRestoreModal,
    closeDeleteModal,
    closeRestoreModal,
    closeCreateModal,
    openCreateModal,
    openActiveProfileError,
    closeActiveProfileError,
  };
} 