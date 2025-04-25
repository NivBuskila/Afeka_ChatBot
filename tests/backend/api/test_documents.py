import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src/backend')))

# Import the FastAPI app
from main import app, Document
from fastapi.testclient import TestClient

# Create a test client
client = TestClient(app)

@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client for testing"""
    mock_supabase = MagicMock()
    
    # Mock document retrieval
    mock_supabase.table().select().execute.return_value = {
        "data": [
            {
                "id": "1",
                "title": "Academic Regulations",
                "content": "Content of academic regulations...",
                "category": "Academic",
                "tags": ["regulations", "academic"]
            },
            {
                "id": "2",
                "title": "Student Guidelines",
                "content": "Content of student guidelines...",
                "category": "Student",
                "tags": ["guidelines", "student"]
            }
        ]
    }
    
    # Mock document insertion
    mock_supabase.table().insert().execute.return_value = {
        "status": 201,
        "data": [{"id": "3"}]
    }
    
    # Apply the mock to the app's supabase_client
    with patch('main.supabase_client', mock_supabase):
        yield mock_supabase

@pytest.fixture
def sample_document():
    """Return a sample document for testing"""
    return {
        "title": "Test Document",
        "content": "This is a test document for document management testing.",
        "category": "Test",
        "tags": ["test", "document"]
    }

def test_get_documents(mock_supabase):
    """Test GET /api/documents returns a list of documents"""
    response = client.get("/api/documents")
    assert response.status_code == 200
    documents = response.json()
    assert len(documents) == 2
    assert documents[0]["title"] == "Academic Regulations"
    assert documents[1]["category"] == "Student"

def test_get_document_by_id(mock_supabase):
    """Test GET /api/documents/{document_id} returns a specific document"""
    # Mock the specific document query
    mock_supabase.table().select().single().execute.return_value = {
        "data": {
            "id": "1",
            "title": "Academic Regulations",
            "content": "Content of academic regulations...",
            "category": "Academic",
            "tags": ["regulations", "academic"]
        }
    }
    
    response = client.get("/api/documents/1")
    assert response.status_code == 200
    document = response.json()
    assert document["id"] == "1"
    assert document["title"] == "Academic Regulations"

def test_get_document_not_found(mock_supabase):
    """Test GET /api/documents/{document_id} with non-existent ID returns 404"""
    # Mock the not found scenario
    mock_supabase.table().select().single().execute.return_value = {"data": None}
    
    response = client.get("/api/documents/999")
    assert response.status_code == 404

def test_create_document_with_api_key(mock_supabase, sample_document):
    """Test POST /api/documents creates a document with valid API key"""
    # Set up a test API key from environment
    with patch('main.INTERNAL_API_KEY', 'test-api-key'):
        response = client.post(
            "/api/documents",
            json=sample_document,
            headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 201
        result = response.json()
        assert "id" in result
        assert result["id"] == "3"

def test_create_document_without_api_key(sample_document):
    """Test POST /api/documents without API key returns 401"""
    response = client.post(
        "/api/documents",
        json=sample_document
    )
    assert response.status_code == 401

def test_create_document_invalid_api_key(sample_document):
    """Test POST /api/documents with invalid API key returns 403"""
    with patch('main.INTERNAL_API_KEY', 'test-api-key'):
        response = client.post(
            "/api/documents",
            json=sample_document,
            headers={"X-API-Key": "invalid-key"}
        )
        assert response.status_code == 403 