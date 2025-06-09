import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard,
  MessageSquare,
  BarChart3,
  Users,
  UserCog,
  FileText,
  Upload,
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Bell,
  Search,
  Filter,
  Download,
  Trash2,
  Edit,
  Plus,
  X,
  AlertTriangle,
  Brain,
  Cpu,
  TrendingUp,
  Sun,
  Moon,
  Globe
} from 'lucide-react';
import './AdminDashboard.css';
import { translations } from './translations';
import ChatWindow from '../Chat/ChatWindow';
import { useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { AnalyticsOverview } from './AnalyticsOverview';
import { DocumentTable } from './DocumentTable';
import { UploadArea } from './UploadArea';
import { UploadModal } from './UploadModal';
import { EditDocumentModal } from './EditDocumentModal';
import { DeleteModal } from './DeleteModal';
import { RAGManagement } from './RAG/RAGManagement';
import { documentService } from '../../services/documentService';
import { userService } from '../../services/userService';
import { analyticsService, DashboardAnalytics } from '../../services/analyticsService';
// import type { Document } from '../../config/supabase';

// Local Document interface for AdminDashboard
interface Document {
  id: number;
  name: string;
  type: string;
  size: number;
  url: string;
  created_at: string;
  updated_at: string;
}
import { supabase } from '../../config/supabase';
import i18n from 'i18next';
import { cacheService } from '../../services/cacheService';
import LoadingScreen from '../LoadingScreen';

type Language = 'he' | 'en';

interface MenuItem {
  id: string;
  title: string;
  icon: React.ReactNode;
  subItems?: {
    id: string;
    title: string;
    icon: React.ReactNode;
  }[];
}

interface User {
  id: number;
  name: string;
  email: string;
  is_admin: boolean;
  lastLogin: string;
  status: 'active' | 'inactive';
}

interface AdminDashboardProps {
  onLogout: () => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ onLogout }) => {
  const { t, i18n } = useTranslation();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [activeItem, setActiveItem] = useState('chatbot');
  const [activeSubItem, setActiveSubItem] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<string>('all');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showDeleteUserModal, setShowDeleteUserModal] = useState(false);
  const [showEditDocumentModal, setShowEditDocumentModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<any>(null);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [analytics, setAnalytics] = useState<DashboardAnalytics>({
    totalDocuments: 0,
    totalUsers: 0,
    totalAdmins: 0,
    recentDocuments: [],
    recentUsers: [],
    recentAdmins: []
  });
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [language, setLanguage] = useState<Language>(i18n.language as Language);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<string>('chatbot');

  useEffect(() => {
    document.documentElement.lang = language;
    document.documentElement.dir = language === 'he' ? 'rtl' : 'ltr';
    i18n.changeLanguage(language);
  }, [language, i18n]);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setIsRefreshing(true);
        console.log("Fetching dashboard analytics...");
        
        // Get analytics data from service
        const analyticsData = await analyticsService.getDashboardAnalytics();
        
        console.log("Received analytics data:", analyticsData);
        
        setAnalytics(analyticsData);
      } catch (error) {
        console.error('Error fetching analytics:', error);
      } finally {
        setIsRefreshing(false);
      }
    };

    if (activeItem === 'analytics') {
      fetchAnalytics();
    }
  }, [activeItem, activeSubItem]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Check if cache is stale or needs refresh
        const forceRefresh = cacheService.isCacheStale('documents');
        
        console.log(`Fetching data, force refresh: ${forceRefresh}`);
        
        const [docs, analyticsData] = await Promise.all([
          documentService.getAllDocuments(),
          analyticsService.getDashboardAnalytics()
        ]);
        
        console.log('Fetched analytics data:', analyticsData);
        console.log('Users found:', analyticsData.recentUsers.length);
        console.log('Admins found:', analyticsData.recentAdmins.length);
        console.log('Documents found:', docs.length);
        
        setDocuments(docs);
        setAnalytics(analyticsData);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setIsInitialLoading(false);
      }
    };

    fetchData();
    
    // Listen for cache changes to refresh data when needed
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'documents_cache_invalidated') {
        console.log('Document cache was invalidated, refreshing data');
        fetchData();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const menuItems: MenuItem[] = [
    {
      id: 'chatbot',
      title: t('admin.sidebar.chatbotPreview'),
      icon: <MessageSquare className="w-5 h-5" />
    },
    {
      id: 'analytics',
      title: t('admin.sidebar.analytics'),
      icon: <BarChart3 className="w-5 h-5" />,
      subItems: [
        { id: 'overview', title: t('admin.sidebar.overview'), icon: <BarChart3 className="w-4 h-4" /> },
        { id: 'users', title: t('admin.sidebar.users'), icon: <Users className="w-4 h-4" /> },
        { id: 'admins', title: t('admin.sidebar.administrators'), icon: <UserCog className="w-4 h-4" /> }
      ]
    },
    {
      id: 'documents',
      title: t('admin.sidebar.knowledgeBase'),
      icon: <FileText className="w-5 h-5" />,
      subItems: [
        { id: 'upload', title: t('admin.sidebar.uploadDocuments'), icon: <Upload className="w-4 h-4" /> },
        { id: 'active', title: t('admin.sidebar.activeDocuments'), icon: <FileText className="w-4 h-4" /> }
      ]
    },
    {
      id: 'rag',
      title: t('rag.management'),
      icon: <Brain className="w-5 h-5" />,
      subItems: [
        { id: 'overview', title: t('rag.overview'), icon: <Brain className="w-4 h-4" /> },
        { id: 'profiles', title: t('rag.profile.selector'), icon: <Cpu className="w-4 h-4" /> },
        { id: 'performance', title: t('rag.performanceMonitor'), icon: <TrendingUp className="w-4 h-4" /> },
        { id: 'test', title: t('rag.test.center'), icon: <Search className="w-4 h-4" /> }
      ]
    },
    {
      id: 'settings',
      title: t('admin.sidebar.settings'),
      icon: <Settings className="w-5 h-5" />
    }
  ];

  const mockUsers: User[] = [
    { id: 1, name: 'ישראל ישראלי', email: 'israel@afeka.ac.il', is_admin: true, lastLogin: '2024-03-25 10:30', status: 'active' },
    { id: 2, name: 'שרה כהן', email: 'sara@afeka.ac.il', is_admin: false, lastLogin: '2024-03-25 09:15', status: 'active' },
    { id: 3, name: 'דוד לוי', email: 'david@afeka.ac.il', is_admin: false, lastLogin: '2024-03-24 15:45', status: 'inactive' },
  ];

  const mockDocuments: any[] = [
    { id: 1, name: i18n.language === 'he' ? 'תקנון אקדמי' : 'Academic Regulations', type: 'pdf', size: 2.5 * 1024 * 1024, url: '#', created_at: '2024-03-20' },
    { id: 2, name: i18n.language === 'he' ? 'מדריך למשתמש' : 'User Guide', type: 'pdf', size: 1.8 * 1024 * 1024, url: '#', created_at: '2024-03-18' },
    { id: 3, name: i18n.language === 'he' ? 'לוח זמנים' : 'Schedule', type: 'pdf', size: 3.2 * 1024 * 1024, url: '#', created_at: '2024-03-15' },
  ];

  // Manual data refresh function
  const refreshData = async () => {
    setIsRefreshing(true);
    try {
      console.log('Refreshing dashboard data...');
      const [docs, analyticsData] = await Promise.all([
        documentService.getAllDocuments(),
        analyticsService.getDashboardAnalytics()
      ]);
      
      console.log('Refreshed analytics data:', analyticsData);
      console.log('Users found after refresh:', analyticsData.recentUsers?.length || 0);
      console.log('Admins found after refresh:', analyticsData.recentAdmins?.length || 0);
      
      setDocuments(docs);
      setAnalytics(analyticsData);
      
      // Print debug information
      if (analyticsData.recentUsers?.length) {
        console.log('First user example:', analyticsData.recentUsers[0]);
      }
      if (analyticsData.recentAdmins?.length) {
        console.log('First admin example:', analyticsData.recentAdmins[0]);
      }
    } catch (error) {
      console.error('Error refreshing data:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleItemClick = (itemId: string) => {
    console.log("Setting active item to:", itemId);
    setActiveItem(itemId);
    
    if (itemId === 'analytics') {
      setActiveSubItem('overview');
    } else if (itemId === 'documents') {
      setActiveSubItem('active');
    } else if (itemId === 'rag') {
      setActiveSubItem('overview');
    } else {
      setActiveSubItem(null);
    }
    
    setActiveTab(itemId);
  };

  const handleSubItemClick = (itemId: string, subItemId: string) => {
    console.log(`Setting active item to: ${itemId}, subItem to: ${subItemId}`);
    setActiveItem(itemId);
    setActiveSubItem(subItemId);
  };

  const handleLogout = () => {
    onLogout();
  };

  const handleEditDocument = (document: Document) => {
    setSelectedDocument(document);
    setShowEditDocumentModal(true);
  };

  const handleDeleteDocument = (document: Document) => {
    setSelectedDocument(document);
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = () => {
    // Add delete logic here
    setShowDeleteModal(false);
    setSelectedDocument(null);
  };

  const handleUpload = async (file: File) => {
    try {
      // Verify user is authenticated before upload
      const { data: authData } = await supabase.auth.getSession();
      if (!authData.session) {
        console.error('User not authenticated');
        alert('יש להתחבר מחדש למערכת');
        return;
      }
      
      // Print debug information
      console.log('User ID:', authData.session.user.id);
      console.log('User email:', authData.session.user.email);
      
      // Check if user exists in users table
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select('id')
        .eq('id', authData.session.user.id)
        .single();
      
      // If user doesn't exist, try creating them (may fail due to RLS)
      if (userError || !userData) {
        console.error('User not found in database:', userError);
        
        // Try creating a new user record
        try {
          const { error: insertError } = await supabase
            .from('users')
            .insert({
              id: authData.session.user.id,
              email: authData.session.user.email || '',
              name: authData.session.user.email?.split('@')[0] || 'User',
              status: 'active'
            });
            
          if (insertError) {
            console.error('Failed to insert user record:', insertError);
            // Continue despite error, as we're already trying to bypass restrictions
          } else {
            console.log('Created new user record for', authData.session.user.email);
            
            // Check if user should be admin and add to admins table
            if (authData.session.user.user_metadata?.is_admin || 
                authData.session.user.user_metadata?.role === 'admin') {
              try {
                const { error: adminError } = await supabase
                  .from('admins')
                  .insert({
                    user_id: authData.session.user.id
                  });
                  
                if (adminError) {
                  console.error('Failed to insert admin record:', adminError);
                } else {
                  console.log('Created new admin record for', authData.session.user.email);
                }
              } catch (adminError) {
                console.error('Error creating admin record:', adminError);
              }
            }
          }
        } catch (createError) {
          console.error('Error creating user record:', createError);
          // Continue despite error
        }
      } else {
        console.log('Found existing user:', userData);
      }
      
      // Create safe filename without Hebrew characters
      const fileExt = file.name.split('.').pop() || '';
      const safeFileName = `${Date.now()}.${fileExt}`;
      const path = `documents/${safeFileName}`;
      
      console.log('Uploading file to path:', path);
      
      try {
        // Upload the file - direct access without RPC
        const { data: uploadData, error: uploadError } = await supabase.storage
          .from('documents')
          .upload(path, file);
        
        if (uploadError) {
          console.error('Error uploading file:', uploadError);
          alert(`שגיאה בהעלאת הקובץ: ${uploadError.message}`);
          return;
        }
        
        console.log('Upload successful:', uploadData);
        
        // Get public URL
        const { data: urlData } = supabase.storage
          .from('documents')
          .getPublicUrl(path);
        
        console.log('File URL:', urlData.publicUrl);
        
        try {
          // Create document record directly (not through RPC)
          const { data: docData, error: docError } = await supabase
            .from('documents')
            .insert({
              name: file.name,
              type: file.type,
              size: file.size,
              url: urlData.publicUrl
            })
            .select()
            .single();
          
          if (docError) {
            console.error('Error creating document record:', docError);
            alert(`שגיאה ביצירת רשומת מסמך: ${docError.message}`);
            return;
          }
          
          console.log('Document created successfully:', docData);
          
          // Attempt to add analytics record (may fail due to RLS)
          try {
            const { error: analyticsError } = await supabase
              .from('document_analytics')
              .insert({
                document_id: docData.id,
                user_id: authData.session.user.id,
                action: 'upload'
              });
            
            if (analyticsError) {
              console.error('Error adding analytics record:', analyticsError);
              // Continue despite error
            }
          } catch (analyticsError) {
            console.error('Failed to add analytics record:', analyticsError);
            // Continue despite error
          }
          
          setDocuments(prev => [docData, ...prev]);
          setShowUploadModal(false);
          
        } catch (docError) {
          console.error('Error in document creation:', docError);
          alert('אירעה שגיאה ביצירת רשומת המסמך');
        }
      } catch (uploadError) {
        console.error('Error in file upload process:', uploadError);
        alert('אירעה שגיאה בתהליך העלאת הקובץ');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('אירעה שגיאה בתהליך ההעלאה');
    }
  };

  const handleUpdateDocument = async (document: Document, file: File) => {
    try {
      setIsRefreshing(true);
      
      // First delete the old file from storage
      const storagePathMatch = document.url.match(/\/documents\/([^\/]+)$/); 
      const storagePath = storagePathMatch ? storagePathMatch[1] : null;
      
      if (storagePath) {
        try {
          // Delete the old file from storage
          const { error: removeError } = await supabase.storage
            .from('documents')
            .remove([`documents/${storagePath}`]);
            
          if (removeError) {
            console.error('Error removing old file:', removeError);
            // Continue anyway to try to upload the new file
          }
        } catch (removeError) {
          console.error('Error in file removal process:', removeError);
          // Continue anyway
        }
      }
      
      // Upload the new file
      const timestamp = Date.now();
      const fileExtension = file.name.split('.').pop() || '';
      const filePath = `documents/${timestamp}.${fileExtension}`;
      
      const { data: uploadData, error: uploadError } = await supabase.storage
        .from('documents')
        .upload(filePath, file);
      
      if (uploadError) {
        throw new Error(`Error uploading file: ${uploadError.message}`);
      }
      
      // Get URL for the uploaded file
      const { data: { publicUrl } } = supabase.storage
        .from('documents')
        .getPublicUrl(uploadData.path);
      
      // Update document record with new file information
      const { data: updatedDoc, error: updateError } = await supabase
        .from('documents')
        .update({
          name: file.name,
          type: file.type,
          size: file.size,
          url: publicUrl,
          updated_at: new Date().toISOString()
        })
        .eq('id', document.id)
        .select()
        .single();
      
      if (updateError) {
        throw new Error(`Error updating document: ${updateError.message}`);
      }
      
      // Update documents list
      setDocuments(prev => prev.map(doc => 
        doc.id === document.id ? updatedDoc : doc
      ));
      
      // Close modal
      setShowEditDocumentModal(false);
      setSelectedDocument(null);
      
      alert(t('documents.updateSuccess') || 'Document updated successfully');
      
    } catch (error) {
      console.error('Error updating document:', error);
      alert(t('documents.updateError') || 'Error updating document');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleDelete = async () => {
    try {
      // First set loading status
      setIsRefreshing(true);
      
      // Delete the document
      await documentService.deleteDocument(selectedDocument!.id);
      
      // Update document list by removing the deleted document
      setDocuments(documents.filter(doc => doc.id !== selectedDocument!.id));
      
      // Close the dialog
      setShowDeleteModal(false);
      
      // User notification
      alert(t('admin.documents.deleteSuccess'));
      
      // After deletion, reload all documents from server
      // to ensure view is synced with server
      try {
        const updatedDocs = await documentService.getAllDocuments();
        setDocuments(updatedDocs);
        console.log('Documents reloaded after deletion');
      } catch (refreshError) {
        console.error('Error refreshing documents after delete:', refreshError);
        // If refresh fails, at least the document was removed from view above
      }
    } catch (error) {
      console.error('Error deleting document:', error);
      alert(t('admin.documents.deleteError'));
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
      alert(t('admin.users.deleteSuccess'));
      
      // Refresh data after deletion
      await refreshData();
    } catch (error) {
      console.error('Error deleting user:', error);
      alert(t('admin.users.deleteError'));
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleLanguageChange = (newLanguage: Language) => {
    setLanguage(newLanguage);
    i18n.changeLanguage(newLanguage);
    document.documentElement.lang = newLanguage;
    document.documentElement.dir = newLanguage === 'he' ? 'rtl' : 'ltr';
  };

  const handleThemeChange = (newTheme: 'dark' | 'light') => {
    setTheme(newTheme);
  };

  const renderContent = () => {
    switch (activeItem) {
      case 'chatbot':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-green-600 dark:text-green-400 mb-4">{t('admin.sidebar.chatbotPreview')}</h2>
            <div className="bg-gray-100/30 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300/20 dark:border-green-500/20 p-4 h-[calc(100vh-200px)] overflow-hidden">
              <div className="h-full relative">
                <ChatWindow onLogout={onLogout} theme={theme} />
              </div>
            </div>
          </div>
        );
      case 'analytics':
        if (activeSubItem === 'users') {
          // Filter only regular users (not admins)
          const regularUsers = analytics.recentUsers.filter(user => {
            // Check if user is not in the admins list
            return !analytics.recentAdmins?.some(admin => admin.id === user.id);
          });
          
          return (
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {t('admin.sidebar.users')}
                </h2>
                <button
                  onClick={refreshData}
                  className="bg-green-500/20 hover:bg-green-500/30 text-green-400 font-medium py-2 px-4 rounded-lg border border-green-500/30 transition-colors"
                >
                  {t('Refresh')}
                </button>
              </div>
              <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 shadow-lg">
                <div className="border-b border-gray-300 dark:border-green-500/20 py-3 px-6">
                  <h3 className="text-lg font-semibold text-green-600 dark:text-green-400">
                    {t('analytics.users')} ({regularUsers.length})
                  </h3>
                </div>
                <div className="p-6 space-y-4">
                  {regularUsers && regularUsers.length > 0 ? (
                    regularUsers.map((user, index) => (
                      <div key={user.id || index} className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-gray-800 dark:text-green-400">{user.email || user.name || 'Unknown User'}</p>
                          <p className="text-sm text-gray-600 dark:text-green-400/50">
                            {user.created_at ? new Date(user.created_at).toLocaleDateString() : ''}
                          </p>
                        </div>
                        <div className="flex items-center">
                          <span className="text-sm text-gray-600 dark:text-green-400/70 mr-4">
                            user
                          </span>
                          <button
                            onClick={() => handleDeleteUser(user)}
                            className="p-1 text-red-500 dark:text-red-400 hover:text-red-600 dark:hover:text-red-300 hover:bg-red-100/20 dark:hover:bg-red-500/20 rounded-full transition-colors"
                            title={t('users.delete') || 'Delete user'}
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-600 dark:text-green-400/70">{t('analytics.noUsers')}</p>
                  )}
                </div>
              </div>
            </div>
          );
        }
        else if (activeSubItem === 'admins') {
          return (
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {t('admin.sidebar.administrators')}
                </h2>
                <button
                  onClick={refreshData}
                  className="bg-green-500/20 hover:bg-green-500/30 text-green-400 font-medium py-2 px-4 rounded-lg border border-green-500/30 transition-colors"
                >
                  {t('Refresh')}
                </button>
              </div>
              <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 shadow-lg">
                <div className="border-b border-gray-300 dark:border-green-500/20 py-3 px-6">
                  <h3 className="text-lg font-semibold text-green-600 dark:text-green-400">
                    {t('analytics.activeAdmins')} ({analytics.recentAdmins.length})
                  </h3>
                </div>
                <div className="p-6 space-y-4">
                  {analytics.recentAdmins && analytics.recentAdmins.length > 0 ? (
                    analytics.recentAdmins.map((admin, index) => (
                      <div key={admin.id || index} className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-gray-800 dark:text-green-400">{admin.email || admin.name || 'Unknown Admin'}</p>
                          <p className="text-sm text-gray-600 dark:text-green-400/50">
                            {admin.created_at ? new Date(admin.created_at).toLocaleDateString() : ''}
                          </p>
                        </div>
                        <span className="text-sm text-gray-600 dark:text-green-400/70">
                          admin {admin.department ? `(${admin.department})` : ''}
                        </span>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-600 dark:text-green-400/70">{t('analytics.noAdmins')}</p>
                  )}
                </div>
              </div>
            </div>
          );
        }
        else {
          // sub-category overview - show general data
          return (
            <div>
              <div className="flex justify-between items-center mb-6 px-6 pt-6">
                <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {t('analytics.overview')}
                </h2>
                <button
                  onClick={refreshData}
                  className="bg-green-500/20 hover:bg-green-500/30 text-green-400 font-medium py-2 px-4 rounded-lg border border-green-500/30 transition-colors"
                >
                  {t('Refresh')}
                </button>
              </div>
              <AnalyticsOverview analytics={analytics} isLoading={isRefreshing} />
            </div>
          );
        }
      case 'documents':
        return (
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-green-600 dark:text-green-400">
                {activeSubItem === 'upload' 
                  ? (i18n.language === 'he' ? 'העלאת מסמכים' : 'Upload Documents') 
                  : (i18n.language === 'he' ? 'מסמכים פעילים' : 'Active Documents')}
              </h2>
              {activeSubItem === 'active' && (
                <button
                  onClick={() => setShowUploadModal(true)}
                  className="bg-green-500/20 hover:bg-green-500/30 text-green-400 font-medium py-2 px-4 rounded-lg border border-green-500/30 transition-colors flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>{t('documents.add')}</span>
                </button>
              )}
            </div>
            
            {activeSubItem === 'upload' ? (
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
      case 'rag':
        return (
          <RAGManagement 
            activeSubItem={activeSubItem}
            language={language}
            onRefresh={refreshData}
          />
        );
      case 'settings':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-green-600 dark:text-green-400 mb-6">{t('admin.sidebar.settings')}</h2>
            <div className="bg-gray-100/30 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300/20 dark:border-green-500/20 p-6 space-y-8">
              
              {/* Theme Section */}
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-green-50 dark:bg-green-900/20 flex items-center justify-center">
                    {theme === 'dark' ? (
                      <Moon className="w-4 h-4 text-green-600 dark:text-green-400" />
                    ) : (
                      <Sun className="w-4 h-4 text-green-600 dark:text-green-400" />
                    )}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-green-400">
                    {i18n.language === 'he' ? 'ערכת נושא' : 'Theme'}
                  </h3>
                </div>

                <div className="relative">
                  <div className="flex p-1 bg-gray-200/50 dark:bg-black/50 rounded-xl border border-gray-300/30 dark:border-green-500/30">
                    <button
                      onClick={() => handleThemeChange('light')}
                      className={`flex-1 flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                        theme === 'light'
                          ? 'bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/30'
                          : 'text-gray-600 dark:text-green-400/70 hover:text-gray-800 dark:hover:text-green-400 hover:bg-gray-100/20 dark:hover:bg-green-500/10'
                      }`}
                    >
                      <Sun className="w-4 h-4 mr-2" />
                      {i18n.language === 'he' ? 'בהיר' : 'Light'}
                    </button>
                    <button
                      onClick={() => handleThemeChange('dark')}
                      className={`flex-1 flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                        theme === 'dark'
                          ? 'bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/30'
                          : 'text-gray-600 dark:text-green-400/70 hover:text-gray-800 dark:hover:text-green-400 hover:bg-gray-100/20 dark:hover:bg-green-500/10'
                      }`}
                    >
                      <Moon className="w-4 h-4 mr-2" />
                      {i18n.language === 'he' ? 'כהה' : 'Dark'}
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
                    {i18n.language === 'he' ? 'שפה' : 'Language'}
                  </h3>
                </div>

                <div className="relative">
                  <div className="flex p-1 bg-gray-200/50 dark:bg-black/50 rounded-xl border border-gray-300/30 dark:border-green-500/30">
                    <button
                      onClick={() => handleLanguageChange('he')}
                      className={`flex-1 flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                        language === 'he'
                          ? 'bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/30'
                          : 'text-gray-600 dark:text-green-400/70 hover:text-gray-800 dark:hover:text-green-400 hover:bg-gray-100/20 dark:hover:bg-green-500/10'
                      }`}
                    >
                      עברית
                    </button>
                    <button
                      onClick={() => handleLanguageChange('en')}
                      className={`flex-1 flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                        language === 'en'
                          ? 'bg-green-500/20 text-green-600 dark:text-green-400 border border-green-500/30'
                          : 'text-gray-600 dark:text-green-400/70 hover:text-gray-800 dark:hover:text-green-400 hover:bg-gray-100/20 dark:hover:bg-green-500/10'
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
        message={t('admin.loading') || 'Loading Dashboard'}
        subMessage={t('admin.loadingPermissions') || 'Initializing admin permissions...'}
      />
    );
  }

  return (
    <div className="flex h-screen bg-white dark:bg-black text-gray-900 dark:text-white transition-colors duration-300">
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
        document={selectedDocument}
        onUpdate={handleUpdateDocument}
      />

      {/* Delete user modal */}
      {showDeleteUserModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-black border border-green-500/30 rounded-lg p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-green-400">{t('users.confirmDelete') || 'Confirm User Deletion'}</h3>
              <button
                onClick={() => setShowDeleteUserModal(false)}
                className="text-green-400 hover:text-green-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="flex items-center mb-4 text-amber-400 bg-amber-500/10 p-3 rounded-lg">
              <AlertTriangle className="w-5 h-5 mr-2" />
              <p className="text-sm">
                {t('users.deleteWarning') || 'This action cannot be undone. The user will be permanently deleted.'}
              </p>
            </div>
            <p className="text-green-400/80 mb-6">
              {t('users.deleteConfirmText') || 'Are you sure you want to delete the user:'} <span className="font-semibold">{selectedUser?.email || selectedUser?.name || 'Unknown User'}</span>?
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteUserModal(false)}
                className="px-4 py-2 border border-green-500/30 rounded-lg text-green-400 hover:bg-green-500/20"
              >
                {t('Cancel')}
              </button>
              <button
                onClick={handleDeleteUserConfirm}
                className="px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400 hover:bg-red-500/30"
              >
                {t('Delete')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard; 