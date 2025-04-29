import subprocess
import sys
import time

def run_command(command, description):
    """Run a command and print its output"""
    print(f"\n===== Running {description} =====\n")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")
    return result.returncode == 0

def main():
    """Run all tests for the Afeka ChatBot system"""
    print("\n===== AFEKA CHATBOT SYSTEM TESTS =====\n")
    
    # Test for backend API
    print("\n=== BACKEND API TESTS ===\n")
    backend_success = run_command("python api_test_extended.py", "Backend API Tests")
    
    # Test for frontend UI
    print("\n=== FRONTEND UI TESTS ===\n")
    frontend_success = run_command("python frontend_ui_test.py", "Frontend UI Tests")
    
    # Print summary of results
    print("\n===== TEST RESULTS SUMMARY =====\n")
    if backend_success:
        print("Backend API: PASSED")
    else:
        print("Backend API: FAILED")
        
    if frontend_success:
        print("Frontend UI: PASSED")
    else:
        print("Frontend UI: FAILED")
        
    if backend_success and frontend_success:
        print("\nALL TESTS PASSED! The Afeka ChatBot system is working correctly.\n")
    else:
        print("\nSOME TESTS FAILED. Please check the logs above for details.\n")
    
    return 0 if (backend_success and frontend_success) else 1

if __name__ == "__main__":
    sys.exit(main()) 