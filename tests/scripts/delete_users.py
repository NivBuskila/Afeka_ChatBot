import sys
import time

# List of user IDs to delete from Supabase
user_ids = [
    "fc19e4b0-5cbe-4e5f-a7b3-58265033bc3f",
    "da6f3bf5-5747-4393-8482-1a28299e47a7",
    "e2445f5d-99ad-40b2-ab90-2e8fa96714d9",
    "3b300a3b-e260-49c8-a533-d96db2820fc6",
    "3395e52d-83bb-4767-9baa-288257cc26b3",
    "7e20e5a5-3d15-44e1-9e5a-df7d8e7e94a7",
    "069319b0-d814-40ad-87d3-6933f4d2b380",
    "7f7a3709-3034-4295-b9a9-d2cc7314357b",
    "7dfbf963-8133-4cd8-a532-06ad5dea9d35",
    "acfb75a2-3a67-47cb-812f-65ce7a4dbdb4",
    "7f2ddba2-5e04-4299-909e-5aadc70bbeed",
    "aff5435d-b97d-4da9-a2e1-ae1aef2a1d98",
    "3b78c998-51dc-4336-a052-345e03a04f0e",
    "a3f9cb2b-40e5-4769-8f30-e0f6608fea00",
    "b50dca0d-5309-4f20-afdc-98c910968285",
    "ca1f5ada-f0dc-4a36-8e48-cd58b1b58f94",
    "05557cf6-1def-4519-a3e1-517e54a4a2c0",
    "ba81b6a3-e9f1-4ec2-93db-8734835f281b",
    "3e94824f-4458-43e0-978b-7e14060628b9",
    "3f85cd26-eae7-4860-a4c6-2f846e54e15a",
    "d2f9b6c8-ced2-430c-9c9a-5e7de95272cf",
    "48593262-66bd-44e8-996a-575bbf203e2d",
]

# The emails associated with the IDs (for logging)
user_emails = [
    "test-b37f5eed@afeka-test.com",
    "test-86a95d1d@afeka-test.com",
    "test-6e228471@afeka-test.com",
    "test-695522d4@afeka-test.com",
    "test-31776121@afeka-test.com",
    "test-6b4f96f7@afeka-test.com",
    "test-6aa89ef4@afeka-test.com",
    "test-78eb20ec@afeka-test.com",
    "test-6daeedee@afeka-test.com",
    "test-2e3c7020@afeka-test.com",
    "test-dbdabba2@afeka-test.com",
    "test-d9db73d9@afeka-test.com",
    "test-bc46e8f0@afeka-test.com",
    "test-3f868023@afeka-test.com",
    "test-427f85c3@afeka-test.com",
    "test-ce2a6ac3@afeka-test.com",
    "test-e2360349@afeka-test.com",
    "test-7226aa20@afeka-test.com",
    "test-4cf38e0b@afeka-test.com",
    "test-7fe68723@afeka-test.com",
    "test-0e9d16c4@afeka-test.com",
    "test-155b8320@afeka-test.com",
]

def execute_sql(query):
    """Execute SQL in Supabase project"""
    import os
    import subprocess
    import json
    from dotenv import load_dotenv
    
    load_dotenv()
    
    project_id = "cqvicgimmzrffvarlokq"
    if not project_id:
        print("Missing project ID")
        return None
    
    # Escape the query for URL
    import urllib.parse
    encoded_query = urllib.parse.quote(query)
    
    # Execute the SQL query using MCP
    cmd = f'curl -s "http://localhost:21444/v1/supabase/execute_sql?project_id={project_id}&query={encoded_query}"'
    
    try:
        result = subprocess.check_output(cmd, shell=True, text=True)
        return json.loads(result)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Failed to parse JSON response")
        return None

def main():
    """Delete all test users from Supabase"""
    print("\n===== Deleting Test Users =====\n")
    
    success_count = 0
    failure_count = 0
    
    for i, user_id in enumerate(user_ids):
        email = user_emails[i] if i < len(user_emails) else f"Unknown (ID: {user_id})"
        
        # Delete user with SQL
        query = f"DELETE FROM auth.users WHERE id = '{user_id}'"
        print(f"Deleting user {email}...")
        
        result = execute_sql(query)
        
        if result and "error" not in result:
            print(f"Success: Deleted user {email}")
            success_count += 1
        else:
            print(f"Error: Failed to delete user {email}")
            print(f"Response: {result}")
            failure_count += 1
        
        # Add a small delay to prevent rate limiting
        time.sleep(0.5)
    
    print(f"\nOperation completed. Successfully deleted {success_count} users.")
    if failure_count > 0:
        print(f"Failed to delete {failure_count} users.")
    
    print("\n===== Deletion Complete =====\n")

if __name__ == "__main__":
    main() 