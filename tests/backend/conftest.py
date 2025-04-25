import pytest
import sys
import os
from fastapi.testclient import TestClient
import json
from unittest.mock import MagicMock, patch

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/backend')))

# Import the FastAPI app
from main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def mock_supabase(monkeypatch):
    """Create a mock Supabase client for testing"""
    # Create a mock class with the methods we need
    mock_supabase = MagicMock()
    
    # Set up table method and chain methods
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Simulate table.select().execute() returning empty data
    mock_select = MagicMock()
    mock_table.select.return_value = mock_select
    mock_select.execute.return_value = {"data": []}
    
    # Simulate table.insert().execute() returning success
    mock_insert = MagicMock()
    mock_table.insert.return_value = mock_insert
    mock_insert.execute.return_value = {"status": 201, "data": [{"id": "test-id"}]}
    
    # Apply the mock to the app's supabase_client
    with patch('main.supabase_client', mock_supabase):
        yield mock_supabase

@pytest.fixture
def mock_ai_service(monkeypatch):
    """Create a mock for the AI service"""
    async def mock_post(*args, **kwargs):
        # Create a mock response object
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "This is a mock response from the AI service"
        }
        return mock_response
    
    # Patch the httpx.AsyncClient.post method
    with patch('httpx.AsyncClient.post', side_effect=mock_post):
        yield

@pytest.fixture
def sample_document():
    """Return a sample document for testing"""
    return {
        "title": "Test Document",
        "content": "This is a test document for testing purposes.",
        "category": "Test",
        "tags": ["test", "sample"]
    }

@pytest.fixture
def sample_chat_request():
    """Return a sample chat request for testing"""
    return {
        "message": "Hello, this is a test message",
        "user_id": "test-user-id"
    }

@pytest.fixture
def authenticated_client(client):
    """Create an authenticated test client for protected endpoints"""
    # This is a placeholder - adjust based on your actual authentication mechanism
    # For example, you might create a mock JWT token and add it to headers
    
    # Create a mock token
    mock_token = "test-auth-token"
    
    # Create a client with auth headers
    client.headers.update({"Authorization": f"Bearer {mock_token}"})
    
    return client

@pytest.fixture
def sample_user():
    """Return a sample user for testing"""
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "name": "Test User"
    }

@pytest.fixture
def sample_chat_history():
    """Return sample chat history for testing"""
    return [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there! How can I help you?"}
    ] 