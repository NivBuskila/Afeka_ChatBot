import os
import sys
import requests
import json
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://cqvicgimmzrffvarlokq.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
PROJECT_ID = "cqvicgimmzrffvarlokq"

def call_mcp_api(endpoint, method="POST", params=None, json_data=None):
    """Call the MCP API directly"""
    base_url = "http://localhost:21444/v1"
    url = f"{base_url}/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, params=params, json=json_data)
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text
        else:
            print(f"API call failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error calling MCP API: {e}")
        return None

def cleanup_users_via_sql():
    """Clean up test users using SQL migration"""
    print("Attempting cleanup via SQL migration...")
    
    # Create a migration to delete all test users from both auth.users and public.users
    sql_query = """
    DELETE FROM auth.users WHERE email LIKE '%afeka-test.com%';
    DELETE FROM public.users WHERE email LIKE '%afeka-test.com%';
    """
    
    # Call MCP API to apply the migration
    result = call_mcp_api(
        "supabase/apply_migration",
        method="POST",
        json_data={
            "project_id": PROJECT_ID,
            "name": "cleanup_test_users",
            "query": sql_query
        }
    )
    
    if result is not None:
        # Verify the cleanup was successful
        check_result_auth = call_mcp_api(
            "supabase/execute_sql",
            method="GET",
            params={
                "project_id": PROJECT_ID,
                "query": "SELECT count(*) FROM auth.users WHERE email LIKE '%afeka-test.com%';"
            }
        )
        
        check_result_public = call_mcp_api(
            "supabase/execute_sql",
            method="GET",
            params={
                "project_id": PROJECT_ID,
                "query": "SELECT count(*) FROM public.users WHERE email LIKE '%afeka-test.com%';"
            }
        )
        
        if (check_result_auth and check_result_auth[0]["count"] == 0 and
            check_result_public and check_result_public[0]["count"] == 0):
            print("SQL cleanup successful - all test users removed from both tables")
            return True
        else:
            print(f"SQL cleanup result verification failed: auth={check_result_auth}, public={check_result_public}")
    else:
        print("SQL cleanup failed")
    
    return False

def cleanup_users_via_api():
    """Clean up all test users from the database using direct API calls"""
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
        print(f"Connecting to Supabase at {SUPABASE_URL}...")
        
        # List all users
        response = requests.get(f"{api_url}/users", headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to get users: {response.status_code}")
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
                        print(f"Deleted test user: {email} (ID: {user_id})")
                        deleted_count += 1
                    else:
                        print(f"Failed to delete user {email}: {delete_response.status_code}")
                        
                    # Add a small delay to prevent rate limiting
                    time.sleep(0.2)
            except Exception as e:
                print(f"Error deleting user {user.get('email')}: {e}")
        
        print(f"Successfully deleted {deleted_count} test users via API.")
        
        # Also clean up public.users table via direct SQL
        print("Cleaning up test users in public.users table...")
        sql_result = call_mcp_api(
            "supabase/apply_migration",
            method="POST",
            json_data={
                "project_id": PROJECT_ID,
                "name": "cleanup_public_users",
                "query": "DELETE FROM public.users WHERE email LIKE '%afeka-test.com%';"
            }
        )
        
        if sql_result is not None:
            print("Successfully cleaned up public.users table.")
            return True
        else:
            print("Failed to clean up public.users table.")
            return False
        
    except Exception as e:
        print(f"Error in API cleanup: {e}")
        return False

def verify_cleanup():
    """Verify that all test users have been cleaned up"""
    try:
        # Check if any test users remain in auth.users
        result_auth = call_mcp_api(
            "supabase/execute_sql", 
            method="GET",
            params={
                "project_id": PROJECT_ID,
                "query": "SELECT id, email FROM auth.users WHERE email LIKE '%afeka-test.com%';"
            }
        )
        
        # Check if any test users remain in public.users
        result_public = call_mcp_api(
            "supabase/execute_sql", 
            method="GET",
            params={
                "project_id": PROJECT_ID,
                "query": "SELECT id, email FROM public.users WHERE email LIKE '%afeka-test.com%';"
            }
        )
        
        auth_count = len(result_auth) if result_auth else 0
        public_count = len(result_public) if result_public else 0
        
        if auth_count > 0 or public_count > 0:
            print(f"WARNING: {auth_count} test users still remain in auth.users.")
            print(f"WARNING: {public_count} test users still remain in public.users.")
            return False
        else:
            print("Verification successful - no test users remain in either table.")
            return True
    except Exception as e:
        print(f"Error in verification: {e}")
        return False

def cleanup_all_test_users():
    """Clean up all test users using all available methods"""
    print("\n=== CLEANUP PHASE 1: SQL Migration ===\n")
    sql_success = cleanup_users_via_sql()
    
    if sql_success and verify_cleanup():
        return True
    
    print("\n=== CLEANUP PHASE 2: Direct API Calls ===\n")
    api_success = cleanup_users_via_api()
    
    if api_success and verify_cleanup():
        return True
    
    print("\n=== CLEANUP PHASE 3: Final Check ===\n")
    return verify_cleanup()

if __name__ == "__main__":
    print("\n===== Cleaning Up Test Users =====\n")
    
    success = cleanup_all_test_users()
    
    if success:
        print("\n===== Cleanup Completed Successfully =====\n")
        sys.exit(0)
    else:
        print("\n===== Cleanup Completed with Warnings =====\n")
        sys.exit(1) 