import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Trash2, Edit } from 'lucide-react';
import { ChatSession } from '../../services/chatService';

interface ChatHistoryProps {
  sessions: ChatSession[];
  onSelectSession: (session: ChatSession) => void;
  onDeleteSession: (sessionId: string) => void;
  onEditSessionTitle: (sessionId: string, title: string) => void;
  activeSessionId?: string;
  isLoading: boolean;
}

const ChatHistory: React.FC<ChatHistoryProps> = ({
  sessions,
  onSelectSession,
  onDeleteSession,
  onEditSessionTitle,
  activeSessionId,
  isLoading
}) => {
  const { t } = useTranslation();
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');



  // Start editing a session title
  const startEditing = (session: ChatSession, event?: React.MouseEvent) => {
    if (event) event.stopPropagation();
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

  // Delete session
  const deleteSession = (sessionId: string, event?: React.MouseEvent) => {
    if (event) event.stopPropagation();
    onDeleteSession(sessionId);
  };

  return (
    <div className="h-full flex flex-col" data-testid="chat-history">
      {/* Sessions list */}
      {isLoading ? (
        <div className="flex items-center justify-center py-4">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-green-700 dark:border-green-500"></div>
        </div>
      ) : sessions.length > 0 ? (
        <ul className="text-sm flex-1 overflow-y-auto">
          {sessions.map((session) => (
            <li
              key={session.id}
              className={`${
                activeSessionId === session.id 
                  ? 'bg-gray-200 dark:bg-gray-800 text-black dark:text-white font-medium' 
                  : 'hover:bg-gray-100 dark:hover:bg-gray-900 text-gray-800 dark:text-gray-300'
              }`}
            >
              {editingSessionId === session.id ? (
                <div className="p-2" onClick={(e) => e.stopPropagation()}>
                  <input
                    type="text"
                    className="w-full px-2 py-1 text-xs rounded border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-green-500"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onBlur={() => saveTitle(session.id)}
                    onKeyDown={(e) => handleKeyDown(e, session.id)}
                    autoFocus
                  />
                </div>
              ) : (
                <div
                  className="py-1.5 px-3 flex justify-between items-center cursor-pointer group"
                  onClick={() => onSelectSession(session)}
                >
                  <div className="truncate flex-1 text-sm">
                    {session.title || t('chat.history.untitled', 'שיחה ללא כותרת')}
                  </div>
                  
                  <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => startEditing(session, e)}
                      className="p-0.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 focus:outline-none"
                      title={t('chat.history.edit') as string}
                    >
                      <Edit className="w-3 h-3" />
                    </button>
                    <button
                      onClick={(e) => deleteSession(session.id, e)}
                      className="p-0.5 text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400 focus:outline-none"
                      title={t('chat.history.delete') as string}
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <div className="text-center p-4 text-gray-500 dark:text-gray-400 text-xs">
          {t('chat.history.noChats')}
        </div>
      )}
    </div>
  );
};

export default ChatHistory;
