#!/usr/bin/env python
"""
Test Orchestrator for Afeka ChatBot
Runs all test scripts and summarizes results
"""
import os
import sys
import time
import subprocess
from datetime import datetime

# Test scripts to run
TEST_SCRIPTS = [
    {
        "name": "Simple API Test",
        "script": "simple_api_test.py"
    },
    {
        "name": "Extended API Test",
        "script": "api_test_extended.py"
    },
    {
        "name": "Frontend UI Test",
        "script": "frontend_ui_test.py"
    },
    {
        "name": "User Management Tests",
        "script": "run_user_tests.py"
    }
]

def print_header(text):
    """Print a formatted header"""
    width = 80
    print("\n" + "=" * width)
    print(text.center(width))
    print("=" * width + "\n")

def print_test_result(name, success, duration):
    """Print a formatted test result"""
    status = "✓ PASSED" if success else "✗ FAILED"
    print(f"{status} - {name} ({duration:.2f}s)")

def run_test(test):
    """Run a test script and return the result"""
    script_name = test["script"]
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    print(f"\nRunning {test['name']}...")
    
    # Measure execution time
    start_time = time.time()
    
    try:
        # Run the test script as a subprocess
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True
        )
        
        # Calculate execution time
        end_time = time.time()
        duration = end_time - start_time
        
        # Determine success based on exit code
        success = result.returncode == 0
        
        # Print test output
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return {
            "name": test["name"],
            "success": success,
            "duration": duration
        }
    
    except Exception as e:
        print(f"Error running test: {e}")
        
        # Calculate execution time
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "name": test["name"],
            "success": False,
            "duration": duration
        }

def run_all_tests():
    """Run all test scripts and summarize the results"""
    print_header("AFEKA CHATBOT - ALL TESTS")
    
    # Record start time
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"Test run started at: {timestamp}\n")
    
    # Run each test script
    results = []
    for test in TEST_SCRIPTS:
        result = run_test(test)
        results.append(result)
    
    # Calculate total execution time
    end_time = time.time()
    total_duration = end_time - start_time
    
    # Print summary
    print_header("TEST SUMMARY")
    
    for result in results:
        print_test_result(result["name"], result["success"], result["duration"])
    
    # Calculate overall success
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print(f"Total execution time: {total_duration:.2f} seconds")
    
    # Return True if all tests passed
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 