import os
import sys
import subprocess

def main():
    """Run a single simple test to verify the API endpoints."""
    # First, run backend tests
    print("Running backend endpoint test...")
    
    # Create a simple test script
    with open('simple_test.py', 'w') as f:
        f.write('''
import pytest
import requests
import os
import time

def test_docker_api():
    """Test if the API is accessible via Docker."""
    # Use environment variables or default to localhost
    api_url = "http://localhost:8000"
    max_retries = 5
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{api_url}/api/health")
            if response.status_code == 200:
                assert response.json().get("status") == "ok"
                print("API health check passed!")
                return
        except requests.RequestException:
            pass
        
        print(f"API not available, retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
        time.sleep(retry_delay)
    
    # If we get here, all retries failed
    pytest.fail("Could not connect to API after multiple attempts")

if __name__ == "__main__":
    # Run the test manually
    try:
        test_docker_api()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
''')

    # Install requests if not already installed
    print("Installing requests package...")
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
    
    # Run the test
    print("Running simple API test...")
    result = subprocess.run([sys.executable, "simple_test.py"])
    
    if result.returncode == 0:
        print("Basic API test completed successfully.")
    else:
        print("API test failed. Check if the backend service is running.")

    # Clean up
    try:
        os.remove('simple_test.py')
    except:
        pass

if __name__ == "__main__":
    main() 