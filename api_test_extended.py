#!/usr/bin/env python
"""
Extended API tests for the Afeka ChatBot
Tests various API endpoints including health, documents, and chat
"""
import sys
import json
import requests
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
TIMEOUT = 10  # seconds

class ApiTests:
    """Tests for the Afeka ChatBot API endpoints"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
    
    def report_result(self, test_name, success, details=None):
        """Report the result of a test"""
        if success:
            self.passed += 1
            print(f"[PASS] {test_name}: SUCCESS")
        else:
            self.failed += 1
            print(f"[FAIL] {test_name}: FAILED {details if details else ''}")
    
    def test_root_endpoint(self):
        """Test the root endpoint (/)"""
        try:
            response = requests.get(f"{API_URL}/", timeout=TIMEOUT)
            
            success = response.status_code == 200
            details = None if success else f"(Status: {response.status_code})"
            
            self.report_result("Root endpoint", success, details)
            return success
        except requests.RequestException as e:
            self.report_result("Root endpoint", False, f"(Error: {e})")
            return False
    
    def test_health_endpoint(self):
        """Test the health endpoint (/api/health)"""
        try:
            response = requests.get(f"{API_URL}/api/health", timeout=TIMEOUT)
            
            success = response.status_code == 200
            details = None if success else f"(Status: {response.status_code})"
            
            self.report_result("Health endpoint", success, details)
            return success
        except requests.RequestException as e:
            self.report_result("Health endpoint", False, f"(Error: {e})")
            return False
    
    def test_documents_endpoint(self):
        """Test the documents endpoint (/api/documents)"""
        try:
            response = requests.get(f"{API_URL}/api/documents", timeout=TIMEOUT)
            
            success = response.status_code == 200
            
            if success:
                # Verify that the response contains a valid documents list
                data = response.json()
                if not isinstance(data, list):
                    success = False
                    details = "(Invalid response format, expected a list)"
                else:
                    details = f"(Found {len(data)} documents)"
            else:
                details = f"(Status: {response.status_code})"
            
            self.report_result("Documents endpoint", success, details)
            return success
        except requests.RequestException as e:
            self.report_result("Documents endpoint", False, f"(Error: {e})")
            return False
        except json.JSONDecodeError:
            self.report_result("Documents endpoint", False, "(Invalid JSON response)")
            return False
    
    def test_chat_endpoint(self):
        """Test the chat endpoint (/api/chat)"""
        try:
            # Test data for chat
            data = {
                "message": "What is Afeka?",
                "conversation_id": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            response = requests.post(
                f"{API_URL}/api/chat",
                json=data,
                timeout=TIMEOUT * 3  # Allow longer timeout for chat endpoint
            )
            
            success = response.status_code == 200
            
            if success:
                # Verify that the response contains a valid result
                data = response.json()
                if not isinstance(data, dict) or 'result' not in data:
                    success = False
                    details = "(Invalid response format, expected dict with 'result')"
                else:
                    message_length = len(data.get('result', ''))
                    details = f"(Response result length: {message_length} chars)"
            else:
                details = f"(Status: {response.status_code})"
            
            self.report_result("Chat endpoint", success, details)
            return success
        except requests.RequestException as e:
            self.report_result("Chat endpoint", False, f"(Error: {e})")
            return False
        except json.JSONDecodeError:
            self.report_result("Chat endpoint", False, "(Invalid JSON response)")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        self.test_root_endpoint()
        self.test_health_endpoint()
        self.test_documents_endpoint()
        self.test_chat_endpoint()
        
        total = self.passed + self.failed
        print(f"\nTest Summary: {self.passed}/{total} passed")
        
        return self.failed == 0

if __name__ == "__main__":
    print("\n===== Extended API Tests =====\n")
    
    tests = ApiTests()
    success = tests.run_all_tests()
    
    print("\n===== Tests Completed =====\n")
    sys.exit(0 if success else 1) 