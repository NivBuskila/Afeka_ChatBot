# CLAUDE.md - AI Assistant Guide for APEX Afeka ChatBot

> **Purpose**: This document provides AI assistants with comprehensive guidance for understanding, navigating, and contributing to the Afeka_ChatBot codebase effectively.

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture Overview](#architecture-overview)
- [Codebase Structure](#codebase-structure)
- [Development Workflows](#development-workflows)
- [Key Conventions](#key-conventions)
- [Common Tasks](#common-tasks)
- [Testing Guidelines](#testing-guidelines)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

---

## Project Overview

### What is APEX Afeka ChatBot?

A sophisticated AI-powered chatbot system designed for Afeka College of Engineering students, providing quick and accurate information about academic regulations, procedures, and institutional data.

**Key Technologies:**
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI (Python 3.11+) with Pydantic validation
- **AI/RAG**: LangChain + Google Generative AI (Gemini) + pgvector
- **Database**: Supabase (PostgreSQL + Auth + Storage)
- **Infrastructure**: Docker Compose

**Core Features:**
- RAG-powered intelligent responses
- Document management and processing
- Admin dashboard with analytics
- Multilingual support (Hebrew/English)
- Real-time streaming chat
- API key rotation and management

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                         │
│  React + TypeScript (Vite) + Tailwind CSS + i18next        │
│                    Port: 80 / 5173 (dev)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ HTTP/REST API
                           │ SSE (Server-Sent Events)
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                     API GATEWAY LAYER                        │
│           FastAPI + Pydantic + AsyncIO (Port 8000)          │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────────┐   │
│  │   Routes    │ │   Services   │ │   Repositories    │   │
│  │  (API       │→│   (Business  │→│   (Data Access    │   │
│  │  Endpoints) │ │   Logic)     │ │   Layer)          │   │
│  └─────────────┘ └──────────────┘ └───────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
┌───────────────▼─────────┐  ┌───────▼──────────────────────┐
│      AI SERVICE          │  │    DATABASE & STORAGE        │
│  Flask (Port 5000)      │  │  Supabase (PostgreSQL +      │
│  - RAG Orchestrator     │  │  pgvector + Auth + Storage)  │
│  - Document Processor   │  │  - Row Level Security (RLS)  │
│  - Embedding Service    │  │  - Vector Search             │
│  - Key Manager          │  │  - File Storage              │
└─────────────────────────┘  └──────────────────────────────┘
```

### Service Responsibilities

| Service | Primary Responsibilities | Port |
|---------|-------------------------|------|
| **Frontend** | UI/UX, routing, state management, i18n | 80 / 5173 |
| **Backend** | API gateway, auth, business logic, RAG orchestration | 8000 |
| **AI Service** | RAG processing, document embedding, key rotation | 5000 |
| **Supabase** | Database, auth, storage, vector search | - |

### Data Flow Patterns

**Chat Request Flow:**
```
User Input → ChatWindow.tsx → chatService.ts → Backend /api/chat/stream
           → ChatService → RAGService → RAGOrchestrator
           → Search Services → Context Builder → Answer Generator
           → LLM (Gemini) → Stream Response → Frontend
```

**Document Upload Flow:**
```
User Upload → DocumentService → Backend /api/documents
           → Supabase Storage → Background Processor
           → DocumentProcessor → SmartChunker → Embedding Service
           → Vector Store (pgvector)
```

---

## Codebase Structure

### Repository Layout

```
Afeka_ChatBot/
├── src/
│   ├── frontend/              # React/TypeScript application
│   │   ├── src/
│   │   │   ├── components/   # React components (organized by feature)
│   │   │   ├── services/     # API service layer
│   │   │   ├── hooks/        # Custom React hooks
│   │   │   ├── contexts/     # React Context providers
│   │   │   ├── i18n/         # Internationalization (he/en)
│   │   │   ├── types/        # TypeScript type definitions
│   │   │   ├── utils/        # Utility functions
│   │   │   ├── config/       # Configuration (Supabase client)
│   │   │   └── App.tsx       # Main app component
│   │   ├── public/           # Static assets
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   └── tsconfig.json
│   │
│   ├── backend/               # FastAPI application
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   └── routes/   # API route handlers
│   │   │   ├── services/     # Business logic layer
│   │   │   ├── repositories/ # Data access layer
│   │   │   ├── middleware/   # HTTP middleware
│   │   │   ├── core/         # Core app logic (app factory, auth)
│   │   │   ├── config/       # Settings (Pydantic)
│   │   │   ├── domain/       # Domain models
│   │   │   ├── models/       # Pydantic schemas
│   │   │   └── utils/        # Utilities
│   │   └── main.py           # Application entry point
│   │
│   ├── ai/                    # AI/RAG service (Flask)
│   │   ├── services/
│   │   │   ├── rag/          # Modular RAG architecture
│   │   │   │   ├── rag_orchestrator.py
│   │   │   │   ├── embedding_service.py
│   │   │   │   ├── search_services.py
│   │   │   │   ├── context_builder.py
│   │   │   │   └── answer_generator.py
│   │   │   ├── document_processor.py
│   │   │   └── smart_chunker.py
│   │   ├── config/           # RAG configuration & profiles
│   │   │   ├── rag_config.py
│   │   │   ├── rag_config_profiles.py
│   │   │   ├── system_prompts.py
│   │   │   └── current_profile.py
│   │   ├── core/             # Key management, token tracking
│   │   ├── scripts/          # Automation scripts
│   │   └── app.py            # Flask app (minimal, mostly health checks)
│   │
│   └── tests/                 # Test suites
│       ├── backend/          # Backend tests (Python)
│       └── frontend/         # Frontend tests (Vitest + Cypress)
│           ├── unit-integration/  # Vitest tests with MSW mocks
│           └── e2e/          # Cypress E2E tests
│
├── supabase/
│   └── migrations/           # Database schema migrations (28 files)
│
├── RAG_Test_Pro/             # RAG testing environment
│
├── .env.example              # Environment variable template
├── package.json              # Root package.json
├── pyproject.toml            # Python project config
├── README.md                 # Project documentation
└── SECURITY.md               # Security guidelines
```

### Key Directory Purposes

| Directory | Purpose | When to Modify |
|-----------|---------|----------------|
| `src/frontend/src/components/` | React UI components | Adding/modifying UI features |
| `src/frontend/src/services/` | API integration layer | Changing API contracts |
| `src/backend/app/api/routes/` | API endpoint definitions | Adding new endpoints |
| `src/backend/app/services/` | Business logic | Implementing features |
| `src/backend/app/repositories/` | Database operations | Changing data access patterns |
| `src/ai/services/rag/` | RAG processing logic | Improving RAG quality |
| `src/ai/config/` | RAG configuration | Tuning RAG parameters |
| `supabase/migrations/` | Database schema | Schema changes (add new migration) |

---

## Development Workflows

### Setting Up the Development Environment

**Prerequisites:**
- Docker & Docker Compose
- Git
- Supabase account with project created

**Initial Setup:**
```bash
# 1. Clone repository
git clone https://github.com/NivBuskila/Afeka_ChatBot.git
cd Afeka_ChatBot

# 2. Create .env file from template
cp .env.example .env

# 3. Edit .env with your credentials
# Required: SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY

# 4. Start development environment
docker-compose -f docker-compose.dev.yml up -d

# 5. Access services
# Frontend: http://localhost:5173
# Backend: http://localhost:8000/docs
# AI Service: http://localhost:5000/status
```

### Git Workflow

**Branch Strategy:**
- Main branch: `main`
- Feature branches: `claude/claude-md-<session-id>`
- **CRITICAL**: Branch names must match session ID for push to succeed

**Common Git Operations:**
```bash
# Create feature branch
git checkout -b claude/claude-md-<session-id>

# Make changes and commit
git add .
git commit -m "feat: descriptive commit message"

# Push to origin (use -u flag)
git push -u origin claude/claude-md-<session-id>

# If push fails due to network, retry with exponential backoff
# Retry sequence: 2s, 4s, 8s, 16s
```

**Commit Message Conventions:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions/modifications
- `chore:` - Maintenance tasks

### Running Services Locally

**Development Mode (with hot-reload):**
```bash
# Full stack
docker-compose -f docker-compose.dev.yml up -d

# Individual services
docker-compose -f docker-compose.dev.yml up frontend
docker-compose -f docker-compose.dev.yml up backend
docker-compose -f docker-compose.dev.yml up ai
```

**Production Mode:**
```bash
docker-compose up -d
```

**Without Docker (manual):**
```bash
# Frontend
cd src/frontend
npm install
npm run dev

# Backend
cd src/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# AI Service
cd src/ai
pip install -r requirements.txt
python app.py
```

### Database Migrations

**Creating a New Migration:**
```bash
# 1. Create migration file with timestamp
cd supabase/migrations
touch $(date +%Y%m%d%H%M%S)_description_of_change.sql

# 2. Write migration SQL
# Example structure:
-- Enable extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create table
CREATE TABLE IF NOT EXISTS new_table (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE new_table ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own records"
  ON new_table FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

-- Create indexes
CREATE INDEX idx_new_table_user_id ON new_table(user_id);

# 3. Apply migration through Supabase dashboard or CLI
# 4. Test migration thoroughly
```

**Important Migration Rules:**
- **NEVER** edit existing migrations
- Always create new migration for schema changes
- Include rollback logic in comments
- Test migrations on development database first
- Document migration purpose in comments

### Testing Workflow

**Frontend Tests:**
```bash
cd src/tests/frontend

# Run unit tests
npm test

# Run with watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run with UI
npm run test:ui

# E2E tests
npm run cypress:open      # Interactive mode
npm run e2e:all          # Headless mode
npm run e2e:user-journey # Specific test suite
```

**Test Development Pattern:**
1. Write test first (TDD approach encouraged)
2. Mock external dependencies (use MSW for API calls)
3. Test user behavior, not implementation
4. Ensure accessibility (use `@testing-library` queries)
5. Run tests before committing

---

## Key Conventions

### Naming Conventions

**Python (Backend/AI Service):**
```python
# Files
chat_service.py            # snake_case
rag_orchestrator.py

# Classes
class ChatService:         # PascalCase
class RAGOrchestrator:

# Functions/Methods
def process_message():     # snake_case
async def get_user():

# Constants
MAX_TOKENS = 2048          # UPPER_SNAKE_CASE
SIMILARITY_THRESHOLD = 0.3

# Private
def _internal_helper():    # leading underscore
_cache = {}
```

**TypeScript (Frontend):**
```typescript
// Files
ChatWindow.tsx             // PascalCase for components
chatService.ts             // camelCase for services/utils

// Components
export const ChatWindow = () => { }  // PascalCase

// Functions
const handleSubmit = () => { }       // camelCase

// Constants
const MAX_MESSAGE_LENGTH = 1000      // UPPER_SNAKE_CASE

// Interfaces/Types
interface ChatMessage { }            // PascalCase
type UserRole = 'admin' | 'user'
```

**Database:**
```sql
-- Tables (snake_case, plural)
CREATE TABLE documents ();
CREATE TABLE chat_sessions ();

-- Columns (snake_case)
user_id UUID
created_at TIMESTAMP

-- Indexes
CREATE INDEX idx_documents_user_id ON documents(user_id);

-- Functions
CREATE FUNCTION update_updated_at_column() RETURNS TRIGGER;
```

### Code Organization Patterns

**Frontend Component Pattern:**
```typescript
// ChatWindow.tsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { chatService } from '@/services/chatService';
import type { Message } from '@/types';

interface ChatWindowProps {
  userId: string;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ userId }) => {
  // 1. Hooks
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);

  // 2. Effects
  useEffect(() => {
    // Load initial messages
  }, []);

  // 3. Event handlers
  const handleSendMessage = async (content: string) => {
    // Implementation
  };

  // 4. Render
  return (
    <div className="chat-window">
      {/* JSX */}
    </div>
  );
};
```

**Backend Service Pattern:**
```python
# chat_service.py
from typing import Optional, List
from app.core.interfaces import IChatService
from app.repositories.interfaces import IMessageRepository

class ChatService(IChatService):
    """Service for handling chat operations."""

    def __init__(
        self,
        message_repo: IMessageRepository,
        rag_service: RAGService
    ):
        """Initialize chat service with dependencies."""
        self.message_repo = message_repo
        self.rag_service = rag_service

    async def process_message(
        self,
        content: str,
        user_id: str,
        history: Optional[List[dict]] = None
    ) -> dict:
        """
        Process a chat message and generate response.

        Args:
            content: User message content
            user_id: User identifier
            history: Optional conversation history

        Returns:
            dict: Response with message and metadata
        """
        try:
            # Implementation
            pass
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise
```

**RAG Configuration Pattern:**
```python
# rag_config.py
from dataclasses import dataclass

@dataclass
class SearchConfig:
    """Configuration for vector search."""
    SIMILARITY_THRESHOLD: float = 0.3
    MAX_CHUNKS_RETRIEVED: int = 15
    HYBRID_SEMANTIC_WEIGHT: float = 0.6
    HYBRID_KEYWORD_WEIGHT: float = 0.4

@dataclass
class LLMConfig:
    """Configuration for LLM behavior."""
    MODEL_NAME: str = "gemini-2.0-flash"
    TEMPERATURE: float = 0.1
    MAX_OUTPUT_TOKENS: int = 2048
```

### Import Organization

**Frontend (TypeScript):**
```typescript
// 1. External libraries
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

// 2. Internal modules (using @ alias)
import { useAuth } from '@/hooks/useAuth';
import { chatService } from '@/services/chatService';
import { Button } from '@/components/ui/Button';

// 3. Types
import type { Message, User } from '@/types';

// 4. Styles (if not using Tailwind exclusively)
import './ChatWindow.css';
```

**Backend (Python):**
```python
# 1. Standard library
import logging
from typing import Optional, List, Dict
from datetime import datetime

# 2. Third-party
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# 3. Local application
from app.core.auth import get_current_user
from app.services.chat_service import ChatService
from app.models.schemas import ChatRequest, ChatResponse

# 4. Logger
logger = logging.getLogger(__name__)
```

### Error Handling Patterns

**Frontend:**
```typescript
// Service layer
export const chatService = {
  async sendMessage(content: string): Promise<Message> {
    try {
      const response = await apiRequest('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ content })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error; // Re-throw for component handling
    }
  }
};

// Component layer
const handleSend = async () => {
  try {
    setLoading(true);
    const message = await chatService.sendMessage(input);
    setMessages(prev => [...prev, message]);
  } catch (error) {
    setError('Failed to send message. Please try again.');
  } finally {
    setLoading(false);
  }
};
```

**Backend:**
```python
# Service layer
class ChatService:
    async def process_message(self, content: str) -> dict:
        try:
            # Business logic
            result = await self._generate_response(content)
            return result
        except RAGServiceError as e:
            logger.error(f"RAG service error: {e}")
            raise ServiceError("Failed to generate response") from e
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            raise

# Route layer
@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service)
):
    try:
        response = await service.process_message(request.content)
        return ChatResponse(**response)
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Unhandled error in chat endpoint")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Logging Standards

**Use structured logging with context:**
```python
# Good
logger.info(
    f"Processing message for user {user_id}: {message[:50]}...",
    extra={
        "user_id": user_id,
        "message_length": len(message),
        "timestamp": datetime.utcnow()
    }
)

# Avoid
print("Processing message")
logger.info("Message received")
```

**Log levels:**
- `DEBUG`: Detailed diagnostic information (disabled in production)
- `INFO`: General informational messages (important events)
- `WARNING`: Warning messages (degraded functionality but still working)
- `ERROR`: Error messages (functionality failed)
- `CRITICAL`: Critical issues (system failure)

### Authentication Patterns

**Frontend:**
```typescript
// Always use Supabase auth
import { supabase } from '@/config/supabase';

// Get current session
const { data: { session } } = await supabase.auth.getSession();

// Make authenticated request
const response = await fetch('/api/endpoint', {
  headers: {
    'Authorization': `Bearer ${session.access_token}`
  }
});
```

**Backend:**
```python
# Use dependency injection for auth
from app.core.auth import get_current_user

@router.get("/protected")
async def protected_route(
    current_user: dict = Depends(get_current_user)
):
    # current_user contains: id, email, role
    return {"user": current_user}

# Check admin status
from app.core.auth import require_admin

@router.delete("/admin/delete")
async def admin_only_route(
    admin_user: dict = Depends(require_admin)
):
    # Only admins can access
    pass
```

---

## Common Tasks

### Adding a New API Endpoint

**1. Define Route (Backend):**
```python
# src/backend/app/api/routes/my_feature.py
from fastapi import APIRouter, Depends
from app.models.schemas import MyRequest, MyResponse
from app.services.my_service import MyService
from app.core.auth import get_current_user

router = APIRouter(prefix="/api/my-feature", tags=["My Feature"])

@router.post("/action", response_model=MyResponse)
async def perform_action(
    request: MyRequest,
    service: MyService = Depends(get_my_service),
    user: dict = Depends(get_current_user)
):
    """Perform a specific action."""
    result = await service.perform_action(request, user["id"])
    return MyResponse(**result)
```

**2. Register Route in App:**
```python
# src/backend/app/core/app.py or main.py
from app.api.routes import my_feature

app.include_router(my_feature.router)
```

**3. Create Service Layer:**
```python
# src/backend/app/services/my_service.py
class MyService:
    async def perform_action(self, request: MyRequest, user_id: str) -> dict:
        # Implement business logic
        return {"result": "success"}
```

**4. Create Frontend Service:**
```typescript
// src/frontend/src/services/myFeatureService.ts
import { supabase } from '@/config/supabase';

export const myFeatureService = {
  async performAction(data: MyRequest): Promise<MyResponse> {
    const { data: { session } } = await supabase.auth.getSession();

    const response = await fetch('/api/my-feature/action', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session.access_token}`
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) throw new Error('Request failed');
    return response.json();
  }
};
```

**5. Use in Component:**
```typescript
import { myFeatureService } from '@/services/myFeatureService';

const handleAction = async () => {
  try {
    const result = await myFeatureService.performAction({ ... });
    console.log('Success:', result);
  } catch (error) {
    console.error('Failed:', error);
  }
};
```

### Adding a New React Component

**1. Create Component File:**
```typescript
// src/frontend/src/components/MyFeature/MyComponent.tsx
import React from 'react';
import { useTranslation } from 'react-i18next';

interface MyComponentProps {
  title: string;
  onAction: () => void;
}

export const MyComponent: React.FC<MyComponentProps> = ({
  title,
  onAction
}) => {
  const { t } = useTranslation();

  return (
    <div className="my-component">
      <h2>{title}</h2>
      <button
        onClick={onAction}
        className="btn-primary"
      >
        {t('common.submit')}
      </button>
    </div>
  );
};
```

**2. Add Translations:**
```json
// src/frontend/src/i18n/locales/en/translation.json
{
  "myFeature": {
    "title": "My Feature",
    "action": "Perform Action"
  }
}

// src/frontend/src/i18n/locales/he/translation.json
{
  "myFeature": {
    "title": "התכונה שלי",
    "action": "בצע פעולה"
  }
}
```

**3. Add to Parent Component:**
```typescript
import { MyComponent } from '@/components/MyFeature/MyComponent';

<MyComponent
  title={t('myFeature.title')}
  onAction={handleAction}
/>
```

### Modifying RAG Configuration

**1. Understand Profile System:**
```python
# src/ai/config/rag_config_profiles.py
RAG_PROFILES = {
    'balanced': {  # Default profile
        'search_config': SearchConfig(
            SIMILARITY_THRESHOLD=0.3,
            MAX_CHUNKS_RETRIEVED=15
        ),
        'llm_config': LLMConfig(
            TEMPERATURE=0.1,
            MAX_OUTPUT_TOKENS=2048
        )
    },
    'fast': {  # Low latency
        # Fewer chunks, faster response
    },
    'quality': {  # High quality
        # More chunks, better quality
    }
}
```

**2. Modify Profile in Supabase:**
```sql
-- Update active profile
UPDATE rag_profiles
SET is_active = FALSE
WHERE is_active = TRUE;

UPDATE rag_profiles
SET is_active = TRUE
WHERE profile_name = 'quality';
```

**3. Or Create Custom Profile:**
```python
# In backend or admin interface
from src.ai.config.rag_config_profiles_supabase import save_profile

custom_profile = {
    'search_config': SearchConfig(
        SIMILARITY_THRESHOLD=0.4,  # More selective
        MAX_CHUNKS_RETRIEVED=10    # Fewer chunks
    ),
    'llm_config': LLMConfig(
        TEMPERATURE=0.2,           # More creative
        MAX_OUTPUT_TOKENS=3000     # Longer responses
    )
}

await save_profile('custom', custom_profile, set_active=True)
```

**4. Profile Changes are Detected Automatically:**
- Backend polls for profile changes every request
- RAG service reloads configuration when changes detected
- No restart required

### Adding Database Schema Changes

**1. Create Migration File:**
```bash
cd supabase/migrations
touch $(date +%Y%m%d%H%M%S)_add_user_preferences.sql
```

**2. Write Migration SQL:**
```sql
-- supabase/migrations/20250623120000_add_user_preferences.sql

-- Create user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  theme VARCHAR(10) DEFAULT 'light',
  language VARCHAR(5) DEFAULT 'he',
  notifications_enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id)
);

