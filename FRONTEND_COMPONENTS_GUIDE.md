# Frontend Components Guide

## Table of Contents
- [Core Components](#core-components)
- [Chat Components](#chat-components)
- [Dashboard Components](#dashboard-components)
- [UI Components](#ui-components)
- [Hooks and Utilities](#hooks-and-utilities)

## Core Components

### App Component (`src/frontend/src/App.tsx`)

Main application component handling routing and global state.

```tsx
interface AppProps {
  // No props - root component
}

// Key features:
// - Route management
// - Authentication state
// - Theme provider
// - Error boundaries
```

**Usage:**
```tsx
import { App } from './App';
import { createRoot } from 'react-dom/client';

const root = createRoot(document.getElementById('root')!);
root.render(<App />);
```

## Chat Components

### ChatWindow Component

**Location:** `src/frontend/src/components/Chat/ChatWindow.tsx`

Main chat interface providing complete chat functionality.

```tsx
interface ChatWindowProps {
  session: ChatSession;
  onSessionUpdate: (session: ChatSession) => void;
  isStreaming?: boolean;
  className?: string;
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  session,
  onSessionUpdate,
  isStreaming = false,
  className = ""
}) => {
  // Implementation
};
```

**Features:**
- Real-time message streaming
- Message history management
- File upload support
- Copy message functionality
- Auto-scroll to latest message

**Usage Example:**
```tsx
const ChatPage = () => {
  const [currentSession, setCurrentSession] = useState<ChatSession>();
  const [isStreaming, setIsStreaming] = useState(false);

  return (
    <ChatWindow
      session={currentSession}
      onSessionUpdate={setCurrentSession}
      isStreaming={isStreaming}
      className="h-full w-full"
    />
  );
};
```

### MessageList Component

**Location:** `src/frontend/src/components/Chat/MessageList.tsx`

Displays chat messages with proper formatting and interactions.

```tsx
interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
  streamingText?: string;
  onMessageCopy?: (content: string) => void;
  className?: string;
}
```

**Features:**
- Markdown rendering
- Code syntax highlighting
- Message copying
- Loading indicators
- Auto-scroll behavior

**Usage:**
```tsx
<MessageList
  messages={chatMessages}
  isLoading={isAIThinking}
  streamingText={currentStreamText}
  onMessageCopy={handleCopyMessage}
  className="flex-1 overflow-y-auto"
/>
```

### MessageItem Component

**Location:** `src/frontend/src/components/Chat/MessageItem.tsx`

Individual message component with rich formatting.

```tsx
interface MessageItemProps {
  message: Message;
  isStreaming?: boolean;
  onCopy?: (content: string) => void;
  showAvatar?: boolean;
}
```

**Features:**
- User/bot message distinction
- Timestamp display
- Copy functionality
- Avatar support
- Markdown rendering

### ChatInput Component

**Location:** `src/frontend/src/components/Chat/ChatInput.tsx`

Message input component with enhanced features.

```tsx
interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
  onFileUpload?: (file: File) => void;
  allowFileUpload?: boolean;
}
```

**Features:**
- Multi-line input support
- File upload integration
- Character count
- Send on Enter (with Shift+Enter for new line)
- Auto-resize textarea

**Usage:**
```tsx
<ChatInput
  onSendMessage={handleSendMessage}
  disabled={isProcessing}
  placeholder="שאל שאלה על התקנון האקדמי..."
  maxLength={4000}
  onFileUpload={handleFileUpload}
  allowFileUpload={true}
/>
```

### ChatHistory Component

**Location:** `src/frontend/src/components/Chat/ChatHistory.tsx`

Sidebar component for managing chat sessions.

```tsx
interface ChatHistoryProps {
  sessions: ChatSession[];
  currentSessionId?: string;
  onSessionSelect: (session: ChatSession) => void;
  onSessionDelete: (sessionId: string) => void;
  onNewChat: () => void;
  isLoading?: boolean;
}
```

**Features:**
- Session list with search
- Session creation/deletion
- Session title editing
- Date grouping

**Usage:**
```tsx
<ChatHistory
  sessions={userSessions}
  currentSessionId={activeSession?.id}
  onSessionSelect={handleSessionSelect}
  onSessionDelete={handleDeleteSession}
  onNewChat={handleNewChat}
  isLoading={isLoadingSessions}
/>
```

## Dashboard Components

### VectorDashboard Component

**Location:** `src/frontend/src/components/VectorDashboard.tsx`

Advanced dashboard for vector database management and analytics.

```tsx
interface VectorDashboardProps {
  userRole: 'admin' | 'user';
  onDocumentUpload?: (file: File) => Promise<void>;
  onVectorSearch?: (query: string) => Promise<SearchResult[]>;
  className?: string;
}
```

**Features:**
- Document management
- Vector search interface
- Performance analytics
- System monitoring
- User management (admin only)

**Usage:**
```tsx
<VectorDashboard
  userRole={user.role}
  onDocumentUpload={handleDocumentUpload}
  onVectorSearch={handleVectorSearch}
  className="container mx-auto p-4"
/>
```

### Analytics Components

#### TokenUsageChart
```tsx
interface TokenUsageChartProps {
  data: TokenUsageData[];
  timeRange: 'day' | 'week' | 'month';
}
```

#### SearchAnalytics
```tsx
interface SearchAnalyticsProps {
  searchData: SearchAnalyticsData;
  onExport?: () => void;
}
```

## UI Components

Located in `src/frontend/src/components/ui/`

### Button Component

```tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  icon?: React.ReactNode;
}

// Usage
<Button 
  variant="primary" 
  size="lg" 
  isLoading={isSubmitting}
  onClick={handleSubmit}
>
  שלח הודעה
</Button>
```

### Modal Component

```tsx
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

// Usage
<Modal
  isOpen={isModalOpen}
  onClose={() => setIsModalOpen(false)}
  title="הגדרות צ'אט"
  size="md"
>
  <SettingsContent />
</Modal>
```

### Input Components

```tsx
// TextInput
interface TextInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

// TextArea
interface TextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  autoResize?: boolean;
}
```

### Loading Components

```tsx
// Spinner
interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
}

// LoadingScreen
interface LoadingScreenProps {
  message?: string;
  progress?: number; // 0-100
}
```

## Hooks and Utilities

### Custom Hooks

#### useChat Hook

```tsx
const useChat = (sessionId?: string) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);

  const sendMessage = async (content: string) => {
    // Implementation
  };

  const clearMessages = () => {
    setMessages([]);
  };

  return {
    messages,
    isLoading,
    isStreaming,
    sendMessage,
    clearMessages,
    // Additional methods
  };
};

// Usage
const ChatComponent = () => {
  const { messages, sendMessage, isLoading } = useChat(sessionId);
  
  return (
    <div>
      <MessageList messages={messages} isLoading={isLoading} />
      <ChatInput onSendMessage={sendMessage} disabled={isLoading} />
    </div>
  );
};
```

#### useAuth Hook

```tsx
const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const signIn = async (email: string, password: string) => {
    // Implementation
  };

  const signOut = async () => {
    // Implementation
  };

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    signIn,
    signOut,
  };
};
```

#### useLocalStorage Hook

```tsx
const useLocalStorage = <T>(key: string, initialValue: T) => {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  };

  return [storedValue, setValue] as const;
};

// Usage
const [chatSettings, setChatSettings] = useLocalStorage('chatSettings', {
  language: 'he',
  theme: 'light'
});
```

### Utility Functions

#### Format Utilities

```tsx
// Date formatting
export const formatMessageTime = (date: string | Date): string => {
  const messageDate = new Date(date);
  const now = new Date();
  const diffInHours = (now.getTime() - messageDate.getTime()) / (1000 * 60 * 60);

  if (diffInHours < 24) {
    return messageDate.toLocaleTimeString('he-IL', {
      hour: '2-digit',
      minute: '2-digit'
    });
  } else {
    return messageDate.toLocaleDateString('he-IL');
  }
};

// Text utilities
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// Copy to clipboard
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error('Failed to copy:', error);
    return false;
  }
};
```

### Context Providers

#### ChatContext

```tsx
interface ChatContextType {
  currentSession: ChatSession | null;
  sessions: ChatSession[];
  createSession: (title?: string) => Promise<ChatSession | null>;
  selectSession: (session: ChatSession) => void;
  deleteSession: (sessionId: string) => Promise<boolean>;
}

const ChatContext = React.createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Implementation
  
  return (
    <ChatContext.Provider value={contextValue}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within ChatProvider');
  }
  return context;
};
```

#### AuthContext

```tsx
interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  signIn: (email: string, password: string) => Promise<AuthResult>;
  signOut: () => Promise<void>;
  signUp: (email: string, password: string, userData: object) => Promise<AuthResult>;
}

// Usage in App
<AuthProvider>
  <ChatProvider>
    <Router>
      <Routes>
        {/* Your routes */}
      </Routes>
    </Router>
  </ChatProvider>
</AuthProvider>
```

## Component Styling Guide

### Tailwind CSS Classes

Common patterns used throughout the application:

```tsx
// Layout
const layoutClasses = {
  container: "container mx-auto px-4",
  flexCenter: "flex items-center justify-center",
  flexBetween: "flex items-center justify-between",
  grid: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
};

// Chat specific
const chatClasses = {
  chatContainer: "flex flex-col h-screen bg-gray-50",
  messageList: "flex-1 overflow-y-auto p-4 space-y-4",
  userMessage: "ml-auto max-w-xs lg:max-w-md px-4 py-2 bg-blue-500 text-white rounded-lg",
  botMessage: "mr-auto max-w-xs lg:max-w-md px-4 py-2 bg-white border rounded-lg",
  inputArea: "border-t bg-white p-4"
};

// States
const stateClasses = {
  loading: "animate-pulse bg-gray-200",
  error: "border-red-500 text-red-500",
  success: "border-green-500 text-green-500",
  disabled: "opacity-50 cursor-not-allowed"
};
```

### RTL Support

The application supports Hebrew (RTL) layout:

```tsx
// RTL-aware components
const RTLAwareComponent = () => (
  <div className="rtl:text-right ltr:text-left">
    <p className="rtl:mr-4 ltr:ml-4">Content with proper spacing</p>
  </div>
);

// Direction-specific classes
const directionClasses = {
  marginStart: "rtl:mr-4 ltr:ml-4",
  marginEnd: "rtl:ml-4 ltr:mr-4",
  paddingStart: "rtl:pr-4 ltr:pl-4",
  paddingEnd: "rtl:pl-4 ltr:pr-4"
};
```

## Component Testing Examples

```tsx
// Test example for ChatInput component
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatInput } from '../ChatInput';

describe('ChatInput', () => {
  const mockOnSendMessage = jest.fn();

  beforeEach(() => {
    mockOnSendMessage.mockClear();
  });

  test('sends message on button click', async () => {
    render(
      <ChatInput 
        onSendMessage={mockOnSendMessage}
        placeholder="Type a message..."
      />
    );

    const input = screen.getByPlaceholderText('Type a message...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
    });
  });

  test('sends message on Enter key', async () => {
    render(<ChatInput onSendMessage={mockOnSendMessage} />);

    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    await waitFor(() => {
      expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
    });
  });
});
```

This comprehensive guide covers all the major frontend components, their APIs, usage patterns, and best practices for the APEX Afeka ChatBot application.