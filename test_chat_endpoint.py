#!/usr/bin/env python
"""
Specific test for the chat endpoint
"""
import sys
import json
import requests
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
TIMEOUT = 30  # seconds

def test_chat_endpoint():
    """Test the chat endpoint (/api/chat)"""
    print("Testing chat endpoint...")
    
    try:
        # Test data for chat
        data = {
            "message": "What is Afeka?",
            "conversation_id": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
        
        print(f"Sending request to {API_URL}/api/chat with data: {data}")
        
        response = requests.post(
            f"{API_URL}/api/chat",
            json=data,
            timeout=TIMEOUT
        )
        
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            # Verify that the response contains a valid message
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2)}")
            
            if not isinstance(response_data, dict) or 'message' not in response_data:
                print("[FAIL] Chat endpoint: FAILED (Invalid response format, expected dict with 'message')")
                return False
            else:
                message_length = len(response_data.get('message', ''))
                print(f"[PASS] Chat endpoint: SUCCESS (Response message length: {message_length} chars)")
                return True
        else:
            try:
                error_data = response.json()
                print(f"[FAIL] Chat endpoint: FAILED (Status: {response.status_code}, Error: {json.dumps(error_data, indent=2)})")
            except:
                print(f"[FAIL] Chat endpoint: FAILED (Status: {response.status_code}, Response: {response.text})")
            return False
    except requests.RequestException as e:
        print(f"[FAIL] Chat endpoint: FAILED (Error: {e})")
        return False
    except json.JSONDecodeError as e:
        print(f"[FAIL] Chat endpoint: FAILED (Invalid JSON response: {e})")
        return False
    except Exception as e:
        print(f"[FAIL] Chat endpoint: FAILED (Unexpected error: {e})")
        return False

if __name__ == "__main__":
    print("\n===== Chat Endpoint Test =====\n")
    
    success = test_chat_endpoint()
    
    print("\n===== Test Completed =====\n")
    sys.exit(0 if success else 1) 