-- Enable RLS
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own preferences"
  ON user_preferences FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update own preferences"
  ON user_preferences FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own preferences"
  ON user_preferences FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

-- Create indexes
CREATE INDEX idx_user_preferences_user_id
  ON user_preferences(user_id);

-- Create updated_at trigger
CREATE TRIGGER update_user_preferences_updated_at
  BEFORE UPDATE ON user_preferences
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Add comments
COMMENT ON TABLE user_preferences IS 'User-specific preferences and settings';
COMMENT ON COLUMN user_preferences.theme IS 'UI theme preference (light/dark)';
```

**3. Apply Migration:**
- Through Supabase dashboard
- Or using Supabase CLI: `supabase db push`

**4. Update Repository Layer:**
```python
# src/backend/app/repositories/preferences_repo.py
class PreferencesRepository:
    async def get_preferences(self, user_id: str) -> dict:
        response = await self.client.table('user_preferences') \
            .select('*') \
            .eq('user_id', user_id) \
            .single() \
            .execute()
        return response.data
```

### Updating System Prompts

**1. Centralized Location:**
```python
# src/ai/config/system_prompts.py

def get_main_system_prompt() -> str:
    """Get the main system prompt for chat."""
    return """
    אתה עוזר אקדמי חכם של מכללת אפקה להנדסה.
    תפקידך לסייע לסטודנטים במידע אקדמי מדויק ומועיל.

    Guidelines:
    1. Always respond in the user's language (Hebrew or English)
    2. Provide accurate, concise information
    3. Reference relevant college policies
    4. Be helpful and professional
    """

