import requests
import time
import json

def test_api_endpoints():
    """Test multiple API endpoints"""
    base_url = "http://localhost:8000"
    endpoints = [
        {"path": "/", "method": "GET", "expected_status": 200, "name": "Root endpoint"},
        {"path": "/api/health", "method": "GET", "expected_status": 200, "name": "Health check"},
        {"path": "/api/documents", "method": "GET", "expected_status": 200, "name": "Documents list"}
    ]
    
    results = []
    
    for endpoint in endpoints:
        try:
            if endpoint["method"] == "GET":
                response = requests.get(f"{base_url}{endpoint['path']}")
            else:
                # Add support for POST and other methods as needed
                continue
                
            status_match = response.status_code == endpoint["expected_status"]
            result = {
                "endpoint": endpoint["name"],
                "path": endpoint["path"],
                "expected_status": endpoint["expected_status"],
                "actual_status": response.status_code,
                "result": "PASSED" if status_match else "FAILED",
                "response": response.json() if response.headers.get('content-type') == 'application/json' else None
            }
            
            results.append(result)
            print(f"{result['result']} - {result['endpoint']} ({result['path']})")
            
        except requests.RequestException as e:
            results.append({
                "endpoint": endpoint["name"],
                "path": endpoint["path"],
                "result": "ERROR",
                "error": str(e)
            })
            print(f"ERROR - {endpoint['name']} ({endpoint['path']}): {str(e)}")
    
    return results

def test_chat_endpoint():
    """Test the chat endpoint with a simple message"""
    base_url = "http://localhost:8000"
    chat_endpoint = "/api/chat"
    
    test_message = {
        "message": "ברוכים הבאים לאפקה",
        "user_id": "test-user-123"
    }
    
    try:
        response = requests.post(
            f"{base_url}{chat_endpoint}", 
            json=test_message,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"PASSED - Chat endpoint test ({chat_endpoint})")
            return {
                "endpoint": "Chat API",
                "path": chat_endpoint,
                "status": response.status_code,
                "result": "PASSED",
                "response": response.json()
            }
        else:
            print(f"FAILED - Chat endpoint test ({chat_endpoint}) - Status: {response.status_code}")
            return {
                "endpoint": "Chat API",
                "path": chat_endpoint,
                "status": response.status_code,
                "result": "FAILED"
            }
    except requests.RequestException as e:
        print(f"ERROR - Chat endpoint test ({chat_endpoint}): {str(e)}")
        return {
            "endpoint": "Chat API",
            "path": chat_endpoint,
            "result": "ERROR",
            "error": str(e)
        }

if __name__ == "__main__":
    print("\n===== Running Extended API Tests =====\n")
    
    # Test basic endpoints
    api_results = test_api_endpoints()
    
    # Test chat functionality
    chat_result = test_chat_endpoint()
    
    print("\n===== Test Summary =====\n")
    passed = sum(1 for r in api_results if r["result"] == "PASSED")
    failed = sum(1 for r in api_results if r["result"] == "FAILED" or r["result"] == "ERROR")
    
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if chat_result.get("result") == "PASSED":
        print("Chat functionality: PASSED")
    else:
        print("Chat functionality: FAILED")
    
    print("\n===== Tests Completed =====\n") 