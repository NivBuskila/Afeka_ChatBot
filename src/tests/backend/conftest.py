"""
pytest configuration and fixtures for backend tests
"""
import asyncio
import pytest
import httpx
import os
import sys
from typing import AsyncGenerator, Dict, Any
from fastapi.testclient import TestClient
from pathlib import Path

# Add project root to Python path
# מתוך src/tests/backend נצטרך לעלות 3 רמות למעלה כדי להגיע לשורש הפרויקט
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# הוסף גם את תיקיית src ל-path
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET"] = "test-jwt-secret-key-for-testing-only"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"
os.environ["AI_SERVICE_URL"] = "http://localhost:5000"
os.environ["INTERNAL_API_KEY"] = "test-internal-api-key"

# Import after setting environment variables and paths
try:
    from backend.main import app
except ImportError:
    # אם זה לא עובד, נסה נתיב יחסי
    try:
        sys.path.insert(0, str(project_root / "src" / "backend"))
        from backend.main import app
    except ImportError:
        # אם כלום לא עובד, צור mock app
        from fastapi import FastAPI
        app = FastAPI()
        print("⚠️ Warning: Using mock FastAPI app - could not import backend.main")

@pytest.fixture(scope="session")
def client():
    """Create test client for the entire test session"""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="session")
async def async_client():
    """Create async test client for the entire test session"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def dev_token():
    """Return dev token for testing"""
    return "dev-token"

@pytest.fixture
def valid_jwt_token():
    """Generate a valid JWT token for testing"""
    import jwt
    payload = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "role": "user",
        "exp": 9999999999  # Far future expiry
    }
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm="HS256")

@pytest.fixture
def expired_jwt_token():
    """Generate an expired JWT token for testing"""
    import jwt
    payload = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "role": "user",
        "exp": 1000000000  # Past expiry
    }
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm="HS256")

@pytest.fixture
def invalid_jwt_token():
    """Generate an invalid JWT token for testing"""
    return "invalid.jwt.token"

@pytest.fixture
def auth_headers(valid_jwt_token):
    """Return authorization headers with valid token"""
    return {"Authorization": f"Bearer {valid_jwt_token}"}

@pytest.fixture
def dev_auth_headers(dev_token):
    """Return authorization headers with dev token"""
    return {"Authorization": f"Bearer {dev_token}"}

@pytest.fixture
def expired_auth_headers(expired_jwt_token):
    """Return authorization headers with expired token"""
    return {"Authorization": f"Bearer {expired_jwt_token}"}

@pytest.fixture
def invalid_auth_headers(invalid_jwt_token):
    """Return authorization headers with invalid token"""
    return {"Authorization": f"Bearer {invalid_jwt_token}"}

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "password": "Test123!@#",
        "role": "user"
    }

@pytest.fixture
def sample_chat_session():
    """Sample chat session data"""
    return {
        "id": "test-session-id",
        "user_id": "test-user-id",
        "title": "Test Chat Session",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def sample_message():
    """Sample message data"""
    return {
        "id": "test-message-id",
        "session_id": "test-session-id",
        "content": "Hello, this is a test message",
        "role": "user",
        "created_at": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def sample_document():
    """Sample document data"""
    return {
        "title": "Test Document",
        "content": "This is a test document with some content for testing purposes.",
        "category": "regulations",
        "tags": ["test", "sample"]
    }

@pytest.fixture
def api_key_headers():
    """Return API key headers for internal endpoints"""
    return {"X-API-Key": os.environ["INTERNAL_API_KEY"]}

@pytest.fixture
def rate_limit_headers():
    """Headers to simulate different IPs for rate limiting tests"""
    return {"X-Forwarded-For": "192.168.1.100"}

# Mock fixtures for external services
@pytest.fixture
def mock_supabase_client(mocker):
    """Mock Supabase client"""
    mock_client = mocker.MagicMock()
    mock_table = mocker.MagicMock()
    mock_client.table.return_value = mock_table
    mock_client.auth = mocker.MagicMock()
    return mock_client

@pytest.fixture
def mock_ai_service_response():
    """Mock AI service response"""
    return {
        "response": "This is a mock AI response",
        "sources": ["document1.pdf", "document2.pdf"],
        "confidence": 0.85
    }

# Event loop fixture for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()