def get_fallback_prompt() -> str:
    """Fallback prompt when main is unavailable."""
    return "You are a helpful academic assistant."
```

**2. Or Store in Database:**
```sql
-- Insert into system_prompts table
INSERT INTO system_prompts (name, prompt_text, is_active)
VALUES (
  'academic_assistant_v2',
  'Your comprehensive prompt here...',
  TRUE
);

-- Deactivate old prompts
UPDATE system_prompts SET is_active = FALSE
WHERE name != 'academic_assistant_v2';
```

**3. Backend Loads Dynamically:**
```python
# Backend automatically uses active prompt from database
# Falls back to system_prompts.py if database unavailable
```

---

## Testing Guidelines

### Frontend Testing Patterns

**Unit Testing with Vitest:**
```typescript
// src/tests/frontend/unit-integration/services/chat/chatService.test.ts
import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import { chatService } from '@/services/chatService';

// Setup MSW server
const server = setupServer(
  http.post('/api/chat', () => {
    return HttpResponse.json({
      message: 'Test response',
      timestamp: new Date().toISOString()
    });
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('chatService', () => {
  it('sends message successfully', async () => {
    const response = await chatService.sendMessage('Hello');

    expect(response).toHaveProperty('message');
    expect(response.message).toBe('Test response');
  });

  it('handles errors gracefully', async () => {
    server.use(
      http.post('/api/chat', () => {
        return new HttpResponse(null, { status: 500 });
      })
    );

    await expect(chatService.sendMessage('Hello'))
      .rejects.toThrow();
  });
});
```

**Component Testing:**
```typescript
// src/tests/frontend/unit-integration/components/ChatWindow.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatWindow } from '@/components/Chat/ChatWindow';

describe('ChatWindow', () => {
  it('renders chat interface', () => {
    render(<ChatWindow userId="test-user" />);

    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  it('sends message on submit', async () => {
    const user = userEvent.setup();
    render(<ChatWindow userId="test-user" />);

    const input = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /send/i });

    await user.type(input, 'Hello');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText('Hello')).toBeInTheDocument();
    });
  });
});
```

**E2E Testing with Cypress:**
```javascript
// src/tests/frontend/e2e/e2e/complete-user-journey.cy.js
describe('Complete User Journey', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5173');
  });

  it('allows user to register, login, and chat', () => {
    // Register
    cy.get('[data-testid="register-button"]').click();
    cy.get('[data-testid="email-input"]').type('test@example.com');
    cy.get('[data-testid="password-input"]').type('SecurePass123!');
    cy.get('[data-testid="submit-button"]').click();

    // Should redirect to chat
    cy.url().should('include', '/chat');

    // Send message
    cy.get('[data-testid="message-input"]').type('Hello, bot!');
    cy.get('[data-testid="send-button"]').click();

    // Verify response
    cy.contains('Hello, bot!').should('be.visible');
    cy.contains(/.*/, { timeout: 10000 }).should('exist'); // Bot response
  });
});
```

### Backend Testing Patterns

**Service Testing:**
```python
# src/tests/backend/test_chat_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.chat_service import ChatService

