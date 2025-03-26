import React from 'react';
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
  LogOut
} from 'lucide-react';
import { translations } from './translations';

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

interface SidebarProps {
  isSidebarCollapsed: boolean;
  setIsSidebarCollapsed: (value: boolean) => void;
  activeItem: string;
  setActiveItem: (value: string) => void;
  activeSubItem: string | null;
  setActiveSubItem: (value: string | null) => void;
  language: Language;
  onLogout: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isSidebarCollapsed,
  setIsSidebarCollapsed,
  activeItem,
  setActiveItem,
  activeSubItem,
  setActiveSubItem,
  language,
  onLogout
}) => {
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

  const handleItemClick = (itemId: string) => {
    setActiveItem(itemId);
    setActiveSubItem(null);
  };

  const handleSubItemClick = (itemId: string, subItemId: string) => {
    setActiveItem(itemId);
    setActiveSubItem(subItemId);
  };

  return (
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
          onClick={onLogout}
          className="w-full flex items-center gap-3 px-4 py-2 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
        >
          <LogOut className="w-5 h-5" />
          {!isSidebarCollapsed && <span>{t('nav.logout')}</span>}
        </button>
      </div>
    </div>
  );
}; 