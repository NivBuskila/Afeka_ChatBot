import requests
import time
import json

def test_frontend_accessibility():
    """Test if the frontend UI is accessible"""
    frontend_url = "http://localhost:5173"
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.get(frontend_url)
            if response.status_code == 200:
                print(f"PASSED - Frontend UI is accessible ({frontend_url})")
                return True
        except requests.RequestException as e:
            print(f"Request error: {e}")
        
        print(f"Frontend not available, retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
        time.sleep(retry_delay)
    
    # If we get here, all retries failed
    print(f"FAILED - Could not access Frontend UI ({frontend_url})")
    return False

def check_frontend_components():
    """Check if key elements are present in the frontend UI"""
    frontend_url = "http://localhost:5173"
    try:
        response = requests.get(frontend_url)
        
        # Check for common frontend components in HTML
        html_content = response.text.lower()
        
        components_to_check = [
            {"name": "React script", "pattern": "react", "required": True},
            {"name": "Chat container", "pattern": "chat", "required": False},
            {"name": "App root", "pattern": "root", "required": True},
        ]
        
        results = []
        all_required_passed = True
        
        for component in components_to_check:
            found = component["pattern"] in html_content
            
            if found:
                print(f"FOUND - {component['name']}")
                results.append({"component": component["name"], "result": "FOUND"})
            else:
                status = "MISSING" if component["required"] else "NOT FOUND (optional)"
                print(f"{status} - {component['name']}")
                results.append({"component": component["name"], "result": status})
                
                if component["required"]:
                    all_required_passed = False
        
        return all_required_passed, results
            
    except requests.RequestException as e:
        print(f"ERROR - Could not check frontend components: {e}")
        return False, []

if __name__ == "__main__":
    print("\n===== Running Frontend UI Tests =====\n")
    
    # Test basic accessibility
    frontend_accessible = test_frontend_accessibility()
    
    if frontend_accessible:
        # Check for frontend components
        components_check, component_results = check_frontend_components()
        
        print("\n===== Test Summary =====\n")
        if components_check:
            print("Frontend UI components: All required components found")
        else:
            print("Frontend UI components: Some required components are missing")
    else:
        print("\n===== Test Summary =====\n")
        print("Frontend UI: Not accessible")
    
    print("\n===== Tests Completed =====\n") 