@pytest.fixture
def mock_rag_service():
    rag = AsyncMock()
    rag.query.return_value = {"answer": "Test answer", "sources": []}
    return rag

@pytest.fixture
def chat_service(mock_rag_service):
    return ChatService(rag_service=mock_rag_service)

@pytest.mark.asyncio
async def test_process_message(chat_service):
    result = await chat_service.process_message(
        content="Test question",
        user_id="test-user"
    )

    assert result["answer"] == "Test answer"
    assert "sources" in result

@pytest.mark.asyncio
async def test_handle_rag_error(chat_service, mock_rag_service):
    mock_rag_service.query.side_effect = Exception("RAG error")

    with pytest.raises(ServiceError):
        await chat_service.process_message(
            content="Test question",
            user_id="test-user"
        )
```

### Test Organization Best Practices

1. **Mirror source structure**: Test files should mirror the source code structure
2. **One test file per module**: `chatService.ts` → `chatService.test.ts`
3. **Descriptive test names**: Use full sentences describing behavior
4. **Arrange-Act-Assert**: Structure tests clearly
5. **Mock external dependencies**: Always mock API calls, database, external services
6. **Test user behavior**: Test what users do, not implementation details

---

## Security Considerations

### Authentication & Authorization

**NEVER bypass authentication:**
```typescript
// ❌ Bad - Direct API call without auth
fetch('/api/admin/delete', { method: 'DELETE' });

