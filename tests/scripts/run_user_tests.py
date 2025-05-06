#!/usr/bin/env python
"""
Run User Management Tests Script
This script runs the user management tests and displays the results
"""
import os
import sys
import subprocess
import time

def print_header(text):
    """Print a formatted header"""
    width = 80
    print("\n" + "=" * width)
    print(text.center(width))
    print("=" * width + "\n")

def print_status(message, status):
    """Print a formatted status message"""
    if status:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print("Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease create a .env file with these variables or set them in your environment.")
        print("You can use .env-example as a template.")
        return False
    return True

def run_tests():
    """Run the user management tests"""
    print_header("AFEKA CHATBOT - USER MANAGEMENT TESTS")
    
    # Check environment variables
    print("Checking environment...")
    if not check_environment():
        return False
    
    # Run the tests
    print("\nRunning tests...")
    start_time = time.time()
    
    try:
        # Run pytest with the test file
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "test_user_management.py", "-v"],
            capture_output=True,
            text=True
        )
        
        # Print the output
        print("\nTest Results:")
        print(result.stdout)
        
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        # Check if tests passed
        passed = result.returncode == 0
        
        # Print summary
        end_time = time.time()
        duration = end_time - start_time
        
        print_header("TEST SUMMARY")
        print(f"Duration: {duration:.2f} seconds")
        print_status("User Management Tests", passed)
        
        if passed:
            print("\nSuccess! All user management tests passed.")
        else:
            print("\nSome tests failed. Please check the output above for details.")
        
        return passed
    
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 