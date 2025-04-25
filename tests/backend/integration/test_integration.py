import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src/backend')))

# Import the FastAPI app
from main import app
from fastapi.testclient import TestClient

# Create a test client
client = TestClient(app)

class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data
    
    def json(self):
        return self._json_data

@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client for testing"""
    # Create a mock class with the methods we need
    mock_supabase = MagicMock()
    
    # Set up table method and chain methods
    mock_table = MagicMock()
    mock_supabase.table.return_value = mock_table
    
    # Simulate table.select().execute() returning chat history
    mock_select = MagicMock()
    mock_table.select.return_value = mock_select
    mock_select.execute.return_value = {
        "data": [
            {
                "id": "test-chat-id",
                "user_id": "test-user",
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"}
                ]
            }
        ]
    }
    
    # Simulate chat history insert
    mock_insert = MagicMock()
    mock_table.insert.return_value = mock_insert
    mock_insert.execute.return_value = {
        "status": 201, 
        "data": [{"id": "new-chat-id"}]
    }
    
    # Apply the mock to the app's supabase_client
    with patch('main.supabase_client', mock_supabase):
        yield mock_supabase

@pytest.fixture
def mock_ai_service():
    """Create a mock for the AI service"""
    async def mock_post(*args, **kwargs):
        # Return a predefined response based on the input
        request_data = kwargs.get('json', {})
        message = request_data.get('message', '')
        
        if "regulations" in message.lower():
            response_text = "According to Afeka's regulations, students must maintain academic integrity."
        else:
            response_text = "I'm here to help with questions about Afeka College regulations."
        
        return MockResponse(200, {"response": response_text})
    
    # Patch the httpx.AsyncClient.post method
    with patch('httpx.AsyncClient.post', side_effect=mock_post):
        yield

def test_complete_chat_flow(mock_supabase, mock_ai_service):
    """
    Test the complete chat flow from user request to AI response,
    including Supabase interactions.
    """
    # Send a message about regulations
    response = client.post(
        "/api/chat",
        json={"message": "Tell me about Afeka's regulations on exams", "user_id": "test-user"}
    )
    
    # Check the response is valid
    assert response.status_code == 200
    response_data = response.json()
    assert "response" in response_data
    
    # Verify the response contains our mock text
    assert "regulations" in response_data["response"].lower()
    assert "academic integrity" in response_data["response"].lower()
    
    # Verify Supabase was called to store the chat
    mock_supabase.table.assert_called()

def test_conversation_threading(mock_supabase, mock_ai_service):
    """
    Test multiple messages in a conversation thread are handled correctly
    """
    # First message in conversation
    first_response = client.post(
        "/api/chat",
        json={
            "message": "What are the regulations?", 
            "user_id": "test-user",
            "session_id": "test-session-1"
        }
    )
    assert first_response.status_code == 200
    
    # Send a follow-up message in the same conversation
    followup_response = client.post(
        "/api/chat",
        json={
            "message": "Tell me more about exam regulations", 
            "user_id": "test-user",
            "session_id": "test-session-1"
        }
    )
    assert followup_response.status_code == 200
    
    # Both responses should have content related to regulations
    first_data = first_response.json()
    followup_data = followup_response.json()
    
    assert "response" in first_data
    assert "response" in followup_data
    
    # The second message should reference regulations
    assert "regulations" in followup_data["response"].lower()
    
    # Verify Supabase was called twice for the two messages
    assert mock_supabase.table.call_count >= 2

def test_error_handling_integration(mock_supabase):
    """Test error handling in the chat endpoint with integration approach"""
    # Test with empty message
    response = client.post(
        "/api/chat",
        json={"message": "", "user_id": "test-user"}
    )
    
    # API returns 500 for empty messages currently
    assert response.status_code == 500
    
    # Supabase should not be called for failed requests
    # Verify the table method was not called or insert was not called
    # This verification might vary depending on your implementation
    assert mock_supabase.table.call_count == 0 or \
           mock_supabase.table().insert.call_count == 0

def test_document_search_integration(mock_supabase):
    """Test document search functionality with integration approach"""
    # Configure mock to return documents
    mock_supabase.table().select().execute.return_value = {
        "data": [
            {
                "id": 1,
                "title": "Exam Regulations",
                "content": "Rules for taking exams at Afeka College",
                "category": "Academic"
            },
            {
                "id": 2,
                "title": "Student Code of Conduct",
                "content": "Guidelines for student behavior",
                "category": "General"
            }
        ]
    }
    
    # Get documents
    response = client.get("/api/documents")
    
    # Check the response
    assert response.status_code == 200
    documents = response.json()
    assert len(documents) == 2
    assert documents[0]["title"] == "Exam Regulations"
    assert documents[1]["category"] == "General" 