// ✅ Good - Always include auth token
const { data: { session } } = await supabase.auth.getSession();
fetch('/api/admin/delete', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${session.access_token}`
  }
});
```

**Always verify admin status:**
```python
# ❌ Bad - Trust client-side role
@router.delete("/admin/delete")
async def delete_resource(user: dict = Depends(get_current_user)):
    # Anyone authenticated can access!
    pass

# ✅ Good - Verify admin in database
@router.delete("/admin/delete")
async def delete_resource(admin: dict = Depends(require_admin)):
    # Only verified admins can access
    pass
```

### Input Validation

**Always validate user input:**
```python
# ✅ Use Pydantic for validation
from pydantic import BaseModel, Field, validator

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    user_id: str = Field(..., regex=r'^[0-9a-f-]{36}$')

    @validator('message')
    def sanitize_message(cls, v):
        # Remove potentially dangerous content
        return v.strip()
```

### SQL Injection Prevention

**Use parameterized queries:**
```python
# ❌ Bad - SQL injection vulnerability
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✅ Good - Parameterized query
query = "SELECT * FROM users WHERE email = %s"
result = await conn.fetch(query, email)

# ✅ Better - Use ORM/query builder
result = await supabase.table('users') \
    .select('*') \
    .eq('email', email) \
    .execute()
```

### API Key Management

**Never hardcode API keys:**
```python
# ❌ Bad
GEMINI_API_KEY = "AIzaSyAbc123..."

# ✅ Good - Use environment variables
from app.config.settings import settings
api_key = settings.GEMINI_API_KEY

# ✅ Better - Use key rotation system
from src.ai.core.database_key_manager import get_key_manager
key_manager = get_key_manager()
api_key = await key_manager.get_valid_key()
```

**Implement key rotation:**
```python
# System automatically rotates keys based on usage
# Keys tracked in api_keys and api_key_usage tables
# Daily limits: 1500 requests
# Per-minute limits: 15 requests
```

### Row Level Security (RLS)

**Always enable RLS on tables:**
```sql
-- Enable RLS
ALTER TABLE my_table ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users see own data only"
  ON my_table FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users modify own data only"
  ON my_table FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

### XSS Prevention

**Sanitize user content:**
```typescript
// React automatically escapes JSX content
// But be careful with dangerouslySetInnerHTML

// ❌ Bad - XSS vulnerability
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// ✅ Good - Sanitize first
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{
  __html: DOMPurify.sanitize(userInput)
}} />

