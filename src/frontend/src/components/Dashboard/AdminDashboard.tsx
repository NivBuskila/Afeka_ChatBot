import React, { useState } from 'react';
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
  role: 'admin' | 'user';
  lastLogin: string;
  status: 'active' | 'inactive';
}

interface Document {
  id: number;
  title: string;
  category: string;
  uploadDate: string;
  size: string;
  status: 'active' | 'archived';
}

interface AdminDashboardProps {
  onLogout: () => void;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ onLogout }) => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [activeItem, setActiveItem] = useState<string>('chatbot');
  const [activeSubItem, setActiveSubItem] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<string>('all');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [selectedItem, setSelectedItem] = useState<number | null>(null);
  const [language, setLanguage] = useState<Language>('he');
  const navigate = useNavigate();

  const t = (key: string) => translations[key]?.[language] || key;

  const menuItems: MenuItem[] = [
    {
      id: 'chatbot',
      title: t('chatbot.preview'),
      icon: <MessageSquare className="w-5 h-5" />
    },
    {
      id: 'analytics',
      title: t('analytics'),
      icon: <BarChart3 className="w-5 h-5" />,
      subItems: [
        { id: 'overview', title: t('analytics.overview'), icon: <BarChart3 className="w-4 h-4" /> },
        { id: 'users', title: t('analytics.users'), icon: <Users className="w-4 h-4" /> },
        { id: 'admins', title: t('analytics.admins'), icon: <UserCog className="w-4 h-4" /> }
      ]
    },
    {
      id: 'documents',
      title: t('documents'),
      icon: <FileText className="w-5 h-5" />,
      subItems: [
        { id: 'upload', title: t('documents.upload'), icon: <Upload className="w-4 h-4" /> },
        { id: 'active', title: t('documents.active'), icon: <FileText className="w-4 h-4" /> }
      ]
    },
    {
      id: 'settings',
      title: t('settings'),
      icon: <Settings className="w-5 h-5" />
    }
  ];

  const mockUsers: User[] = [
    { id: 1, name: 'ישראל ישראלי', email: 'israel@afeka.ac.il', role: 'admin', lastLogin: '2024-03-25 10:30', status: 'active' },
    { id: 2, name: 'שרה כהן', email: 'sara@afeka.ac.il', role: 'user', lastLogin: '2024-03-25 09:15', status: 'active' },
    { id: 3, name: 'דוד לוי', email: 'david@afeka.ac.il', role: 'user', lastLogin: '2024-03-24 15:45', status: 'inactive' },
  ];

  const mockDocuments: Document[] = [
    { id: 1, title: t('category.regulations'), category: t('category.regulations'), uploadDate: '2024-03-20', size: '2.5 MB', status: 'active' },
    { id: 2, title: t('category.guides'), category: t('category.guides'), uploadDate: '2024-03-18', size: '1.8 MB', status: 'active' },
    { id: 3, title: t('category.schedules'), category: t('category.schedules'), uploadDate: '2024-03-15', size: '3.2 MB', status: 'archived' },
  ];

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

  const renderContent = () => {
    switch (activeItem) {
      case 'chatbot':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-green-400 mb-4">{t('chatbot.preview')}</h2>
            <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-4 h-[calc(100vh-200px)]">
              <ChatWindow onLogout={onLogout} />
            </div>
          </div>
        );
      case 'analytics':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-green-400 mb-4">
              {activeSubItem ? t(`analytics.${activeSubItem}`) : t('analytics.overview')}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-4">
                <h3 className="text-green-400/80 mb-2">{t('analytics.active.users')}</h3>
                <p className="text-2xl font-bold text-green-400">1,234</p>
                <p className="text-sm text-green-400/60">+12% {t('analytics.week.change')}</p>
              </div>
              <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-4">
                <h3 className="text-green-400/80 mb-2">{t('analytics.daily.conversations')}</h3>
                <p className="text-2xl font-bold text-green-400">456</p>
                <p className="text-sm text-green-400/60">+8% {t('analytics.week.change')}</p>
              </div>
              <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-4">
                <h3 className="text-green-400/80 mb-2">{t('analytics.active.documents')}</h3>
                <p className="text-2xl font-bold text-green-400">89</p>
                <p className="text-sm text-green-400/60">+5% {t('analytics.week.change')}</p>
              </div>
              <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-4">
                <h3 className="text-green-400/80 mb-2">{t('analytics.avg.response')}</h3>
                <p className="text-2xl font-bold text-green-400">1.2s</p>
                <p className="text-sm text-green-400/60">-15% {t('analytics.week.change')}</p>
              </div>
            </div>
            <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-4">
              <div className="flex items-center justify-center h-[400px] text-green-400/50">
                {t('analytics.overview')}
              </div>
            </div>
          </div>
        );
      case 'documents':
        return (
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-green-400">
                {activeSubItem === 'upload' ? t('documents.upload') : t('documents.active')}
              </h2>
              {activeSubItem === 'active' && (
                <button
                  onClick={() => setShowUploadModal(true)}
                  className="flex items-center gap-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 px-4 py-2 rounded-lg border border-green-500/30 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  <span>{t('documents.add')}</span>
                </button>
              )}
            </div>
            
            {activeSubItem === 'upload' ? (
              <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-8">
                <div className="flex flex-col items-center justify-center h-[400px] border-2 border-dashed border-green-500/30 rounded-lg">
                  <Upload className="w-12 h-12 text-green-400/50 mb-4" />
                  <p className="text-green-400/70 mb-4">{t('documents.drag.drop')}</p>
                  <button className="bg-green-500/20 hover:bg-green-500/30 text-green-400 px-6 py-2 rounded-lg border border-green-500/30 transition-colors">
                    {t('documents.select.files')}
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20">
                <div className="p-4 border-b border-green-500/10">
                  <div className="flex items-center gap-4">
                    <div className="relative flex-1">
                      <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-green-400/50" />
                      <input
                        type="text"
                        placeholder={t('documents.search')}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full bg-black/50 border border-green-500/30 rounded-lg px-4 py-2 pl-10 text-white focus:outline-none focus:ring-1 focus:ring-green-500/50"
                      />
                    </div>
                    <select
                      value={selectedFilter}
                      onChange={(e) => setSelectedFilter(e.target.value)}
                      className="bg-black/50 border border-green-500/30 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-1 focus:ring-green-500/50"
                    >
                      <option value="all">{t('documents.all.categories')}</option>
                      <option value="active">{t('documents.status.active')}</option>
                      <option value="archived">{t('documents.status.archived')}</option>
                    </select>
                  </div>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-green-500/10">
                        <th className="text-center py-3 px-4 text-green-400/70">{t('table.document.name')}</th>
                        <th className="text-center py-3 px-4 text-green-400/70">{t('table.category')}</th>
                        <th className="text-center py-3 px-4 text-green-400/70">{t('table.upload.date')}</th>
                        <th className="text-center py-3 px-4 text-green-400/70">{t('table.size')}</th>
                        <th className="text-center py-3 px-4 text-green-400/70">{t('table.status')}</th>
                        <th className="text-center py-3 px-4 text-green-400/70">{t('table.actions')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mockDocuments.map((doc) => (
                        <tr key={doc.id} className="border-b border-green-500/10">
                          <td className="text-center py-3 px-4">{doc.title}</td>
                          <td className="text-center py-3 px-4">{doc.category}</td>
                          <td className="text-center py-3 px-4">{doc.uploadDate}</td>
                          <td className="text-center py-3 px-4">{doc.size}</td>
                          <td className="text-center py-3 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              doc.status === 'active' 
                                ? 'bg-green-500/20 text-green-400' 
                                : 'bg-gray-500/20 text-gray-400'
                            }`}>
                              {doc.status === 'active' ? t('documents.status.active') : t('documents.status.archived')}
                            </span>
                          </td>
                          <td className="text-center py-3 px-4">
                            <div className="flex items-center justify-center gap-2">
                              <button className="p-1 hover:bg-green-500/10 rounded">
                                <Edit className="w-4 h-4 text-green-400" />
                              </button>
                              <button className="p-1 hover:bg-green-500/10 rounded">
                                <Trash2 className="w-4 h-4 text-green-400" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        );
      case 'settings':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-green-400 mb-6">{t('settings')}</h2>
            <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-6">
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-green-400 mb-2">{t('settings.language')}</h3>
                <div className="flex gap-4">
                  <button
                    onClick={() => setLanguage('he')}
                    className={`px-4 py-2 rounded-lg border transition-colors ${
                      language === 'he'
                        ? 'bg-green-500/20 border-green-500/30 text-green-400'
                        : 'bg-black/50 border-green-500/30 text-green-400/70 hover:bg-green-500/10'
                    }`}
                  >
                    {t('settings.language.he')}
                  </button>
                  <button
                    onClick={() => setLanguage('en')}
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

  return (
    <div className="flex h-screen bg-black text-white">
      {/* Sidebar */}
      <div className={`bg-black/50 backdrop-blur-lg border-r border-green-500/20 transition-all duration-300 ${isSidebarCollapsed ? 'w-16' : 'w-64'}`}>
        <div className="p-4 flex items-center justify-between">
          {!isSidebarCollapsed && (
            <div className="flex items-center space-x-2">
              <LayoutDashboard className="w-6 h-6 text-green-400" />
              <span className="text-xl font-bold text-green-400">{t('nav.apex.admin')}</span>
            </div>
          )}
          <button
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            className="p-2 hover:bg-green-500/10 rounded-lg transition-colors"
          >
            {isSidebarCollapsed ? (
              <ChevronRight className="w-5 h-5 text-green-400" />
            ) : (
              <ChevronLeft className="w-5 h-5 text-green-400" />
            )}
          </button>
        </div>

        <div className="mt-8">
          {menuItems.map((item) => (
            <div key={item.id}>
              <button
                onClick={() => handleItemClick(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-2 transition-colors ${
                  activeItem === item.id
                    ? 'bg-green-500/20 text-green-400'
                    : 'text-green-400/70 hover:bg-green-500/10'
                }`}
              >
                {item.icon}
                {!isSidebarCollapsed && <span>{item.title}</span>}
              </button>
              {!isSidebarCollapsed && item.subItems && activeItem === item.id && (
                <div className="pl-12 mt-2 space-y-1">
                  {item.subItems.map((subItem) => (
                    <button
                      key={subItem.id}
                      onClick={() => handleSubItemClick(item.id, subItem.id)}
                      className={`w-full flex items-center gap-3 px-4 py-2 text-sm transition-colors ${
                        activeSubItem === subItem.id
                          ? 'bg-green-500/20 text-green-400'
                          : 'text-green-400/70 hover:bg-green-500/10'
                      }`}
                    >
                      {subItem.icon}
                      <span>{subItem.title}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="absolute bottom-0 left-0 right-0 p-4">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-2 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
          >
            <LogOut className="w-5 h-5" />
            {!isSidebarCollapsed && <span>{t('nav.logout')}</span>}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {/* Top Bar */}
        <div className="h-16 bg-black/50 backdrop-blur-lg border-b border-green-500/20 flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-green-500/10 rounded-lg transition-colors">
              <Bell className="w-5 h-5 text-green-400/70" />
            </button>
            <div className="relative">
              <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-green-400/50" />
              <input
                type="text"
                placeholder={t('header.search')}
                className="bg-black/50 border border-green-500/30 rounded-lg px-4 py-2 pl-10 text-white focus:outline-none focus:ring-1 focus:ring-green-500/50"
              />
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center">
                <UserCog className="w-4 h-4 text-green-400" />
              </div>
              <div className="text-right">
                <div className="text-sm font-medium text-green-400">{t('header.system.admin')}</div>
                <div className="text-xs text-green-400/50">admin@afeka.ac.il</div>
              </div>
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div className="h-[calc(100vh-4rem)] overflow-y-auto">
          {renderContent()}
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-black/90 border border-green-500/20 rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-green-400">{t('modal.upload.title')}</h3>
              <button
                onClick={() => setShowUploadModal(false)}
                className="p-1 hover:bg-green-500/10 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-green-400/70" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-green-400/70 mb-2">{t('modal.upload.document.name')}</label>
                <input
                  type="text"
                  className="w-full bg-black/50 border border-green-500/30 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-1 focus:ring-green-500/50"
                />
              </div>
              <div>
                <label className="block text-green-400/70 mb-2">{t('modal.upload.category')}</label>
                <select className="w-full bg-black/50 border border-green-500/30 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-1 focus:ring-green-500/50">
                  <option value="תקנונים">{t('category.regulations')}</option>
                  <option value="מדריכים">{t('category.guides')}</option>
                  <option value="לוחות זמנים">{t('category.schedules')}</option>
                </select>
              </div>
              <div>
                <label className="block text-green-400/70 mb-2">{t('modal.upload.file')}</label>
                <div className="border-2 border-dashed border-green-500/30 rounded-lg p-4 text-center">
                  <Upload className="w-8 h-8 text-green-400/50 mx-auto mb-2" />
                  <p className="text-green-400/70 mb-2">{t('modal.upload.drag.file')}</p>
                  <button className="bg-green-500/20 hover:bg-green-500/30 text-green-400 px-4 py-2 rounded-lg border border-green-500/30 transition-colors">
                    {t('modal.upload.select.file')}
                  </button>
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-4 mt-6">
              <button
                onClick={() => setShowUploadModal(false)}
                className="px-4 py-2 text-green-400/70 hover:text-green-400 transition-colors"
              >
                {t('modal.upload.cancel')}
              </button>
              <button className="px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg border border-green-500/30 transition-colors">
                {t('modal.upload.submit')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-black/90 border border-green-500/20 rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-green-400">{t('modal.delete.title')}</h3>
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="p-1 hover:bg-green-500/10 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-green-400/70" />
              </button>
            </div>
            <p className="text-green-400/70 mb-6">
              {t('modal.delete.message')}
            </p>
            <div className="flex justify-end gap-4">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 text-green-400/70 hover:text-green-400 transition-colors"
              >
                {t('modal.delete.cancel')}
              </button>
              <button className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg border border-red-500/30 transition-colors">
                {t('modal.delete.confirm')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard; 