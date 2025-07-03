# APEX Afeka ChatBot - Comprehensive API Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Frontend APIs](#frontend-apis)
4. [Backend APIs](#backend-apis)
5. [AI Service APIs](#ai-service-apis)
6. [Usage Examples](#usage-examples)
7. [Development Guide](#development-guide)

## Project Overview

The APEX Afeka ChatBot is an intelligent AI-powered chatbot designed for Afeka College students to access academic regulations and information. The system uses RAG (Retrieval-Augmented Generation) technology for accurate, context-aware responses.

### Tech Stack
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: Python FastAPI + Supabase
- **AI Service**: Python Flask + RAG System
- **Database**: Supabase (PostgreSQL)
- **Infrastructure**: Docker + Nginx

## Architecture

```mermaid
graph TB
    U[User] --> F[Frontend - React/TypeScript]
    F --> B[Backend API - FastAPI]
    B --> AI[AI Service - Flask]
    B --> DB[(Supabase Database)]
    B --> S3[Supabase Storage]
    AI --> RAG[RAG System]
    RAG --> VDB[(Vector Database)]
```

## Frontend APIs

### Core Services

#### Chat Service (`src/frontend/src/services/chatService.ts`)

Main service for chat functionality with comprehensive message handling.

```typescript
interface Message {
  id: string;
  user_id: string;
  chat_session_id: string;
  content: string;
  created_at: string;
  is_bot: boolean;
}

interface ChatSession {
  id: string;
  user_id: string;
  title: string | null;
  created_at: string;
  updated_at: string | null;
  messages?: Message[];
}
```

**Public Methods:**

##### `getCurrentUser(): Promise<User | null>`
Gets the current authenticated user.

```typescript
const user = await chatService.getCurrentUser();
if (user) {
  console.log(`User ID: ${user.id}`);
}
```

##### `createChatSession(userId: string, title?: string): Promise<ChatSession | null>`
Creates a new chat session.

```typescript
const session = await chatService.createChatSession(
  user.id, 
  "Academic Questions"
);
```

##### `sendStreamingMessage(message, userId, history, callbacks)`
Sends messages with real-time streaming responses.

```typescript
await chatService.sendStreamingMessage(
  "What are the graduation requirements?",
  user.id,
  [],
  {
    onChunk: (chunk, accumulated) => {
      setStreamingText(accumulated);
    },
    onComplete: (fullResponse, sources) => {
      setFinalResponse(fullResponse);
      setSources(sources);
    },
    onError: (error) => {
      console.error('Streaming error:', error);
    }
  }
);
```

##### `fetchAllChatSessions(userId: string): Promise<ChatSession[]>`
Retrieves all chat sessions for a user.

##### `deleteChatSession(sessionId: string): Promise<boolean>`
Deletes a chat session and all its messages.

#### Auth Service (`src/frontend/src/services/authService.ts`)

Handles user authentication with Supabase.

```typescript
const authService = {
  signIn: (email: string, password: string) => Promise<AuthResponse>,
  signUp: (email: string, password: string, userData: object) => Promise<AuthResponse>,
  signOut: () => Promise<void>,
  resetPassword: (email: string) => Promise<void>,
  getCurrentUser: () => Promise<User | null>
}
```

**Usage Example:**
```typescript
// Sign in user
const { user, error } = await authService.signIn(
  "student@afeka.ac.il", 
  "password123"
);

// Sign out
await authService.signOut();
```

### React Components

#### Chat Components (`src/frontend/src/components/Chat/`)

##### `ChatWindow.tsx`
Main chat interface component.

```typescript
interface ChatWindowProps {
  session: ChatSession;
  onSessionUpdate: (session: ChatSession) => void;
  isStreaming?: boolean;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  session,
  onSessionUpdate,
  isStreaming = false
}) => {
  // Component implementation
};
```

**Usage:**
```tsx
<ChatWindow 
  session={currentSession}
  onSessionUpdate={handleSessionUpdate}
  isStreaming={isStreamingActive}
/>
```

##### `MessageList.tsx`
Displays chat messages with proper formatting.

```typescript
interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
  streamingText?: string;
}
```

##### `ChatInput.tsx`
Message input component with send functionality.

```typescript
interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}
```

#### Dashboard Components (`src/frontend/src/components/Dashboard/`)

##### `VectorDashboard.tsx`
Advanced admin dashboard for vector database management.

Key features:
- Document upload and processing
- Vector search analytics
- RAG performance metrics
- System monitoring

```tsx
<VectorDashboard 
  userRole="admin"
  onDocumentUpload={handleDocumentUpload}
  onVectorSearch={handleVectorSearch}
/>
```

### Custom Hooks

#### `useChat` Hook
Manages chat state and operations.

```typescript
const useChat = (sessionId?: string) => {
  return {
    messages: Message[],
    isLoading: boolean,
    sendMessage: (content: string) => Promise<void>,
    clearMessages: () => void,
    isStreaming: boolean
  };
};
```

**Usage:**
```typescript
const { messages, sendMessage, isLoading } = useChat(session.id);

const handleSend = async (message: string) => {
  await sendMessage(message);
};
```

## Backend APIs

### Core API Routes

Base URL: `http://localhost:8000`

#### Chat API (`/api/chat`)

##### `POST /api/chat`
Process chat messages with AI responses.

**Request:**
```typescript
interface ChatRequest {
  message: string;
  user_id: string;
  history?: Array<{type: string, content: string}>;
}
```

**Response:**
```typescript
interface ChatResponse {
  message: string;
  sources: Array<{
    title: string;
    content: string;
    score: number;
  }>;
  chunks: number;
  metadata: {
    timestamp: string;
    rag_used: boolean;
  };
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "What are the course requirements for Computer Science?",
    "user_id": "user123",
    "history": []
  }'
```

##### `POST /api/chat/stream`
Streaming chat with Server-Sent Events.

**Response Format:**
```typescript
// Stream events
data: {"type": "start", "content": ""}
data: {"type": "chunk", "content": "Partial response...", "accumulated": "Full response so far"}
data: {"type": "complete", "content": "Full response", "sources": [...]}
data: {"type": "end"}
```

#### Document Management (`/api/documents`)

##### `POST /api/documents/upload`
Upload documents for RAG processing.

**Request:** Multipart form with file upload
**Response:**
```typescript
{
  "document_id": "doc_123",
  "filename": "regulations.pdf",
  "status": "processing",
  "chunks_created": 45
}
```

##### `GET /api/documents`
List all processed documents.

**Response:**
```typescript
{
  "documents": [
    {
      "id": "doc_123",
      "filename": "regulations.pdf",
      "status": "ready",
      "upload_date": "2024-01-15T10:30:00Z",
      "chunk_count": 45
    }
  ]
}
```

#### Vector Management (`/api/vector`)

##### `POST /api/vector/search`
Perform semantic search in vector database.

**Request:**
```typescript
{
  "query": "graduation requirements",
  "limit": 10,
  "threshold": 0.7
}
```

**Response:**
```typescript
{
  "results": [
    {
      "content": "To graduate, students must complete...",
      "score": 0.95,
      "source_document": "academic_regulations.pdf",
      "metadata": {
        "page": 15,
        "section": "Graduation Requirements"
      }
    }
  ]
}
```

#### System Prompts (`/api/system-prompts`)

##### `GET /api/system-prompts`
Retrieve available system prompts.

##### `POST /api/system-prompts`
Create or update system prompts.

**Request:**
```typescript
{
  "name": "academic_assistant",
  "content": "You are an academic assistant for Afeka College...",
  "language": "he",
  "is_active": true
}
```

#### API Keys Management (`/api/keys`)

##### `GET /api/keys/status`
Get API key usage and status.

**Response:**
```typescript
{
  "current_key_index": 2,
  "total_keys": 5,
  "available_keys": 4,
  "usage_stats": {
    "today": 150,
    "limit": 1000
  }
}
```

### Backend Services

#### Chat Service (`src/backend/app/services/chat_service.py`)

```python
class ChatService:
    async def process_chat_message(
        self, 
        user_message: str, 
        user_id: str, 
        history: List[Dict] = None
    ) -> Dict:
        """Process chat message with RAG integration"""
        
    async def process_chat_message_stream(
        self, 
        user_message: str, 
        user_id: str, 
        history: List[Dict] = None
    ) -> AsyncGenerator[Dict, None]:
        """Process chat message with streaming response"""
```

## AI Service APIs

### RAG System (`src/ai/services/`)

#### RAG Orchestrator
Main class for coordinating RAG operations.

```python
from src.ai.services import RAGOrchestrator

# Initialize RAG service
rag_service = RAGOrchestrator()

# Process query
result = await rag_service.process_query(
    query="What is the GPA requirement?",
    user_id="user123",
    max_results=5
)
```

#### Document Processor (`src/ai/services/document_processor.py`)

Handles document ingestion and processing.

```python
class DocumentProcessor:
    def process_document(
        self, 
        file_path: str, 
        document_type: str = "pdf"
    ) -> ProcessingResult:
        """Process document for RAG system"""
        
    def chunk_document(
        self, 
        content: str, 
        chunk_size: int = 1000
    ) -> List[str]:
        """Split document into chunks"""
```

#### Smart Chunker (`src/ai/services/smart_chunker.py`)

Advanced document chunking with semantic awareness.

```python
class SmartChunker:
    def create_semantic_chunks(
        self, 
        text: str, 
        max_chunk_size: int = 1000,
        overlap: int = 200
    ) -> List[Dict]:
        """Create semantically coherent chunks"""
```

### AI Service Endpoints

Base URL: `http://localhost:5000`

#### `GET /`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "ai-service",
  "version": "2.0-minimal"
}
```

#### `GET /api/key-status`
Check AI key management status.

**Response:**
```json
{
  "status": "ok",
  "key_management": {
    "current_key_index": 1,
    "total_keys": 3,
    "available_keys": 2
  }
}
```

## Usage Examples

### Complete Chat Integration

```typescript
// Frontend React component
import { useEffect, useState } from 'react';
import { chatService } from '../services/chatService';

const ChatComponent = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);

  // Initialize chat session
  useEffect(() => {
    const initChat = async () => {
      const user = await chatService.getCurrentUser();
      if (user) {
        const session = await chatService.createChatSession(user.id);
        setCurrentSession(session);
      }
    };
    initChat();
  }, []);

  // Send message with streaming
  const handleSendMessage = async (message: string) => {
    if (!currentSession) return;

    setIsStreaming(true);
    
    // Add user message
    const userMessage = await chatService.addMessage({
      user_id: currentSession.user_id,
      chat_session_id: currentSession.id,
      content: message,
      is_bot: false
    });
    
    if (userMessage) {
      setMessages(prev => [...prev, userMessage]);
    }

    // Send to AI with streaming
    await chatService.sendStreamingMessage(
      message,
      currentSession.user_id,
      messages.map(m => ({
        type: m.is_bot ? 'bot' : 'user',
        content: m.content
      })),
      {
        onChunk: (chunk, accumulated) => {
          // Update streaming message in real-time
          setMessages(prev => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage && lastMessage.is_bot) {
              lastMessage.content = accumulated;
            } else {
              newMessages.push({
                id: `stream_${Date.now()}`,
                user_id: currentSession.user_id,
                chat_session_id: currentSession.id,
                content: accumulated,
                created_at: new Date().toISOString(),
                is_bot: true
              });
            }
            return newMessages;
          });
        },
        onComplete: (fullResponse, sources) => {
          setIsStreaming(false);
          // Save final bot message
          chatService.addMessage({
            user_id: currentSession.user_id,
            chat_session_id: currentSession.id,
            content: fullResponse,
            is_bot: true
          });
        },
        onError: (error) => {
          setIsStreaming(false);
          console.error('Chat error:', error);
        }
      }
    );
  };

  return (
    <div className="chat-container">
      <MessageList messages={messages} isLoading={isStreaming} />
      <ChatInput 
        onSendMessage={handleSendMessage}
        disabled={isStreaming}
      />
    </div>
  );
};
```

### Backend RAG Integration

```python
# Backend service example
from src.ai.services import RAGOrchestrator