// ✅ Better - Use text content
<div>{userInput}</div>
```

### CORS Configuration

**Properly configure CORS:**
```python
# src/backend/app/core/app.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Dev frontend
        "http://localhost:80",     # Prod frontend
        # Add production domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting

**Implement rate limiting:**
```python
# Backend has rate limiting middleware
# Default: 500 requests per window
# Configure via API_RATE_LIMIT env var

# For specific endpoints, add stricter limits:
from app.middleware.rate_limit import RateLimitMiddleware

@router.post("/expensive-operation")
@rate_limit(requests=10, window=60)  # 10 req/min
async def expensive_operation():
    pass
```

---

## Troubleshooting

### Common Issues & Solutions

#### Frontend Issues

**Issue: Vite HMR not working**
```bash
# Solution 1: Clear Vite cache
rm -rf node_modules/.vite
npm run dev

# Solution 2: Check vite.config.ts
# Ensure server.watch is configured correctly

# Solution 3: Docker volume issues
# Recreate containers
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

**Issue: Supabase auth errors**
```typescript
// Check 1: Verify environment variables
console.log('Supabase URL:', import.meta.env.VITE_SUPABASE_URL);

// Check 2: Verify session
const { data: { session }, error } = await supabase.auth.getSession();
if (error) console.error('Session error:', error);

// Check 3: Check RLS policies in Supabase dashboard
```

**Issue: i18n translations not loading**
```typescript
// Check 1: Verify translation files exist
// src/frontend/src/i18n/locales/he/translation.json
// src/frontend/src/i18n/locales/en/translation.json

// Check 2: Check i18n initialization
// src/frontend/src/i18n/config.ts

