import pytest
import requests

def test_root():
    """Test the root endpoint returns a welcome message"""
    response = requests.get("http://localhost:8000/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Afeka ChatBot API is running" in response.json()["message"]

def test_health_check():
    """Test the /api/health endpoint returns the expected status"""
    response = requests.get("http://localhost:8000/api/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "ok"

def test_chat_endpoint_with_valid_message():
    """Test the chat endpoint with a valid message"""
    response = requests.post(
        "http://localhost:8000/api/chat",
        json={"message": "Hello", "user_id": "test-user"}
    )
    
    assert response.status_code == 200
    # The exact response structure might vary, but it should be valid JSON
    response_data = response.json()
    assert isinstance(response_data, dict) 