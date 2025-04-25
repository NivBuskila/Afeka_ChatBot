import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock, AsyncMock

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src/backend')))

# Import the FastAPI app
from main import app
from fastapi.testclient import TestClient

# Create a test client
client = TestClient(app)

@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client for testing proxy endpoints"""
    mock_supabase = MagicMock()
    
    # Mock for chat sessions
    mock_supabase.table().select().execute.return_value = {
        "data": [
            {
                "id": "session-1",
                "user_id": "test-user",
                "title": "Chat about regulations",
                "created_at": "2023-01-01T12:00:00Z"
            },
            {
                "id": "session-2",
                "user_id": "test-user",
                "title": "Questions about exams",
                "created_at": "2023-01-02T12:00:00Z"
            }
        ]
    }
    
    # Mock for messages
    mock_supabase.table().insert().execute.return_value = {
        "status": 201,
        "data": [{"id": "msg-123"}]
    }
    
    # Apply the mock to the app's supabase_client
    with patch('main.supabase_client', mock_supabase):
        yield mock_supabase

def test_proxy_get_chat_sessions(mock_supabase):
    """Test proxy endpoint for getting chat sessions"""
    response = client.get("/api/proxy/chat_sessions?user_id=test-user")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == "session-1"
    assert data[1]["title"] == "Questions about exams"

def test_proxy_get_chat_session(mock_supabase):
    """Test proxy endpoint for getting a specific chat session"""
    # Mock for a specific chat session
    mock_supabase.table().select().single().execute.return_value = {
        "data": {
            "id": "session-1",
            "user_id": "test-user",
            "title": "Chat about regulations",
            "created_at": "2023-01-01T12:00:00Z"
        }
    }
    
    response = client.get("/api/proxy/chat_sessions/session-1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "session-1"
    assert data["title"] == "Chat about regulations"

def test_proxy_create_chat_session(mock_supabase):
    """Test proxy endpoint for creating a chat session"""
    new_session = {
        "user_id": "test-user",
        "title": "New Chat Session"
    }
    
    response = client.post("/api/proxy/chat_sessions", json=new_session)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["id"] == "msg-123"

def test_proxy_create_message(mock_supabase):
    """Test proxy endpoint for creating a message"""
    new_message = {
        "session_id": "session-1",
        "role": "user",
        "content": "Hello, this is a test message",
        "user_id": "test-user"
    }
    
    response = client.post("/api/proxy/messages", json=new_message)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["id"] == "msg-123"

def test_proxy_get_documents(mock_supabase):
    """Test proxy endpoint for getting documents"""
    # Mock for documents
    mock_supabase.table().select().execute.return_value = {
        "data": [
            {
                "id": 1,
                "title": "Academic Regulations",
                "content": "Content of regulations...",
                "category": "Academic"
            },
            {
                "id": 2,
                "title": "Student Guidelines",
                "content": "Content of guidelines...",
                "category": "Student"
            }
        ]
    }
    
    response = client.get("/api/proxy/documents")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Academic Regulations"
    assert data[1]["id"] == 2

def test_proxy_get_document(mock_supabase):
    """Test proxy endpoint for getting a specific document"""
    # Mock for a specific document
    mock_supabase.table().select().single().execute.return_value = {
        "data": {
            "id": 1,
            "title": "Academic Regulations",
            "content": "Content of regulations...",
            "category": "Academic"
        }
    }
    
    response = client.get("/api/proxy/documents/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Academic Regulations"

def test_proxy_update_chat_session(mock_supabase):
    """Test proxy endpoint for updating a chat session"""
    # Mock for update
    mock_supabase.table().update().eq().execute.return_value = {
        "status": 200,
        "data": [{
            "id": "session-1",
            "title": "Updated Title",
            "user_id": "test-user"
        }]
    }
    
    update_data = {
        "title": "Updated Title"
    }
    
    response = client.patch("/api/proxy/chat_sessions/session-1", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title" 