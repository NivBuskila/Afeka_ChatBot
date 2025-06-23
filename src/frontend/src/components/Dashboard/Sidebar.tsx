import React from "react";
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
  Brain,
  Cpu,
  TrendingUp,
  Search,
  Coins,
  MessageCircle,
} from "lucide-react";
import { translations } from "./translations";

type Language = "he" | "en";

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
  onItemClick: (itemId: string) => void;
  onSubItemClick: (itemId: string, subItemId: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isSidebarCollapsed,
  setIsSidebarCollapsed,
  activeItem,
  activeSubItem,
  language,
  onLogout,
  onItemClick,
  onSubItemClick,
}) => {
  const t = (key: string) => translations[key]?.[language] || key;

  const menuItems: MenuItem[] = [
    {
      id: "chatbot",
      title: t("chatbot.preview"),
      icon: <MessageSquare className="w-5 h-5" />,
    },
    {
      id: "analytics",
      title: t("analytics"),
      icon: <BarChart3 className="w-5 h-5" />,
      subItems: [
        {
          id: "overview",
          title: t("analytics.overview"),
          icon: <BarChart3 className="w-4 h-4" />,
        },
        {
          id: "token-usage",
          title: t("analytics.token.usage"),
          icon: <Coins className="w-4 h-4" />,
        },
        {
          id: "users",
          title: t("analytics.users"),
          icon: <Users className="w-4 h-4" />,
        },
        {
          id: "admins",
          title: t("analytics.admins"),
          icon: <UserCog className="w-4 h-4" />,
        },
      ],
    },
    {
      id: "documents",
      title: t("documents"),
      icon: <FileText className="w-5 h-5" />,
      subItems: [
        {
          id: "upload",
          title: t("documents.upload"),
          icon: <Upload className="w-4 h-4" />,
        },
        {
          id: "active",
          title: t("documents.active"),
          icon: <FileText className="w-4 h-4" />,
        },
      ],
    },
    {
      id: "rag",
      title: t("rag.management"),
      icon: <Brain className="w-5 h-5" />,
      subItems: [
        {
          id: "overview",
          title: t("rag.overview"),
          icon: <Brain className="w-4 h-4" />,
        },
        {
          id: "profiles",
          title: t("rag.profiles"),
          icon: <Cpu className="w-4 h-4" />,
        },
        {
          id: "performance",
          title: t("rag.performance"),
          icon: <TrendingUp className="w-4 h-4" />,
        },
        {
          id: "test",
          title: t("rag.test"),
          icon: <Search className="w-4 h-4" />,
        },
        {
          id: "system-prompt",
          title: t("rag.system.prompt"),
          icon: <MessageCircle className="w-4 h-4" />,
        },
      ],
    },
    {
      id: "settings",
      title: t("settings"),
      icon: <Settings className="w-5 h-5" />,
    },
  ];

  const handleItemClick = (itemId: string) => {
    onItemClick(itemId);
  };

  const handleSubItemClick = (itemId: string, subItemId: string) => {
    onSubItemClick(itemId, subItemId);
  };

  return (
    <div
      className={`bg-gray-100/50 dark:bg-black/50 backdrop-blur-lg border-r border-gray-300/20 dark:border-green-500/20 transition-all duration-300 ${
        isSidebarCollapsed ? "w-16" : "w-64"
      } flex flex-col h-full`}
    >
      <div className="p-4 flex items-center justify-between flex-shrink-0">
        {!isSidebarCollapsed && (
          <div className="flex items-center space-x-2">
            <LayoutDashboard className="w-6 h-6 text-green-600 dark:text-green-400" />
            <span className="text-xl font-bold text-green-600 dark:text-green-400">
              {t("nav.apex.admin")}
            </span>
          </div>
        )}
        <button
          onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          className="p-2 hover:bg-gray-200/20 dark:hover:bg-green-500/10 rounded-lg transition-colors"
        >
          {isSidebarCollapsed ? (
            <ChevronRight className="w-5 h-5 text-green-600 dark:text-green-400" />
          ) : (
            <ChevronLeft className="w-5 h-5 text-green-600 dark:text-green-400" />
          )}
        </button>
      </div>

      <div className="mt-8 flex-1 overflow-y-auto">
        {menuItems.map((item) => (
          <div key={item.id}>
            <button
              onClick={() => handleItemClick(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-2 transition-colors ${
                activeItem === item.id
                  ? "bg-green-500/20 text-green-600 dark:text-green-400"
                  : "text-gray-600 dark:text-green-400/70 hover:bg-gray-200/20 dark:hover:bg-green-500/10"
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
                        ? "bg-green-500/20 text-green-600 dark:text-green-400"
                        : "text-gray-600 dark:text-green-400/70 hover:bg-gray-200/20 dark:hover:bg-green-500/10"
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

      <div className="p-4 border-t border-gray-300/20 dark:border-green-500/20 flex-shrink-0">
        <button
          onClick={onLogout}
          className="w-full flex items-center gap-3 px-4 py-2 text-red-500 dark:text-red-400 hover:bg-red-100/20 dark:hover:bg-red-500/10 rounded-lg transition-colors"
        >
          <LogOut className="w-5 h-5" />
          {!isSidebarCollapsed && <span>{t("nav.logout")}</span>}
        </button>
      </div>
    </div>
  );
};
