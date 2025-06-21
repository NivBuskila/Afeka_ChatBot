import { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { useTheme } from '../contexts/ThemeContext'
import type { Document } from '../config/supabase'
import { DashboardAnalytics } from '../services/analyticsService'

type Language = 'he' | 'en'

export interface AdminState {
  // UI State
  isSidebarCollapsed: boolean
  activeItem: string
  activeSubItem: string | null
  searchQuery: string
  
  // Modal States
  showUploadModal: boolean
  showDeleteModal: boolean
  showDeleteUserModal: boolean
  showEditDocumentModal: boolean
  
  // Selected Items
  selectedUser: any
  selectedDocument: Document | null
  
  // Data State
  documents: Document[]
  analytics: DashboardAnalytics
  
  // Loading States
  isInitialLoading: boolean
  isRefreshing: boolean
  
  // Theme & Language
  language: Language
  theme: 'light' | 'dark'
  
  // Messages
  successMessage: string
  errorMessage: string
  
  // Pagination State
  usersItemsPerPage: number
  usersCurrentPage: number
  adminsItemsPerPage: number
  adminsCurrentPage: number
}

export interface AdminStateActions {
  // UI Actions
  setIsSidebarCollapsed: (collapsed: boolean) => void
  setActiveItem: (item: string) => void
  setActiveSubItem: (subItem: string | null) => void
  setSearchQuery: (query: string) => void
  
  // Modal Actions
  setShowUploadModal: (show: boolean) => void
  setShowDeleteModal: (show: boolean) => void
  setShowDeleteUserModal: (show: boolean) => void
  setShowEditDocumentModal: (show: boolean) => void
  
  // Selected Items Actions
  setSelectedUser: (user: any) => void
  setSelectedDocument: (document: Document | null) => void
  
  // Data Actions
  setDocuments: (documents: Document[] | ((prev: Document[]) => Document[])) => void
  setAnalytics: (analytics: DashboardAnalytics) => void
  
  // Loading Actions
  setIsInitialLoading: (loading: boolean) => void
  setIsRefreshing: (refreshing: boolean) => void
  
  // Theme & Language Actions
  setLanguage: (language: Language) => void
  setTheme: (theme: 'light' | 'dark') => void
  
  // Message Actions
  showSuccessMessage: (message: string) => void
  showErrorMessage: (message: string) => void
  
  // Pagination Actions
  setUsersItemsPerPage: (itemsPerPage: number) => void
  setUsersCurrentPage: (page: number) => void
  setAdminsItemsPerPage: (itemsPerPage: number) => void
  setAdminsCurrentPage: (page: number) => void
  
  // Navigation Actions
  handleItemClick: (itemId: string) => void
  handleSubItemClick: (itemId: string, subItemId: string) => void
  handleLanguageChange: (newLanguage: Language) => void
  handleThemeChange: (newTheme: 'dark' | 'light') => void
}

export const useAdminState = (): AdminState & AdminStateActions => {
  const { t, i18n } = useTranslation()
  const { theme, setTheme: setContextTheme } = useTheme()
  
  // UI State
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [activeItem, setActiveItem] = useState('chatbot')
  const [activeSubItem, setActiveSubItem] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  
  // Modal States
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [showDeleteUserModal, setShowDeleteUserModal] = useState(false)
  const [showEditDocumentModal, setShowEditDocumentModal] = useState(false)
  
  // Selected Items
  const [selectedUser, setSelectedUser] = useState<any>(null)
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null)
  
  // Data State
  const [documents, setDocuments] = useState<Document[]>([])
  const [analytics, setAnalytics] = useState<DashboardAnalytics>({
    totalDocuments: 0,
    totalUsers: 0,
    totalAdmins: 0,
    recentDocuments: [],
    recentUsers: [],
    recentAdmins: [],
  })
  
  // Loading States
  const [isInitialLoading, setIsInitialLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  
  // Theme & Language
  const [language, setLanguage] = useState<Language>(i18n.language as Language)
  
  // Messages
  const [successMessage, setSuccessMessage] = useState<string>('')
  const [errorMessage, setErrorMessage] = useState<string>('')
  
  // Pagination State
  const [usersItemsPerPage, setUsersItemsPerPage] = useState(10)
  const [usersCurrentPage, setUsersCurrentPage] = useState(1)
  const [adminsItemsPerPage, setAdminsItemsPerPage] = useState(10)
  const [adminsCurrentPage, setAdminsCurrentPage] = useState(1)
  
  // Message Functions - Memoized for performance
  const showSuccessMessage = useCallback((message: string) => {
    setSuccessMessage(message)
    setErrorMessage('')
    setTimeout(() => setSuccessMessage(''), 3000)
  }, [])

  const showErrorMessage = useCallback((message: string) => {
    setErrorMessage(message)
    setSuccessMessage('')
    setTimeout(() => setErrorMessage(''), 5000)
  }, [])
  
  // Navigation Functions - Memoized for performance
  const handleItemClick = useCallback((itemId: string) => {
    setActiveItem(itemId)

    if (itemId === 'analytics') {
      setActiveSubItem('overview')
    } else if (itemId === 'documents') {
      setActiveSubItem('active')
    } else if (itemId === 'rag') {
      setActiveSubItem('overview')
    } else {
      setActiveSubItem(null)
    }
  }, [])

  const handleSubItemClick = useCallback((itemId: string, subItemId: string) => {
    setActiveItem(itemId)
    setActiveSubItem(subItemId)
  }, [])

  const handleLanguageChange = useCallback((newLanguage: Language) => {
    setLanguage(newLanguage)
  }, [])

  const handleThemeChange = useCallback((newTheme: 'dark' | 'light') => {
    setContextTheme(newTheme)
  }, [setContextTheme])
  
  // Effects for pagination reset
  useEffect(() => {
    const regularUsers = analytics.recentUsers.filter((user) => {
      return !analytics.recentAdmins?.some((admin) => admin.id === user.id)
    })
    const totalPages = Math.ceil(regularUsers.length / usersItemsPerPage)
    if (usersCurrentPage > totalPages && totalPages > 0) {
      setUsersCurrentPage(1)
    }
  }, [analytics.recentUsers, analytics.recentAdmins, usersItemsPerPage, usersCurrentPage])

  useEffect(() => {
    const adminsTotalPages = Math.ceil(analytics.recentAdmins.length / adminsItemsPerPage)
    if (adminsCurrentPage > adminsTotalPages && adminsTotalPages > 0) {
      setAdminsCurrentPage(1)
    }
  }, [analytics.recentAdmins.length, adminsItemsPerPage, adminsCurrentPage])

  // Language and theme effects
  useEffect(() => {
    document.documentElement.lang = language
    document.documentElement.dir = language === 'he' ? 'rtl' : 'ltr'
    i18n.changeLanguage(language)
  }, [language, i18n])

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [theme])
  
  return {
    // State
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
    
    // Actions
    setIsSidebarCollapsed,
    setActiveItem,
    setActiveSubItem,
    setSearchQuery,
    setShowUploadModal,
    setShowDeleteModal,
    setShowDeleteUserModal,
    setShowEditDocumentModal,
    setSelectedUser,
    setSelectedDocument,
    setDocuments,
    setAnalytics,
    setIsInitialLoading,
    setIsRefreshing,
    setLanguage,
    setTheme: handleThemeChange,
    showSuccessMessage,
    showErrorMessage,
    setUsersItemsPerPage,
    setUsersCurrentPage,
    setAdminsItemsPerPage,
    setAdminsCurrentPage,
    handleItemClick,
    handleSubItemClick,
    handleLanguageChange,
    handleThemeChange,
  }
}