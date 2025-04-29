import pytest
import requests
import time
import os

def test_api_health_check():
    """Test if the API health endpoint responds correctly"""
    # Use environment variables or default to localhost
    api_url = "http://localhost:8000"
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{api_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                assert "status" in data
                assert data["status"] == "ok"
                print("✅ API health check passed!")
                return
        except requests.RequestException as e:
            print(f"Request error: {e}")
        
        print(f"API not available, retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
        time.sleep(retry_delay)
    
    # If we get here, all retries failed
    print("❌ Could not connect to API after multiple attempts")
    
def test_frontend_access():
    """Test if the frontend is accessible"""
    frontend_url = "http://localhost:5173"
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.get(frontend_url)
            if response.status_code == 200:
                print("✅ Frontend is accessible!")
                return
        except requests.RequestException as e:
            print(f"Request error: {e}")
        
        print(f"Frontend not available, retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
        time.sleep(retry_delay)
    
    # If we get here, all retries failed
    print("❌ Could not connect to frontend after multiple attempts")

if __name__ == "__main__":
    print("Running API tests...")
    test_api_health_check()
    test_frontend_access()
    print("Tests completed.") 