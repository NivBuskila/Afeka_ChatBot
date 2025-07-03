# Backend API Guide

## Table of Contents
- [API Overview](#api-overview)
- [Authentication](#authentication)
- [Chat API](#chat-api)
- [Document Management](#document-management)
- [Vector Management](#vector-management)
- [User Management](#user-management)
- [System Administration](#system-administration)
- [Services Documentation](#services-documentation)
- [Database Models](#database-models)

## API Overview

**Base URL:** `http://localhost:8000`
**Documentation:** `http://localhost:8000/docs` (Swagger UI)
**Alternative Docs:** `http://localhost:8000/redoc`

### General Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Error responses:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": { /* error details */ }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Authentication

The API uses Supabase JWT tokens for authentication.

### Headers

```bash
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Getting Authentication Token

```typescript
// Frontend: Get current session token
const { data: { session } } = await supabase.auth.getSession();
const token = session?.access_token;

// Use in API calls
const response = await fetch(`${BACKEND_URL}/api/protected-endpoint`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

## Chat API

### POST `/api/chat`

Process chat messages with AI responses.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```typescript
interface ChatRequest {
  message: string;
  user_id: string;
  history?: Array<{
    type: 'user' | 'bot';
    content: string;
  }>;
  session_id?: string;
  context?: {
    document_filter?: string[];
    max_sources?: number;
  };
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "מה הם דרישות הסיום ללימודי מדעי המחשב?",
    "user_id": "user_12345",
    "history": [
      {
        "type": "user",
        "content": "שלום"
      },
      {
        "type": "bot", 
        "content": "שלום! איך אני יכול לעזור לך היום?"
      }
    ]
  }'
```

**Response:**
```typescript
interface ChatResponse {
  message: string;
  sources: Array<{
    title: string;
    content: string;
    score: number;
    metadata: {
      document_id: string;
      page?: number;
      section?: string;
    };
  }>;
  chunks: number;
  metadata: {
    timestamp: string;
    rag_used: boolean;
    response_time_ms: number;
    token_usage: {
      prompt_tokens: number;
      completion_tokens: number;
      total_tokens: number;
    };
  };
}
```

**Example Response:**
```json
{
  "message": "דרישות הסיום ללימודי מדעי המחשב כוללות השלמת 120 נקודות זכות...",
  "sources": [
    {
      "title": "תקנון אקדמי - דרישות סיום",
      "content": "על מנת לסיים את התואר בהצלחה...",
      "score": 0.95,
      "metadata": {
        "document_id": "doc_123",
        "page": 15,
        "section": "דרישות הסיום"
      }
    }
  ],
  "chunks": 3,
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "rag_used": true,
    "response_time_ms": 1250,
    "token_usage": {
      "prompt_tokens": 850,
      "completion_tokens": 120,
      "total_tokens": 970
    }
  }
}
```

### POST `/api/chat/stream`

Streaming chat with Server-Sent Events (SSE).

**Request:** Same as regular chat endpoint

**Response:** Server-Sent Events stream

**Event Types:**
```typescript
// Stream start
data: {"type": "start", "content": ""}

// Content chunks
data: {"type": "chunk", "content": "חלק", "accumulated": "חלק מהתשובה"}

// Complete response with sources
data: {"type": "complete", "content": "תשובה מלאה", "sources": [...]}

// Stream end
data: {"type": "end"}

// Error
data: {"type": "error", "content": "Error message"}
```

**Usage Example:**
```javascript
const eventSource = new EventSource('/api/chat/stream', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'chunk':
      updateStreamingText(data.accumulated);
      break;
    case 'complete':
      setFinalResponse(data.content, data.sources);
      break;
    case 'error':
      handleError(data.content);
      break;
  }
};
```

### GET `/api/chat/status`

Get chat system status and configuration.

**Response:**
```json
{
  "service_type": "chat_service",
  "settings": {
    "max_context_tokens": 4000,
    "langchain_history_k": 10,
    "gemini_model": "gemini-1.5-flash"
  },
  "features": {
    "rag_integration": true,
    "streaming": true,
    "conversation_memory": true,
    "source_tracking": true
  },
  "status": {
    "ai_service_healthy": true,
    "vector_db_healthy": true,
    "last_health_check": "2024-01-15T10:30:00Z"
  }
}
```

## Document Management

### POST `/api/documents/upload`

Upload documents for RAG processing.

**Request:** Multipart form data
```
Content-Type: multipart/form-data

file: <file_data>
document_type: "pdf" | "docx" | "txt"
title?: string
category?: string
language?: "he" | "en"
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@regulation.pdf" \
  -F "document_type=pdf" \
  -F "title=תקנון אקדמי 2024" \
  -F "category=regulations" \
  -F "language=he"
```

**Response:**
```json
{
  "document_id": "doc_456",
  "filename": "regulation.pdf",
  "title": "תקנון אקדמי 2024",
  "status": "processing",
  "estimated_processing_time": "5-10 minutes",
  "file_info": {
    "size_bytes": 2048576,
    "pages": 45,
    "detected_language": "he"
  }
}
```

### GET `/api/documents`

List all processed documents.

**Query Parameters:**
- `status`: Filter by status (`processing`, `ready`, `error`)
- `category`: Filter by category
- `search`: Search in title/content
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)

**Example:**
```bash
curl "http://localhost:8000/api/documents?status=ready&category=regulations&limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "documents": [
    {
      "id": "doc_123",
      "filename": "regulations.pdf",
      "title": "תקנון אקדמי",
      "status": "ready",
      "category": "regulations",
      "language": "he",
      "upload_date": "2024-01-15T08:00:00Z",
      "processed_date": "2024-01-15T08:05:00Z",
      "chunk_count": 45,
      "file_info": {
        "size_bytes": 1024000,
        "pages": 30
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 25,
    "pages": 3
  }
}
```

### GET `/api/documents/{document_id}`

Get specific document details.

**Response:**
```json
{
  "id": "doc_123",
  "filename": "regulations.pdf",
  "title": "תקנון אקדמי",
  "status": "ready",
  "chunks": [
    {
      "id": "chunk_1",
      "content": "חלק מהמסמך...",
      "page": 1,
      "section": "מבוא"
    }
  ],
  "processing_log": [
    {
      "timestamp": "2024-01-15T08:00:00Z",
      "status": "uploaded",
      "message": "File uploaded successfully"
    },
    {
      "timestamp": "2024-01-15T08:05:00Z", 
      "status": "processed",
      "message": "Document processed into 45 chunks"
    }
  ]
}
```

### DELETE `/api/documents/{document_id}`

Delete a document and all its chunks.

**Response:**
```json
{
  "success": true,
  "message": "Document deleted successfully",
  "deleted_chunks": 45
}
```

## Vector Management

### POST `/api/vector/search`

Perform semantic search in vector database.

**Request:**
```json
{
  "query": "דרישות סיום",
  "limit": 10,
  "threshold": 0.7,
  "filters": {
    "document_category": ["regulations", "academic"],
    "language": "he"
  },
  "include_metadata": true
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "על מנת לסיים את התואר...",
      "score": 0.95,
      "chunk_id": "chunk_123",
      "document_id": "doc_456",
      "metadata": {
        "title": "תקנון אקדמי",
        "page": 15,
        "section": "דרישות סיום",
        "category": "regulations"
      }
    }
  ],
  "query_metadata": {
    "search_time_ms": 45,
    "total_chunks_searched": 1500,
    "embedding_time_ms": 12
  }
}
```

### GET `/api/vector/stats`

Get vector database statistics.

**Response:**
```json
{
  "total_chunks": 1500,
  "total_documents": 25,
  "embedding_dimensions": 768,
  "languages": {
    "he": 1200,
    "en": 300
  },
  "categories": {
    "regulations": 800,
    "academic": 400,
    "general": 300
  },
  "last_updated": "2024-01-15T10:00:00Z"
}
```

### POST `/api/vector/reindex/{document_id}`

Reindex a specific document.

**Response:**
```json
{
  "success": true,
  "message": "Document reindexing started",
  "job_id": "reindex_job_789",
  "estimated_time": "3-5 minutes"
}
```

## User Management

### GET `/api/users/profile`

Get current user profile.

**Response:**
```json
{
  "id": "user_123",
  "email": "student@afeka.ac.il",
  "profile": {
    "full_name": "שם המשתמש",
    "student_id": "123456789",
    "department": "מדעי המחשב",
    "year": 3
  },
  "preferences": {
    "language": "he",
    "notifications": true,
    "chat_history_retention": 30
  },
  "statistics": {
    "total_messages": 150,
    "sessions_count": 25,
    "last_activity": "2024-01-15T10:30:00Z"
  }
}
```

### PUT `/api/users/profile`

Update user profile.

**Request:**
```json
{
  "profile": {
    "full_name": "שם חדש",
    "department": "הנדסת תוכנה"
  },
  "preferences": {
    "language": "en",
    "notifications": false
  }
}
```

### GET `/api/users/sessions`

Get user's chat sessions.

**Query Parameters:**
- `limit`: Number of sessions (default: 20)
- `offset`: Pagination offset
- `search`: Search in session titles

**Response:**
```json
{
  "sessions": [
    {
      "id": "session_123",
      "title": "שאלות על תקנון",
      "created_at": "2024-01-15T09:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "message_count": 12,
      "last_message_preview": "תודה על העזרה!"
    }
  ],
  "pagination": {
    "total": 25,
    "limit": 20,
    "offset": 0
  }
}
```

## System Administration

### GET `/api/admin/statistics`

Get system-wide statistics (admin only).

**Response:**
```json
{
  "users": {
    "total": 1500,
    "active_today": 45,
    "active_this_week": 200
  },
  "messages": {
    "total": 25000,
    "today": 150,
    "this_week": 800
  },
  "documents": {
    "total": 50,
    "processing": 2,
    "ready": 48
  },
  "api_usage": {
    "requests_today": 500,
    "tokens_used_today": 25000,
    "average_response_time_ms": 850
  }
}
```

### GET `/api/admin/health`

Comprehensive system health check.

**Response:**
```json
{
  "overall_status": "healthy",
  "services": {
    "database": {
      "status": "healthy",
      "response_time_ms": 12,
      "last_check": "2024-01-15T10:30:00Z"
    },
    "ai_service": {
      "status": "healthy",
      "response_time_ms": 45,
      "last_check": "2024-01-15T10:30:00Z"
    },
    "vector_db": {
      "status": "healthy",
      "response_time_ms": 8,
      "last_check": "2024-01-15T10:30:00Z"
    }
  },
  "resources": {
    "memory_usage_percent": 65,
    "cpu_usage_percent": 25,
    "disk_usage_percent": 40
  }
}
```

### POST `/api/admin/system-prompts`

Manage system prompts (admin only).

**Request:**
```json
{
  "name": "academic_assistant_he",
  "content": "אתה עוזר אקדמי למכללת אפקה...",
  "language": "he",
  "category": "academic",
  "is_active": true,
  "metadata": {
    "version": "2.1",
    "author": "admin",
    "description": "Hebrew academic assistant prompt"
  }
}
```

## Services Documentation

### Chat Service

**Location:** `src/backend/app/services/chat_service.py`

```python
class ChatService:
    def __init__(self):
        self.rag_service = RAGOrchestrator()
        self.conversation_memory = ConversationBufferWindowMemory(k=10)
    
    async def process_chat_message(
        self, 
        user_message: str, 
        user_id: str, 
        history: List[Dict] = None
    ) -> Dict:
        """
        Process a chat message with RAG integration.
        
        Args:
            user_message: The user's message
            user_id: Unique identifier for the user
            history: Previous conversation history
            
        Returns:
            Dict containing response, sources, and metadata
        """
        
    async def process_chat_message_stream(
        self, 
        user_message: str, 
        user_id: str, 
        history: List[Dict] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        Process chat message with streaming response.
        
        Yields:
            Dict with streaming chunks and metadata
        """
```

**Usage:**
```python
# Initialize service
chat_service = ChatService()

# Process message
result = await chat_service.process_chat_message(
    user_message="מה הם דרישות הסיום?",
    user_id="user_123",
    history=[
        {"type": "user", "content": "שלום"},
        {"type": "bot", "content": "שלום! איך אני יכול לעזור?"}
    ]
)

# Access response
print(result["response"])
print(f"Sources found: {len(result['sources'])}")
```

### Document Service

```python
class DocumentService:
    async def upload_document(
        self, 
        file_data: bytes, 
        filename: str,
        document_type: str = "pdf",
        metadata: Dict = None
    ) -> DocumentUploadResult:
        """Upload and process document for RAG system"""
        
    async def get_document_status(self, document_id: str) -> DocumentStatus:
        """Get processing status of a document"""
        
    async def delete_document(self, document_id: str) -> bool:
        """Delete document and all its chunks"""
```

### Vector Service

```python
class VectorService:
    async def search_similar(
        self, 
        query: str, 
        limit: int = 10,
        threshold: float = 0.7,
        filters: Dict = None
    ) -> List[SearchResult]:
        """Perform semantic search in vector database"""
        
    async def add_document_chunks(
        self, 
        document_id: str, 
        chunks: List[str],
        metadata: List[Dict] = None
    ) -> int:
        """Add document chunks to vector database"""
```

## Database Models

### User Model

```python
class User(BaseModel):
    id: str
    email: str
    created_at: datetime
    updated_at: datetime
    profile: UserProfile
    preferences: UserPreferences

class UserProfile(BaseModel):
    full_name: str
    student_id: Optional[str]
    department: Optional[str]
    year: Optional[int]

class UserPreferences(BaseModel):
    language: str = "he"
    notifications: bool = True
    chat_history_retention: int = 30
```

### Chat Models

```python
class ChatSession(BaseModel):
    id: str
    user_id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

class Message(BaseModel):
    id: str
    session_id: str
    user_id: str
    content: str
    is_bot: bool
    created_at: datetime
    metadata: Optional[Dict] = None

class ChatRequest(BaseModel):
    message: str
    user_id: str
    history: Optional[List[Dict]] = None
    session_id: Optional[str] = None
    context: Optional[Dict] = None
```

### Document Models

```python
class Document(BaseModel):
    id: str
    filename: str
    title: Optional[str]
    category: Optional[str]
    language: str = "he"
    status: DocumentStatus
    upload_date: datetime
    processed_date: Optional[datetime]
    chunk_count: int = 0
    file_info: FileInfo

class DocumentChunk(BaseModel):
    id: str
    document_id: str
    content: str
    chunk_index: int
    metadata: Dict

class FileInfo(BaseModel):
    size_bytes: int
    pages: Optional[int]
    detected_language: Optional[str]
```

## Error Handling

### Common Error Codes

```python
class ErrorCodes:
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RAG_SERVICE_ERROR = "RAG_SERVICE_ERROR"
    DOCUMENT_PROCESSING_ERROR = "DOCUMENT_PROCESSING_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
```

### Error Response Examples

**Validation Error (422):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "message",
      "error": "Message cannot be empty"
    }
  }
}
```

**Authentication Error (401):**
```json
{
  "success": false,
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Valid authentication token required"
  }
}
```

**Rate Limit Error (429):**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "details": {
      "retry_after_seconds": 60,
      "current_limit": "100 requests per hour"
    }
  }
}
```

## Testing Examples

### Unit Tests

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_endpoint():
    response = client.post(
        "/api/chat",
        headers={"Authorization": "Bearer test_token"},
        json={
            "message": "Test message",
            "user_id": "test_user"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "sources" in data

@pytest.mark.asyncio
async def test_chat_service():
    chat_service = ChatService()
    result = await chat_service.process_chat_message(
        user_message="Test question",
        user_id="test_user"
    )
    assert result["response"] is not None
    assert isinstance(result["sources"], list)
```

### Integration Tests

```python
def test_document_upload_and_search():
    # Upload document
    with open("test_document.pdf", "rb") as f:
        upload_response = client.post(
            "/api/documents/upload",
            headers={"Authorization": "Bearer test_token"},
            files={"file": f},
            data={"document_type": "pdf"}
        )
    
    assert upload_response.status_code == 200
    document_id = upload_response.json()["document_id"]
    
    # Wait for processing
    time.sleep(5)
    
    # Search in uploaded document
    search_response = client.post(
        "/api/vector/search",
        headers={"Authorization": "Bearer test_token"},
        json={
            "query": "test query",
            "limit": 5
        }
    )
    
    assert search_response.status_code == 200
    results = search_response.json()["results"]
    assert len(results) > 0
```

This comprehensive backend API guide provides detailed documentation for all endpoints, services, and integration patterns in the APEX Afeka ChatBot system.