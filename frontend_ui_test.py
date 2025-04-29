#!/usr/bin/env python
"""
Frontend UI Test for Afeka ChatBot
Tests if the React app is accessible and contains key HTML elements
"""
import sys
import requests

# Configuration
FRONTEND_URL = "http://localhost:5173"
TIMEOUT = 10  # seconds

def test_frontend_accessibility():
    """Test that the frontend is accessible and returns HTTP 200"""
    print("Testing frontend accessibility...")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=TIMEOUT)
        
        if response.status_code == 200:
            print("✓ Frontend accessibility: SUCCESS")
            return response
        else:
            print(f"✗ Frontend accessibility: FAILED (Status: {response.status_code})")
            return None
    except requests.RequestException as e:
        print(f"✗ Frontend accessibility: ERROR - {e}")
        return None

def check_for_element(html, search_text, element_name):
    """Check if HTML contains the specified element"""
    if search_text in html:
        print(f"✓ {element_name} found: SUCCESS")
        return True
    else:
        print(f"✗ {element_name} not found: FAILED")
        return False

def test_frontend_elements(response):
    """Test that the frontend contains the expected HTML elements"""
    if not response:
        return False
    
    html = response.text
    
    # Elements to check for
    elements = [
        ('<script src="/src/main.tsx"', 'Main script'),
        ('<div id="root"', 'Root div'),
        ('<title>Afeka ChatBot</title>', 'Title'),
        ('/@vite/client', 'Vite client')
    ]
    
    # Check each element
    results = []
    for search_text, element_name in elements:
        results.append(check_for_element(html, search_text, element_name))
    
    # Return True only if all elements were found
    return all(results)

def run_all_tests():
    """Run all frontend UI tests"""
    print("\n===== Frontend UI Tests =====\n")
    
    # Test 1: Check if frontend is accessible
    response = test_frontend_accessibility()
    
    # Test 2: Check if frontend contains required elements (only if Test 1 passed)
    if response:
        success = test_frontend_elements(response)
    else:
        success = False
    
    # Print summary
    print("\n===== Test Summary =====")
    if success:
        print("All frontend UI tests PASSED")
    else:
        print("Some frontend UI tests FAILED")
    
    print("\n===== Tests Completed =====\n")
    return success

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 