class ChatService:
    def __init__(self):
        self.rag_service = RAGOrchestrator()
    
    async def process_chat_message(
        self, 
        user_message: str, 
        user_id: str, 
        history: List[Dict] = None
    ) -> Dict:
        """Process chat message with RAG"""
        
        # Get relevant context from RAG
        rag_result = await self.rag_service.process_query(
            query=user_message,
            user_id=user_id,
            max_results=5,
            threshold=0.7
        )
        
        # Build context from retrieved documents
        context = self._build_context(rag_result.get('sources', []))
        
        # Generate response with context
        response = await self._generate_response(
            user_message=user_message,
            context=context,
            history=history
        )
        
        return {
            "response": response,
            "sources": rag_result.get('sources', []),
            "chunks": len(rag_result.get('sources', [])),
            "metadata": {
                "rag_used": len(rag_result.get('sources', [])) > 0,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
```

### Document Upload and Processing

```python
# Document upload example
import aiofiles
from src.ai.services.document_processor import DocumentProcessor

@router.post("/api/documents/upload")
async def upload_document(file: UploadFile):
    """Upload and process document for RAG"""
    
    # Save uploaded file
    file_path = f"uploads/{file.filename}"
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Process document
    processor = DocumentProcessor()
    result = processor.process_document(
        file_path=file_path,
        document_type="pdf"
    )
    
    return {
        "document_id": result.document_id,
        "filename": file.filename,
        "status": "processing",
        "chunks_created": result.chunk_count
    }
```

## Development Guide

### Setup Instructions

1. **Clone Repository**
```bash
git clone https://github.com/your-org/afeka-chatbot.git
cd afeka-chatbot
```

2. **Environment Setup**
```bash
# Copy environment template
cp .env.example .env

# Add your configuration
export SUPABASE_KEY=your_key_here
export GEMINI_API_KEY=your_gemini_key
```

3. **Docker Development**
```bash
# Start all services in development mode
docker-compose -f docker-compose.dev.yml up -d

# Access services
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# AI Service: http://localhost:5000
```

### Testing

#### Backend Tests
```bash
cd src/backend
pytest tests/ -v
```

#### Frontend Tests
```bash
cd src/frontend
npm test
```

#### Integration Tests
```bash
# Test full chat flow
python -m pytest tests/integration/test_chat_flow.py
```

### API Documentation Access

- **Backend API Docs**: http://localhost:8000/docs
- **Interactive API Testing**: http://localhost:8000/redoc

### Environment Variables

#### Frontend
```env
VITE_BACKEND_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
```

#### Backend
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql://user:pass@host:port/db
```

#### AI Service
```env
BACKEND_URL=http://localhost:8000
DEBUG=false
PORT=5000
```

### Contributing

1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes with tests
3. Run full test suite: `npm test && pytest`
4. Create pull request with description

### Performance Considerations

- **Caching**: Implement Redis for frequent queries
- **Rate Limiting**: Configure per-user request limits
- **Vector Search**: Optimize embedding dimensions for speed
- **Streaming**: Use WebSocket for real-time features

### Security Notes

- All API endpoints require authentication
- Implement CORS properly for production
- Sanitize user inputs before processing
- Use HTTPS in production environments
- Regularly rotate API keys

For more detailed information, see the project README and individual component documentation.