// Check 3: Force language change
import { i18n } from '@/i18n/config';
i18n.changeLanguage('he');
```

#### Backend Issues

**Issue: Import errors from AI service**
```python
# Problem: Backend can't import from src.ai
# Solution: Ensure PYTHONPATH includes project root

# In Docker: Already configured
# Local dev: Add to environment
export PYTHONPATH="${PYTHONPATH}:/home/user/Afeka_ChatBot"

# Or use relative imports with fallback
try:
    from ....ai.services.rag_service import RAGService
except ImportError:
    from src.ai.services.rag_service import RAGService
```

**Issue: Database connection errors**
```python
# Check 1: Verify Supabase credentials
from app.config.settings import settings
print(f"Supabase URL: {settings.SUPABASE_URL}")

# Check 2: Test connection
from app.repositories.supabase_repo import get_supabase_client
client = get_supabase_client()
response = client.table('users').select('count').execute()
print(f"Connection test: {response.count}")

# Check 3: Check RLS policies (might block service role)
```

**Issue: RAG responses are low quality**
```python
# Solution 1: Check active RAG profile
from src.ai.config.current_profile_supabase import get_active_profile
profile = await get_active_profile()
print(f"Active profile: {profile}")

# Solution 2: Adjust similarity threshold
# Lower threshold = more chunks retrieved
# In Supabase: UPDATE rag_profiles SET search_config = ...

# Solution 3: Verify embeddings are generated
# Check document_embeddings table
SELECT COUNT(*) FROM document_embeddings;

# Solution 4: Test RAG directly
from src.ai.services.rag_service import RAGService
rag = RAGService(profile='quality')
result = await rag.query("test question")
```

**Issue: Streaming responses not working**
```python
# Check 1: Verify SSE headers
from fastapi.responses import StreamingResponse

async def stream():
    yield "data: test\n\n"

return StreamingResponse(
    stream(),
    media_type="text/event-stream",
    headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    }
)

# Check 2: Check frontend SSE handling
const eventSource = new EventSource('/api/chat/stream');
eventSource.onmessage = (event) => {
    console.log('Received:', event.data);
};
```

#### AI Service Issues

**Issue: API key exhausted**
```python
# Check key usage
from src.ai.core.database_key_manager import get_key_manager
manager = get_key_manager()
status = await manager.get_all_keys_status()
print(status)

# Add new key
await manager.add_key("new-gemini-api-key")

# Check rate limits
SELECT * FROM api_key_usage
WHERE date = CURRENT_DATE
ORDER BY minute_requests DESC;
```

**Issue: Document processing stuck**
```python
# Check background processor status
# Look for documents with status = 'processing'
SELECT * FROM documents WHERE status = 'processing';

# Manually trigger processing
from src.ai.scripts.process_document import process_single_document
await process_single_document(document_id)

# Check for errors in logs
# Backend logs should show document processor activity
```

#### Database Issues

**Issue: Migration failed**
```sql
-- Check migration status
SELECT * FROM supabase_migrations.schema_migrations
ORDER BY version DESC
LIMIT 10;

-- Rollback manually if needed
-- (Implement rollback logic in migration comments)

-- Re-run migration
-- Through Supabase dashboard or CLI
```

**Issue: RLS blocking queries**
```sql
-- Temporarily disable RLS for testing (dev only!)
ALTER TABLE my_table DISABLE ROW LEVEL SECURITY;

-- Check which policies are active
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE tablename = 'my_table';

-- Test query as specific user
SET request.jwt.claim.sub = 'user-uuid-here';
SELECT * FROM my_table;
```

**Issue: Slow queries**
```sql
-- Check for missing indexes
EXPLAIN ANALYZE
SELECT * FROM documents WHERE user_id = 'xxx';

-- If "Seq Scan" appears, add index:
CREATE INDEX idx_documents_user_id ON documents(user_id);

-- Check query plan
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM your_query;
```

### Performance Optimization

**Frontend Optimization:**
```typescript
// 1. Lazy load routes
const Dashboard = lazy(() => import('@/components/Dashboard/Dashboard'));

// 2. Memoize expensive computations
const processedData = useMemo(
  () => expensiveComputation(data),
  [data]
);

// 3. Debounce user input
const debouncedSearch = useMemo(
  () => debounce((query) => performSearch(query), 300),
  []
);

// 4. Virtualize long lists
import { FixedSizeList } from 'react-window';
```

**Backend Optimization:**
```python
# 1. Use async/await consistently
async def get_data():
    results = await asyncio.gather(
        fetch_user(),
        fetch_documents(),
        fetch_analytics()
    )
    return results

# 2. Implement caching
from functools import lru_cache

@lru_cache(maxsize=128)
def get_config():
    return load_config()

# 3. Batch database queries
# Use Supabase's select with multiple relations
response = client.table('documents') \
    .select('*, user:users(*), embeddings:document_embeddings(*)') \
    .execute()

# 4. Use database indexes (see migrations)
```

**RAG Optimization:**
```python
# 1. Use appropriate profile
# For speed: 'fast' profile (fewer chunks, lower quality)
# For quality: 'quality' profile (more chunks, better results)

# 2. Tune similarity threshold
# Higher = fewer, more relevant chunks
# Lower = more chunks, potentially less relevant

# 3. Implement semantic caching
# Cache frequent queries and their responses

