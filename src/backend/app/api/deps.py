import logging
from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from supabase import create_client, Client

from ..config.settings import settings
from ..core.interfaces import IDocumentService, IChatService, IChatSessionService, IMessageService, IDocumentRepository
from ..services.document_service import DocumentService
from ..services.chat_service import ChatService
from ..services.chat_session_service import ChatSessionService
from ..services.message_service import MessageService
from ..repositories.supabase_repo import SupabaseDocumentRepository
from ..repositories.mock_repo import MockDocumentRepository
from ..repositories.chat_session_repo import SupabaseChatSessionRepository
from ..repositories.message_repo import SupabaseMessageRepository

logger = logging.getLogger(__name__)

# --- API Key Security ---
api_key_header = APIKeyHeader(name=settings.API_KEY_NAME, auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verify the API key."""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API Key",
            headers={"WWW-Authenticate": "APIKey"}
        )
    if api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "APIKey"}
        )
    return api_key

# --- Supabase Client ---
_supabase_client = None

async def get_supabase_client() -> Client:
    """Get or create a Supabase client singleton."""
    global _supabase_client
    
    if _supabase_client is None:
        if not settings.SUPABASE_KEY or not settings.SUPABASE_URL:
            logger.error("Supabase URL or Key not configured")
            raise HTTPException(
                status_code=503, 
                detail="Database connection not configured"
            )
            
        try:
            _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise HTTPException(
                status_code=503, 
                detail="Failed to connect to database"
            )
    
    return _supabase_client

# --- Repository Dependency ---
async def get_document_repository() -> IDocumentRepository:
    """Get document repository (with fallback to mock)."""
    try:
        client = await get_supabase_client()
        return SupabaseDocumentRepository(client)
    except HTTPException:
        logger.warning("Falling back to mock document repository")
        return MockDocumentRepository()

# --- Service Dependencies ---
def get_chat_service() -> IChatService:
    """Get chat service instance."""
    return ChatService()

async def get_document_service() -> IDocumentService:
    """Get document service instance with repository dependency."""
    repository = await get_document_repository()
    return DocumentService(repository)

async def get_chat_session_service() -> IChatSessionService:
    """Get chat session service instance with repository dependency."""
    client = await get_supabase_client()
    repository = SupabaseChatSessionRepository(client)
    return ChatSessionService(repository)

async def get_message_service() -> IMessageService:
    """Get message service instance with repository dependency."""
    client = await get_supabase_client()
    repository = SupabaseMessageRepository(client)
    return MessageService(repository)