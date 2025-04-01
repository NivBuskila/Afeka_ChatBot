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
  X
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
import { DeleteModal } from './DeleteModal';
import { documentService } from '../../services/documentService';
import { userService } from '../../services/userService';
import { analyticsService, DashboardAnalytics } from '../../services/analyticsService';
import type { Document } from '../../config/supabase';
import { supabase } from '../../config/supabase';

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
  role: 'admin' | 'user' | 'standard' | 'administrator';
  lastLogin: string;
  status: 'active' | 'inactive';
}

interface AdminDashboardProps {
  onLogout: () => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ onLogout }) => {
  const { t, i18n } = useTranslation();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [activeItem, setActiveItem] = useState('dashboard');
  const [activeSubItem, setActiveSubItem] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<string>('all');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [analytics, setAnalytics] = useState<DashboardAnalytics>({
    totalDocuments: 0,
    totalUsers: 0,
    recentDocuments: [],
    recentUsers: []
  });
  const [loading, setLoading] = useState(true);
  const [language, setLanguage] = useState<Language>(i18n.language as Language);
  const navigate = useNavigate();

  useEffect(() => {
    document.documentElement.lang = language;
    document.documentElement.dir = language === 'he' ? 'rtl' : 'ltr';
    i18n.changeLanguage(language);
  }, [language, i18n]);

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
      id: 'settings',
      title: t('admin.sidebar.settings'),
      icon: <Settings className="w-5 h-5" />
    }
  ];

  const mockUsers: User[] = [
    { id: 1, name: 'ישראל ישראלי', email: 'israel@afeka.ac.il', role: 'admin', lastLogin: '2024-03-25 10:30', status: 'active' },
    { id: 2, name: 'שרה כהן', email: 'sara@afeka.ac.il', role: 'user', lastLogin: '2024-03-25 09:15', status: 'active' },
    { id: 3, name: 'דוד לוי', email: 'david@afeka.ac.il', role: 'user', lastLogin: '2024-03-24 15:45', status: 'inactive' },
  ];

  const mockDocuments: any[] = [
    { id: 1, name: i18n.language === 'he' ? 'תקנון אקדמי' : 'Academic Regulations', type: 'pdf', size: 2.5 * 1024 * 1024, url: '#', created_at: '2024-03-20' },
    { id: 2, name: i18n.language === 'he' ? 'מדריך למשתמש' : 'User Guide', type: 'pdf', size: 1.8 * 1024 * 1024, url: '#', created_at: '2024-03-18' },
    { id: 3, name: i18n.language === 'he' ? 'לוח זמנים' : 'Schedule', type: 'pdf', size: 3.2 * 1024 * 1024, url: '#', created_at: '2024-03-15' },
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [docs, analyticsData] = await Promise.all([
          documentService.getAllDocuments(),
          analyticsService.getDashboardAnalytics()
        ]);
        setDocuments(docs);
        setAnalytics(analyticsData);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleItemClick = (itemId: string) => {
    setActiveItem(itemId);
    setActiveSubItem(null);
  };

  const handleSubItemClick = (itemId: string, subItemId: string) => {
    setActiveItem(itemId);
    setActiveSubItem(subItemId);
  };

  const handleLogout = () => {
    onLogout();
  };

  const handleEditDocument = (document: Document) => {
    setSelectedDocument(document);
    // Add edit logic here
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
      // בדיקה שהמשתמש מחובר לפני העלאת הקובץ
      const { data: authData } = await supabase.auth.getSession();
      if (!authData.session) {
        console.error('User not authenticated');
        alert('יש להתחבר מחדש למערכת');
        return;
      }
      
      // הדפסת מידע לצורך דיבאג
      console.log('User ID:', authData.session.user.id);
      console.log('User email:', authData.session.user.email);
      
      // בודקים אם המשתמש קיים בטבלת משתמשים
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select('id, role')
        .eq('id', authData.session.user.id)
        .single();
      
      // אם המשתמש לא קיים, ננסה ליצור אותו (למרות שזה עלול להיכשל בגלל RLS)
      if (userError || !userData) {
        console.error('User not found in database:', userError);
        
        // ננסה ליצור רשומת משתמש חדשה
        try {
          const { error: insertError } = await supabase
            .from('users')
            .insert({
              id: authData.session.user.id,
              email: authData.session.user.email || '',
              role: authData.session.user.user_metadata?.role || 'user'
            });
            
          if (insertError) {
            console.error('Failed to insert user record:', insertError);
            // ממשיכים למרות השגיאה, כי אנחנו כבר מנסים לעקוף את המגבלות
          } else {
            console.log('Created new user record for', authData.session.user.email);
          }
        } catch (createError) {
          console.error('Error creating user record:', createError);
          // ממשיכים למרות השגיאה
        }
      } else {
        console.log('Found existing user:', userData);
      }
      
      // יצירת שם קובץ בטוח ללא תווים בעברית
      const fileExt = file.name.split('.').pop() || '';
      const safeFileName = `${Date.now()}.${fileExt}`;
      const path = `documents/${safeFileName}`;
      
      console.log('Uploading file to path:', path);
      
      try {
        // העלאת הקובץ - גישה ישירה ללא RPC
        const { data: uploadData, error: uploadError } = await supabase.storage
          .from('documents')
          .upload(path, file);
        
        if (uploadError) {
          console.error('Error uploading file:', uploadError);
          alert(`שגיאה בהעלאת הקובץ: ${uploadError.message}`);
          return;
        }
        
        console.log('Upload successful:', uploadData);
        
        // קבלת הURL הציבורי
        const { data: urlData } = supabase.storage
          .from('documents')
          .getPublicUrl(path);
        
        console.log('File URL:', urlData.publicUrl);
        
        try {
          // יצירת רשומת מסמך ישירות (לא דרך RPC)
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
          
          // ניסיון להוסיף רשומת אנליטיקס (עלול להיכשל בגלל RLS)
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
              // ממשיכים למרות השגיאה
            }
          } catch (analyticsError) {
            console.error('Failed to add analytics record:', analyticsError);
            // ממשיכים למרות השגיאה
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

  const handleDelete = async () => {
    if (!selectedDocument) return;

    try {
      await documentService.deleteDocument(selectedDocument.id);
      setDocuments(prev => prev.filter(doc => doc.id !== selectedDocument.id));
      setShowDeleteModal(false);
      setSelectedDocument(null);
    } catch (error) {
      console.error('Error deleting document:', error);
    }
  };

  const handleLanguageChange = (newLanguage: Language) => {
    setLanguage(newLanguage);
    i18n.changeLanguage(newLanguage);
    document.documentElement.lang = newLanguage;
    document.documentElement.dir = newLanguage === 'he' ? 'rtl' : 'ltr';
  };

  const renderContent = () => {
    switch (activeItem) {
      case 'chatbot':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-green-400 mb-4">{t('admin.sidebar.chatbotPreview')}</h2>
            <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-4 h-[calc(100vh-200px)]">
              <ChatWindow onLogout={onLogout} />
            </div>
          </div>
        );
      case 'analytics':
        // הוספת הדפסת מידע לדיבאג על ה-activeSubItem
        console.log('Active Sub Item:', activeSubItem);
        console.log('Analytics Users:', analytics.recentUsers);
        
        if (activeSubItem === 'users') {
          // רק משתמשים רגילים
          const filteredUsers = analytics.recentUsers.filter(user => 
            user.role === 'user' || user.role === 'standard' || user.role?.toLowerCase() === 'user');
          
          console.log('Filtered Users:', filteredUsers);
          
          return (
            <div className="p-6">
              <h2 className="text-2xl font-bold text-green-400 mb-6">
                {t('admin.sidebar.users')} 
              </h2>
              <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20">
                <div className="border-b border-green-500/20 py-3 px-6">
                  <h3 className="text-lg font-semibold text-green-400">{t('analytics.users')}</h3>
                </div>
                <div className="p-6 space-y-4">
                  {filteredUsers.length > 0 ? (
                    filteredUsers.map((user) => (
                      <div key={user.id} className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-green-400">{user.email}</p>
                          <p className="text-sm text-green-400/50">
                            {new Date(user.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <span className="text-sm text-green-400/70">
                          {user.role || 'user'}
                        </span>
                      </div>
                    ))
                  ) : (
                    <p className="text-green-400/70">{t('analytics.noUsers')}</p>
                  )}
                </div>
              </div>
            </div>
          );
        } else if (activeSubItem === 'admins') {
          // רק מנהלים
          const filteredAdmins = analytics.recentUsers.filter(user => 
            user.role === 'admin' || user.role === 'administrator' || user.role?.toLowerCase() === 'admin');
          
          console.log('Filtered Admins:', filteredAdmins);
          
          return (
            <div className="p-6">
              <h2 className="text-2xl font-bold text-green-400 mb-6">
                {t('admin.sidebar.administrators')}
              </h2>
              <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20">
                <div className="border-b border-green-500/20 py-3 px-6">
                  <h3 className="text-lg font-semibold text-green-400">{t('admin.sidebar.administrators')}</h3>
                </div>
                <div className="p-6 space-y-4">
                  {filteredAdmins.length > 0 ? (
                    filteredAdmins.map((user) => (
                      <div key={user.id} className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-green-400">{user.email}</p>
                          <p className="text-sm text-green-400/50">
                            {new Date(user.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <span className="text-sm text-green-400/70">
                          {user.role || 'admin'}
                        </span>
                      </div>
                    ))
                  ) : (
                    <p className="text-green-400/70">{t('analytics.noAdmins')}</p>
                  )}
                </div>
              </div>
            </div>
          );
        } else {
          // תצוגת Overview
          return (
            <div>
              <h3 className="text-lg font-semibold text-green-400 mb-4">Active Tab: {activeSubItem || 'overview'}</h3>
              <AnalyticsOverview analytics={analytics} />
            </div>
          );
        }
      case 'documents':
        return (
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-green-400">
                {activeSubItem === 'upload' ? t('admin.sidebar.uploadDocuments') : t('documents.activeDocuments')}
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
      case 'settings':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-green-400 mb-6">{t('admin.sidebar.settings')}</h2>
            <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-6">
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-green-400 mb-2">{t('settings.language')}</h3>
                <div className="flex gap-4">
                  <button
                    onClick={() => handleLanguageChange('he')}
                    className={`px-4 py-2 rounded-lg border transition-colors ${
                      language === 'he'
                        ? 'bg-green-500/20 border-green-500/30 text-green-400'
                        : 'bg-black/50 border-green-500/30 text-green-400/70 hover:bg-green-500/10'
                    }`}
                  >
                    {t('settings.language.he')}
                  </button>
                  <button
                    onClick={() => handleLanguageChange('en')}
                    className={`px-4 py-2 rounded-lg border transition-colors ${
                      language === 'en'
                        ? 'bg-green-500/20 border-green-500/30 text-green-400'
                        : 'bg-black/50 border-green-500/30 text-green-400/70 hover:bg-green-500/10'
                    }`}
                  >
                    {t('settings.language.en')}
                  </button>
                </div>
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  if (loading) {
    return <div>{t('loading')}</div>;
  }

  return (
    <div className="flex h-screen bg-black text-white">
      <Sidebar
        isSidebarCollapsed={isSidebarCollapsed}
        setIsSidebarCollapsed={setIsSidebarCollapsed}
        activeItem={activeItem}
        setActiveItem={setActiveItem}
        activeSubItem={activeSubItem}
        setActiveSubItem={setActiveSubItem}
        language={language}
        onLogout={onLogout}
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar language={language} />
        
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-black p-6">
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
    </div>
  );
};

export default AdminDashboard; 