import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AlertCircle, Search, Trash2, Edit, Plus } from 'lucide-react';
import { ChatSession } from '../../services/chatService';

interface ChatHistoryProps {
  sessions: ChatSession[];
  onSelectSession: (session: ChatSession) => void;
  onCreateNewSession: () => void;
  onDeleteSession: (sessionId: string) => void;
  onEditSessionTitle: (sessionId: string, title: string) => void;
  activeSessionId?: string;
  isLoading: boolean;
}

const ChatHistory: React.FC<ChatHistoryProps> = ({
  sessions,
  onSelectSession,
  onCreateNewSession,
  onDeleteSession,
  onEditSessionTitle,
  activeSessionId,
  isLoading
}) => {
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState('');
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  // Filter sessions based on search term
  const filteredSessions = sessions.filter((session) =>
    session.title?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Format date to a more readable format
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('he-IL', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  // Start editing a session title
  const startEditing = (session: ChatSession) => {
    setEditingSessionId(session.id);
    setEditTitle(session.title || '');
  };

  // Save edited title
  const saveTitle = (sessionId: string) => {
    if (editTitle.trim()) {
      onEditSessionTitle(sessionId, editTitle.trim());
    }
    setEditingSessionId(null);
  };

  // Handle key down events for editing
  const handleKeyDown = (e: React.KeyboardEvent, sessionId: string) => {
    if (e.key === 'Enter') {
      saveTitle(sessionId);
    } else if (e.key === 'Escape') {
      setEditingSessionId(null);
    }
  };

  // Confirm delete dialog
  const confirmDelete = (sessionId: string) => {
    setConfirmDeleteId(sessionId);
  };

  // Execute delete and close dialog
  const executeDelete = (sessionId: string) => {
    onDeleteSession(sessionId);
    setConfirmDeleteId(null);
  };

  // Cancel delete
  const cancelDelete = () => {
    setConfirmDeleteId(null);
  };

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-800">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-2">
          {t('chat.history.title')}
        </h2>

        {/* Search and new chat button */}
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              placeholder={t('chat.history.search')}
              className="w-full px-3 py-2 pr-8 text-sm rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Search className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>
          <button
            onClick={onCreateNewSession}
            className="p-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
            title={t('chat.history.newChat')}
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Sessions list */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-700 dark:border-green-500"></div>
          </div>
        ) : filteredSessions.length > 0 ? (
          <ul className="divide-y divide-gray-200 dark:divide-gray-800">
            {filteredSessions.map((session) => (
              <li
                key={session.id}
                className={`relative hover:bg-gray-100 dark:hover:bg-gray-800 ${
                  activeSessionId === session.id ? 'bg-gray-100 dark:bg-gray-800' : ''
                }`}
              >
                <button
                  onClick={() => onSelectSession(session)}
                  className="w-full text-left p-4 focus:outline-none"
                >
                  <div className="flex justify-between items-start">
                    {editingSessionId === session.id ? (
                      <input
                        type="text"
                        className="flex-1 px-2 py-1 text-sm rounded border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onBlur={() => saveTitle(session.id)}
                        onKeyDown={(e) => handleKeyDown(e, session.id)}
                        autoFocus
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      <h3 className="font-medium text-gray-900 dark:text-white truncate max-w-[70%]">
                        {session.title || t('chat.history.untitled')}
                      </h3>
                    )}
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {formatDate(session.updated_at || session.created_at)}
                    </span>
                  </div>
                </button>
                
                {/* Action buttons */}
                <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex space-x-1">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      startEditing(session);
                    }}
                    className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 focus:outline-none"
                    title={t('chat.history.edit')}
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      confirmDelete(session.id);
                    }}
                    className="p-1 text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400 focus:outline-none"
                    title={t('chat.history.delete')}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <div className="flex flex-col items-center justify-center h-full p-4 text-center">
            <AlertCircle className="w-8 h-8 mb-2 text-gray-400" />
            <p className="text-gray-600 dark:text-gray-400">
              {searchTerm
                ? t('chat.history.noResults')
                : t('chat.history.noChats')}
            </p>
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="mt-2 text-sm text-green-600 dark:text-green-500 hover:underline"
              >
                {t('chat.history.clearSearch')}
              </button>
            )}
          </div>
        )}
      </div>

      {/* Confirmation Dialog */}
      {confirmDeleteId && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-sm w-full">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              {t('chat.history.confirmDelete')}
            </h3>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              {t('chat.history.confirmDeleteMessage')}
            </p>
            <div className="flex justify-end space-x-2">
              <button
                onClick={cancelDelete}
                className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={() => executeDelete(confirmDeleteId)}
                className="px-4 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700"
              >
                {t('common.delete')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatHistory;
