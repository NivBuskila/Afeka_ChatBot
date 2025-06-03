import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from dotenv import load_dotenv
from supabase import create_client, Client

# Assuming your RAGService and DocumentProcessor are structured as previously discussed
# You might need to adjust import paths based on your project structure
from src.backend.app.core.rag_service import RAGService
from src.backend.services.document_processor import DocumentProcessor # Example path, adjust as needed

# Load environment variables from .env file for testing convenience
# Ensure your .env file (or test-specific .env) has SUPABASE_URL and SUPABASE_KEY
load_dotenv()

@pytest.fixture(scope="session")
def supabase_url() -> str:
    url = os.getenv("SUPABASE_URL")
    if not url:
        pytest.fail("Missing SUPABASE_URL environment variable for tests.")
    return url

@pytest.fixture(scope="session")
def supabase_key() -> str:
    # Using service key for tests is common for backend operations, adjust if anon key is needed for specific tests
    key = os.getenv("SUPABASE_KEY") # Or SUPABASE_SERVICE_KEY based on your .env
    if not key:
        pytest.fail("Missing SUPABASE_KEY (or SUPABASE_SERVICE_KEY) environment variable for tests.")
    return key

@pytest.fixture(scope="session") # Session scope if client can be reused across tests
def supabase_client_fixture(supabase_url, supabase_key) -> Client:
    """Pytest fixture for creating a Supabase client instance for tests."""
    try:
        client = create_client(supabase_url, supabase_key)
        # You might want to add a quick check here to ensure the client is functional
        # For example, trying to fetch a non-existent item or checking service status if API allows
        logger.info("Supabase client fixture created successfully.")
        return client
    except Exception as e:
        pytest.fail(f"Failed to create Supabase client fixture: {e}")

@pytest.fixture(scope="module") # Module scope, or function if RAGService needs fresh state per test
def document_processor_fixture() -> DocumentProcessor:
    """Fixture for DocumentProcessor. This is a basic setup.
       Ensures necessary environment variables are set.
    """
    try:
        # Ensure GEMINI_API_KEY is available
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("Missing GEMINI_API_KEY for DocumentProcessor fixture. Skipping tests requiring it.")
        
        # Ensure Supabase URL and Key are available as DocumentProcessor initializes its own client
        supabase_url_env = os.getenv("SUPABASE_URL")
        supabase_key_env = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
        if not supabase_url_env or not supabase_key_env:
             pytest.skip("Missing SUPABASE_URL or SUPABASE_KEY/SUPABASE_SERVICE_KEY for DocumentProcessor fixture. Skipping tests requiring it.")

        processor = DocumentProcessor() # Initialize without arguments
        logger.info("DocumentProcessor fixture created.")
        return processor
    except Exception as e:
        pytest.fail(f"Failed to create DocumentProcessor fixture: {e}")

@pytest.fixture(scope="module") # Or function scope depending on RAGService state management
async def rag_service_fixture(document_processor_fixture: DocumentProcessor) -> RAGService:
    """Pytest fixture for creating a RAGService instance for tests."""
    # RAGService is initialized with the DocumentProcessor fixture.
    # Environment variables for RAGService (ENABLE_RERANK, RERANK_THREADS, etc.)
    # will be picked up automatically by its __init__ method.
    # Ensure GEMINI_API_KEY is set for the call_llm_placeholder used by RAGService.
    try:
        if not os.getenv("GEMINI_API_KEY"):
             pytest.skip("Missing GEMINI_API_KEY for RAGService fixture (used by LLM). Skipping tests requiring it.")

        service = RAGService(
            doc_processor=document_processor_fixture,
            # RAGService will pick up other configs from env vars (e.g., reranking settings)
        )
        # If RAGService has an async initialization part (e.g., loading models explicitly)
        # await service.initialize_models() # Example, if needed
        logger.info("RAGService fixture created.")
        return service
    except Exception as e:
        pytest.fail(f"Failed to create RAGService fixture: {e}")

# Add a logger for fixture creation info, if not already configured project-wide
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "DEBUG").upper()) 