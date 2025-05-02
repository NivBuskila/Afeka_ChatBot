import sys
import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://cqvicgimmzrffvarlokq.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def extract_project_id_from_url(url):
    """Extract project ID from Supabase URL"""
    import re
    match = re.search(r'https://([^.]+)\.supabase\.co', url)
    if match:
        return match.group(1)
    return None

def execute_sql(project_id, query):
    """Execute SQL directly using MCP API"""
    base_url = "http://localhost:21444/v1"
    
    try:
        response = requests.post(
            f"{base_url}/supabase/execute_sql",
            json={
                "project_id": project_id,
                "query": query
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"SQL execution failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error executing SQL: {e}")
        return None

def cleanup_users_via_api():
    """Clean up all test users from the database using direct API calls"""
    print("\n=== Cleaning up test users via direct API calls ===\n")
    
    if not SUPABASE_URL:
        print("ERROR: SUPABASE_URL not found in environment variables.")
        return False
        
    if not SUPABASE_SERVICE_KEY:
        print("ERROR: SUPABASE_SERVICE_KEY not found in environment variables.")
        return False
    
    api_url = f"{SUPABASE_URL}/auth/v1/admin"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }
    
    # First, try to clean up using direct SQL
    project_id = extract_project_id_from_url(SUPABASE_URL)
    if project_id:
        print("Cleaning up test users using direct SQL...")
        
        # Clean auth.users table
        auth_result = execute_sql(
            project_id, 
            "DELETE FROM auth.users WHERE email LIKE '%afeka-test.com%';"
        )
        
        # Clean public.users table
        public_result = execute_sql(
            project_id, 
            "DELETE FROM public.users WHERE email LIKE '%afeka-test.com%';"
        )
        
        if auth_result is not None and public_result is not None:
            print("SQL cleanup executed successfully.")
    
    # Now try the API-based cleanup
    try:
        print(f"Connecting to Supabase at {SUPABASE_URL}...")
        
        # List all users
        response = requests.get(f"{api_url}/users", headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to get users via API: {response.status_code} - {response.text}")
            return False
        
        users = response.json()
        
        # Filter for test users (emails containing 'afeka-test.com')
        test_users = [user for user in users if user.get('email') and 'afeka-test.com' in user.get('email')]
        
        print(f"Found {len(test_users)} test users to delete via API.")
        
        if not test_users:
            print("No test users found in auth.users.")
        
        # Delete each test user
        deleted_count = 0
        for user in test_users:
            try:
                user_id = user.get('id')
                email = user.get('email')
                
                if user_id:
                    # Delete the user
                    delete_response = requests.delete(f"{api_url}/users/{user_id}", headers=headers)
                    
                    if delete_response.status_code in [200, 204]:
                        print(f"Deleted test user via API: {email} (ID: {user_id})")
                        deleted_count += 1
                    else:
                        print(f"Failed to delete user {email} via API: {delete_response.status_code} - {delete_response.text}")
                        
                    # Add a small delay to prevent rate limiting
                    time.sleep(0.2)
            except Exception as e:
                print(f"Error deleting user {user.get('email')} via API: {e}")
        
        print(f"Successfully deleted {deleted_count} of {len(test_users)} test users via API.")
        
        return True
        
    except Exception as e:
        print(f"Error in API cleanup: {e}")
        return False

def verify_cleanup():
    """Verify that all test users have been cleaned up"""
    print("\n=== Verifying cleanup ===\n")
    
    project_id = extract_project_id_from_url(SUPABASE_URL)
    if project_id:
        # Check auth.users table
        auth_result = execute_sql(
            project_id, 
            "SELECT COUNT(*) FROM auth.users WHERE email LIKE '%afeka-test.com%';"
        )
        
        # Check public.users table
        public_result = execute_sql(
            project_id, 
            "SELECT COUNT(*) FROM public.users WHERE email LIKE '%afeka-test.com%';"
        )
        
        if auth_result is not None and public_result is not None:
            auth_count = auth_result[0]["count"] if auth_result else 0
            public_count = public_result[0]["count"] if public_result else 0
            
            if auth_count > 0 or public_count > 0:
                print(f"WARNING: {auth_count} test users still remain in auth.users.")
                print(f"WARNING: {public_count} test users still remain in public.users.")
                return False
            else:
                print("Verification successful - no test users remain in either table.")
                return True
    
    # Fall back to API verification if direct SQL failed
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("ERROR: Supabase credentials not found.")
        return False
    
    api_url = f"{SUPABASE_URL}/auth/v1/admin"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # List all users again to check if any test users remain
        response = requests.get(f"{api_url}/users", headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to verify cleanup: {response.status_code} - {response.text}")
            return False
        
        users = response.json()
        
        # Filter for test users (emails containing 'afeka-test.com')
        remaining_test_users = [user for user in users if user.get('email') and 'afeka-test.com' in user.get('email')]
        
        if remaining_test_users:
            print(f"WARNING: {len(remaining_test_users)} test users still remain in auth.users.")
            return False
        else:
            print("Verification successful - no test users remain in auth.users.")
            # Still need to verify public.users table
            if project_id:
                public_result = execute_sql(
                    project_id, 
                    "SELECT COUNT(*) FROM public.users WHERE email LIKE '%afeka-test.com%';"
                )
                if public_result and public_result[0]["count"] > 0:
                    print(f"WARNING: {public_result[0]['count']} test users still remain in public.users.")
                    return False
            
            return True
        
    except Exception as e:
        print(f"Error in verification: {e}")
        return False

def cleanup_all_test_users():
    """Clean up all test users using API method"""
    project_id = extract_project_id_from_url(SUPABASE_URL)
    if project_id:
        print(f"Project ID: {project_id}")
    else:
        print("WARNING: Could not extract project ID from URL.")
    
    print("\n=== CLEANUP PHASE: Direct API Calls ===\n")
    api_success = cleanup_users_via_api()
    
    print("\n=== VERIFICATION PHASE: Checking for Remaining Users ===\n")
    verification = verify_cleanup()
    
    return api_success and verification

if __name__ == "__main__":
    print("\n===== Cleaning Up Test Users =====\n")
    
    success = cleanup_all_test_users()
    
    if success:
        print("\n===== Cleanup Completed Successfully =====\n")
        sys.exit(0)
    else:
        print("\n===== Cleanup Completed with Warnings =====\n")
        sys.exit(1) 