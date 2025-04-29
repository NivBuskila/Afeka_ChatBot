#!/usr/bin/env python
"""
Simple API health check test script
"""
import sys
import requests

API_URL = "http://localhost:8000"

def test_api_health():
    """Test the API health endpoint"""
    print("Testing API health endpoint...")
    
    try:
        response = requests.get(f"{API_URL}/api/health")
        
        if response.status_code == 200:
            print("[PASS] API health check: SUCCESS")
            return True
        else:
            print(f"[FAIL] API health check: FAILED (Status: {response.status_code})")
            return False
    except requests.RequestException as e:
        print(f"[FAIL] API health check: ERROR - {e}")
        return False

if __name__ == "__main__":
    print("\n===== Simple API Health Check =====\n")
    
    success = test_api_health()
    
    print("\n===== Test Completed =====\n")
    sys.exit(0 if success else 1) 