# 4. Optimize embedding generation
# Use batch processing for multiple documents
```

### Debugging Tools

**Frontend:**
```bash
# React DevTools - Browser extension
# Redux DevTools - If using Redux (currently using Context)

# Vite inspector
npm install -D vite-plugin-inspect
# Add to vite.config.ts

# Bundle analyzer
npm install -D rollup-plugin-visualizer
npm run build -- --analyze
```

**Backend:**
```bash
# FastAPI interactive docs
# http://localhost:8000/docs

# Python debugger
import pdb; pdb.set_trace()

# Or use ipdb
pip install ipdb
import ipdb; ipdb.set_trace()

# Logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Database:**
```bash
# Supabase Studio (dashboard)
# https://app.supabase.com

# Direct PostgreSQL connection
psql postgresql://postgres:[password]@[host]:5432/postgres

# Query performance
EXPLAIN ANALYZE your_query;
```

---

## Best Practices Summary

### For AI Assistants Working on This Codebase

1. **Read Before Writing**: Always read existing code before suggesting changes
2. **Follow Patterns**: Use established patterns in the codebase
3. **Test Changes**: Write or update tests for new features
4. **Document Decisions**: Add comments explaining non-obvious logic
5. **Security First**: Never bypass authentication or validation
6. **Type Safety**: Use TypeScript types and Python type hints
7. **Error Handling**: Always handle errors gracefully with user-friendly messages
8. **Logging**: Add appropriate logging for debugging
9. **Performance**: Consider performance impact of changes
10. **Internationalization**: Support both Hebrew and English

### Code Quality Checklist

Before committing code, verify:

- [ ] Code follows naming conventions
- [ ] All imports are organized properly
- [ ] Error handling is implemented
- [ ] Logging is added for important operations
- [ ] Types/interfaces are defined
- [ ] Tests are written/updated
- [ ] Documentation is updated
- [ ] No hardcoded credentials or API keys
- [ ] Authentication is properly implemented
- [ ] RLS policies are appropriate (for DB changes)
- [ ] Translation keys are added (for UI changes)
- [ ] No console.log/print statements in production code
- [ ] Code is formatted consistently

### When in Doubt

1. **Check existing code**: Look for similar implementations
2. **Read the docs**: Refer to this CLAUDE.md and README.md
3. **Test thoroughly**: Use both unit and E2E tests
4. **Ask for clarification**: If requirements are unclear, ask the user
5. **Start small**: Make incremental changes rather than large rewrites

---

## Quick Reference

### Important File Paths

| Purpose | Path |
|---------|------|
| Frontend Entry | `src/frontend/src/main.tsx` |
| Backend Entry | `src/backend/main.py` |
| API Routes | `src/backend/app/api/routes/` |
| Frontend Services | `src/frontend/src/services/` |
| React Components | `src/frontend/src/components/` |
| RAG Configuration | `src/ai/config/rag_config.py` |
| System Prompts | `src/ai/config/system_prompts.py` |
| Database Migrations | `supabase/migrations/` |
| Frontend Tests | `src/tests/frontend/` |
| Environment Template | `.env.example` |

### Key Commands

```bash
# Development
docker-compose -f docker-compose.dev.yml up -d

# Production
docker-compose up -d

# Frontend tests
cd src/tests/frontend && npm test

# Backend tests
cd src/tests/backend && pytest

# Database migration
cd supabase/migrations && touch $(date +%Y%m%d%H%M%S)_description.sql

# Git workflow
git checkout -b claude/claude-md-<session-id>
git add .
git commit -m "feat: description"
git push -u origin claude/claude-md-<session-id>
```

### Environment Variables Priority List

**Must Have:**
- `SUPABASE_URL`
- `SUPABASE_KEY` / `SUPABASE_SERVICE_KEY`
- `SUPABASE_ANON_KEY`
- `GEMINI_API_KEY`
- `VITE_SUPABASE_URL` (frontend)
- `VITE_SUPABASE_ANON_KEY` (frontend)

**Development:**
- `NODE_ENV=development`
- `DEBUG=True`
- `VITE_BACKEND_URL=http://localhost:8000`

### Common Supabase Tables

| Table | Purpose |
|-------|---------|
| `users` | User accounts |
| `admins` | Admin users |
| `documents` | Document metadata |
| `document_embeddings` | Vector embeddings |
| `document_chunks` | Text chunks for RAG |
| `chat_sessions` | Chat session metadata |
| `messages` | Chat message history |
| `api_keys` | Gemini API keys |
| `api_key_usage` | API usage tracking |
| `system_prompts` | System prompt management |
| `rag_profiles` | RAG configuration profiles |

---

## Additional Resources

- **Project README**: `README.md` - High-level overview and setup
- **Security Policy**: `SECURITY.md` - Security guidelines
- **License**: `LICENSE` - MIT License
- **Supabase Docs**: https://supabase.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev
- **LangChain Docs**: https://python.langchain.com
- **Gemini API**: https://ai.google.dev/docs

---

## Document Version

**Version**: 1.0
**Last Updated**: 2025-01-23
**Current Branch**: `claude/claude-md-mic3r3nqyp1ivzer-01Fxp1wZFRASWqTsCqZBifVV`
**Maintainers**: Niv Buskila, Amitay Manor, Omri Roter

---

**This document is a living guide. When making significant architectural changes, update this file accordingly.**
