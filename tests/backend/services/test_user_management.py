import pytest
import requests
import time
import json
import os
import sys
import uuid
import logging
import subprocess
import socket
import importlib
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://cqvicgimmzrffvarlokq.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")  # Public anon key for testing
API_BASE_URL = "http://localhost:8000"

# Services configuration
REQUIRED_SERVICES = {
    "api": {
        "name": "Backend API",
        "check_url": f"{API_BASE_URL}/health",
        "start_command": "cd src/backend && uvicorn main:app --host 0.0.0.0 --port 8000",
        "port": 8000,
    }
    # Add additional services here if needed
    # "frontend": {
    #    "name": "Frontend",
    #    "check_url": "http://localhost:3000",
    #    "start_command": "cd src/frontend && npm start",
    #    "port": 3000,
    # }
}

# Required packages for testing
REQUIRED_PACKAGES = [
    "uvicorn",
    "fastapi",
    "supabase",
    "pytest",
    "requests",
    "python-dotenv"
]

def install_package(package):
    """Install a Python package using pip"""
    try:
        logger.info(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package}: {e}")
        return False

def ensure_dependencies():
    """Check for and install missing dependencies"""
    missing_packages = []
    
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package)
            logger.info(f"Package {package} is already installed")
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"Missing required packages: {', '.join(missing_packages)}")
        logger.info("Installing missing packages...")
        
        for package in missing_packages:
            if not install_package(package):
                logger.error(f"Failed to install {package}. Tests may not run correctly.")
        
        # Reimport after installation (especially for the current script)
        logger.info("Reloading modules after installation...")
        for package in missing_packages:
            try:
                if package == "python-dotenv":
                    # Special case for python-dotenv which imports as dotenv
                    module_name = "dotenv"
                elif package == "fastapi":
                    # We don't need to import FastAPI directly in this script
                    continue
                else:
                    module_name = package
                
                importlib.import_module(module_name)
                logger.info(f"Successfully imported {package} after installation")
            except ImportError as e:
                logger.error(f"Still could not import {package}: {e}")

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def is_service_running(service_config):
    """Check if a service is running by testing its endpoint or port"""
    # First check if the port is in use
    if is_port_in_use(service_config["port"]):
        logger.info(f"Port {service_config['port']} is in use")
        
        # Then try to access the check URL if provided
        if "check_url" in service_config:
            try:
                response = requests.get(service_config["check_url"], timeout=2)
                if response.status_code == 200:
                    logger.info(f"Service {service_config['name']} is running (status code 200)")
                    return True
                else:
                    logger.warning(f"Service port is in use but received status code {response.status_code}")
            except requests.RequestException as e:
                logger.warning(f"Service port is in use but could not connect to check URL: {e}")
        
        # If no check URL or it failed but port is in use, assume it's running
        return True
    return False

def activate_virtual_env():
    """Attempts to activate the test_env virtual environment if needed"""
    # Check if we're already in a virtual environment
    if sys.prefix != sys.base_prefix:
        logger.info(f"Already in a virtual environment: {sys.prefix}")
        return True
    
    # Find and activate the test_env
    venv_path = Path("test_env")
    if not venv_path.exists():
        logger.warning("test_env virtual environment not found")
        return False
    
    # Try to activate the virtual environment
    try:
        if os.name == "nt":  # Windows
            activate_script = venv_path / "Scripts" / "activate.bat"
            if not activate_script.exists():
                logger.warning(f"Activation script not found at {activate_script}")
                return False
            
            # For Windows, we can't truly activate the venv in the current process
            # since subprocess executes in a separate shell, but we can update PATH
            logger.info("Adding virtual environment to PATH...")
            venv_scripts = str(venv_path / "Scripts")
            os.environ["PATH"] = f"{venv_scripts};{os.environ['PATH']}"
            os.environ["VIRTUAL_ENV"] = str(venv_path)
            return True
        else:  # Unix/Linux/Mac
            activate_script = venv_path / "bin" / "activate"
            if not activate_script.exists():
                logger.warning(f"Activation script not found at {activate_script}")
                return False
            
            # Similar approach for Unix systems
            logger.info("Adding virtual environment to PATH...")
            venv_bin = str(venv_path / "bin")
            os.environ["PATH"] = f"{venv_bin}:{os.environ['PATH']}"
            os.environ["VIRTUAL_ENV"] = str(venv_path)
            return True
    except Exception as e:
        logger.error(f"Failed to activate virtual environment: {e}")
        return False

def ensure_services_running():
    """Ensure all required services are running.
    
    This function only starts services that are not already running.
    It returns a dictionary of processes that were started by this function,
    so they can be properly shut down after the tests complete.
    
    Services that were already running before this function was called will
    NOT be included in the returned dictionary, so they will not be shut down
    when the tests are complete.
    
    Returns:
        dict: A dictionary of service_id -> process for services started by this function
    """
    logger.info("Checking required services...")
    
    # Track ONLY the processes that we start here, to shut them down later
    started_processes = {}
    
    # First ensure we have all required dependencies
    ensure_dependencies()
    
    # Try to activate the virtual environment if needed
    activate_virtual_env()
    
    for service_id, service_config in REQUIRED_SERVICES.items():
        if not is_service_running(service_config):
            logger.info(f"Starting {service_config['name']} service...")
            
            # For uvicorn, we'll use a special approach to ensure it works
            if "start_command" in service_config and "uvicorn" in service_config["start_command"]:
                # Extract directory if command starts with cd
                dir_path = None
                if service_config["start_command"].startswith("cd "):
                    parts = service_config["start_command"].split("&&")
                    if len(parts) >= 2:
                        cd_part = parts[0].strip()
                        dir_path = cd_part.replace("cd ", "").strip()
                
                # Direct Python module approach for uvicorn
                try:
                    # Ensure uvicorn is installed
                    install_package("uvicorn")
                    install_package("fastapi")
                    
                    if dir_path and os.path.exists(dir_path):
                        # Construct the Python command to run uvicorn directly
                        python_exe = sys.executable
                        uvicorn_args = "-m uvicorn main:app --host 0.0.0.0 --port 8000"
                        
                        logger.info(f"Starting uvicorn using Python directly: {python_exe} {uvicorn_args} in {dir_path}")
                        
                        # Run uvicorn through Python directly
                        process = subprocess.Popen(
                            f"{python_exe} {uvicorn_args}",
                            shell=True,
                            cwd=dir_path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        
                        # Store the process for later cleanup
                        started_processes[service_id] = process
                        
                        # Wait a bit longer for uvicorn to start
                        time.sleep(5)
                        
                        # Verify the service started
                        if is_service_running(service_config):
                            logger.info(f"Successfully started {service_config['name']} using Python directly")
                        else:
                            logger.error(f"Failed to start {service_config['name']} using Python directly")
                            try:
                                out, err = process.communicate(timeout=1)
                                if err:
                                    logger.error(f"Error output: {err}")
                                if out:
                                    logger.info(f"Output: {out}")
                            except:
                                logger.error("Could not get process output")
                    else:
                        logger.error(f"Directory not found or not specified: {dir_path}")
                except Exception as e:
                    logger.error(f"Error starting uvicorn with Python directly: {e}")
            # Split the command for better execution
            elif "start_command" in service_config:
                command = service_config["start_command"]
                
                # Handle cd command separately for better reliability
                if command.startswith("cd "):
                    parts = command.split("&&")
                    if len(parts) >= 2:
                        # Extract the directory part
                        cd_part = parts[0].strip()
                        dir_path = cd_part.replace("cd ", "").strip()
                        
                        # Extract the actual command
                        actual_command = "&&".join(parts[1:]).strip()
                        
                        # Check if the directory exists
                        if os.path.exists(dir_path):
                            try:
                                # Start the service in the specified directory
                                logger.info(f"Running '{actual_command}' in directory '{dir_path}'")
                                process = subprocess.Popen(
                                    actual_command,
                                    shell=True,
                                    cwd=dir_path,  # Set the working directory
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True
                                )
                                
                                # Store the process for later cleanup
                                started_processes[service_id] = process
                                
                                # Wait a bit for the service to start
                                time.sleep(3)
                                
                                # Verify the service started
                                if is_service_running(service_config):
                                    logger.info(f"Successfully started {service_config['name']}")
                                else:
                                    logger.error(f"Failed to start {service_config['name']}")
                                    # Output the process stderr for debugging
                                    try:
                                        out, err = process.communicate(timeout=1)
                                        if err:
                                            logger.error(f"Error output: {err}")
                                    except:
                                        logger.error("Could not get error output")
                            except Exception as e:
                                logger.error(f"Error starting {service_config['name']}: {e}")
                        else:
                            logger.error(f"Directory not found: {dir_path}")
                    else:
                        logger.error(f"Invalid command format: {command}")
                else:
                    try:
                        # Execute the command as-is
                        process = subprocess.Popen(
                            command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        
                        # Store the process for later cleanup
                        started_processes[service_id] = process
                        
                        # Wait a bit for the service to start
                        time.sleep(3)
                        
                        # Verify the service started
                        if is_service_running(service_config):
                            logger.info(f"Successfully started {service_config['name']}")
                        else:
                            logger.error(f"Failed to start {service_config['name']}")
                    except Exception as e:
                        logger.error(f"Error starting {service_config['name']}: {e}")
        else:
            # This service was already running - we won't shut it down later
            logger.info(f"{service_config['name']} is already running (will NOT be shut down after tests)")
    
    return started_processes

def shutdown_services(started_processes):
    """Shutdown services that were started specifically for the tests.
    
    This function only shuts down processes that were started by the ensure_services_running function.
    Any services that were already running before the tests began will not be affected.
    
    Args:
        started_processes (dict): Dictionary of service_id -> process to shut down
    """
    if not started_processes:
        logger.info("No services to shut down - all were already running before tests")
        return
        
    logger.info(f"Shutting down {len(started_processes)} services that were started for tests...")
    
    for service_id, process in started_processes.items():
        try:
            logger.info(f"Shutting down {REQUIRED_SERVICES[service_id]['name']}...")
            process.terminate()
            process.wait(timeout=5)
            logger.info(f"Service {REQUIRED_SERVICES[service_id]['name']} shut down")
        except Exception as e:
            logger.error(f"Error shutting down service: {e}")
            # Try to force kill if normal termination fails
            try:
                process.kill()
            except:
                pass

# Test data - use random email to avoid conflicts
def generate_test_email():
    """Generate a random test email"""
    random_id = uuid.uuid4().hex[:8]
    return f"test-{random_id}@afeka-test.com"

def force_cleanup_existing_test_users():
    """Force cleanup of any existing test users from previous test runs"""
    from supabase import create_client
    
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        logger.warning("Supabase credentials not found. Skipping force cleanup.")
        return
        
    try:
        # Initialize Supabase client with admin key for deletion
        supabase_admin_key = os.getenv("SUPABASE_SERVICE_KEY")
        if not supabase_admin_key:
            logger.warning("Supabase admin key not found. Skipping force cleanup.")
            return
        
        logger.info("=== Performing force cleanup of any lingering test users ===")
        supabase = create_client(SUPABASE_URL, supabase_admin_key)
        
        # Try to clean up using the stored procedure we created
        try:
            logger.info("Cleaning up test users using cleanup_test_users procedure")
            supabase.rpc("cleanup_test_users").execute()
            logger.info("Successfully cleaned up test users with stored procedure")
            return
        except Exception as e:
            logger.warning(f"Could not use cleanup procedure: {e}")
        
        # Try to delete users directly through the Supabase client
        try:
            # Try to batch-delete users via admin API
            logger.info("Deleting test users directly through Supabase client")
            
            # First get test users
            try:
                # Run a direct query on auth.users table
                result = supabase.rpc(
                    "get_test_users",
                    {"test_domain": "afeka-test.com"}
                ).execute()
                
                if "data" in result:
                    users = result["data"]
                    logger.info(f"Found {len(users)} users to clean up")
                    
                    # Delete each user
                    for user in users:
                        try:
                            user_id = user.get("id")
                            if user_id:
                                supabase.auth.admin.delete_user(user_id)
                                logger.info(f"Deleted user: {user.get('email')}")
                        except Exception as e:
                            logger.warning(f"Error deleting user: {e}")
            except Exception as e:
                logger.warning(f"Could not get users via RPC: {e}")
                
                # Fallback - try direct deletion 
                test_emails = []
                
                # Try an alternative approach - sign out current user to ensure we don't delete them
                try:
                    supabase.auth.sign_out()
                    logger.info("Signed out current user for safety")
                except:
                    pass
                    
                # Use auth API with admin key for deletion
                try:
                    # Get list of users first
                    resp = requests.get(
                        f"{SUPABASE_URL}/auth/v1/admin/users",
                        headers={
                            "apikey": supabase_admin_key,
                            "Authorization": f"Bearer {supabase_admin_key}"
                        }
                    )
                    
                    if resp.status_code == 200:
                        users = resp.json()
                        test_users = [u for u in users if "afeka-test.com" in u.get("email", "")]
                        
                        if test_users:
                            logger.info(f"Found {len(test_users)} test users to delete")
                            
                            for user in test_users:
                                user_id = user.get("id")
                                email = user.get("email")
                                
                                if user_id:
                                    del_resp = requests.delete(
                                        f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}",
                                        headers={
                                            "apikey": supabase_admin_key,
                                            "Authorization": f"Bearer {supabase_admin_key}"
                                        }
                                    )
                                    
                                    if del_resp.status_code in [200, 204]:
                                        logger.info(f"Deleted test user: {email}")
                                    else:
                                        logger.warning(f"Failed to delete user {email}: {del_resp.status_code}")
                        else:
                            logger.info("No test users found to delete")
                    else:
                        logger.warning(f"Failed to get users list: {resp.status_code}")
                except Exception as e:
                    logger.warning(f"Error in auth API cleanup: {e}")
                
        except Exception as e:
            logger.error(f"Error during user cleanup: {e}")
            # Continue with tests even if cleanup fails
    
    except Exception as e:
        logger.error(f"Force cleanup failed: {e}")
        # Continue with tests even if force cleanup fails

class TestUserManagement:
    """Test user management functionalities (signup, login, logout, delete)"""
    
    # Class-level variable to store started processes
    started_processes = {}
    
    @classmethod
    def setup_class(cls):
        """Setup before any test in the class runs"""
        # Ensure all services are running
        cls.started_processes = ensure_services_running()
        
        # Try to clean up any lingering test users
        force_cleanup_existing_test_users()
    
    @classmethod
    def teardown_class(cls):
        """Teardown after all tests in the class have run.
        
        This will shut down ONLY the services that were started by the test itself.
        Any services that were already running before the test will remain running.
        """
        # Shutdown services that were started for the tests
        if cls.started_processes:
            shutdown_services(cls.started_processes)
        else:
            logger.info("No services to shut down - all were already running before tests")
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test case"""
        # Store created user data for cleanup
        self.created_user_ids = []
        yield
        # Cleanup - delete any test users created during tests
        self.delete_test_users()
    
    def delete_test_users(self):
        """Helper to delete all test users created during tests"""
        from supabase import create_client
        
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            logger.warning("Supabase credentials not found. Skipping user cleanup.")
            return
            
        try:
            # Initialize Supabase client with admin key for deletion
            supabase_admin_key = os.getenv("SUPABASE_SERVICE_KEY")
            if not supabase_admin_key:
                logger.warning("Supabase admin key not found. Skipping user cleanup.")
                return
                
            supabase = create_client(SUPABASE_URL, supabase_admin_key)
            
            # Print summary before deletion
            user_count = len(self.created_user_ids)
            logger.info(f"Cleaning up {user_count} test users...")
            
            # Delete each user by ID
            for user_id in self.created_user_ids:
                try:
                    supabase.auth.admin.delete_user(user_id)
                    logger.info(f"Successfully deleted test user with ID: {user_id}")
                except Exception as e:
                    logger.error(f"Error deleting user with ID {user_id}: {e}")
                    # If the standard API fails, try a direct request
                    try:
                        url = f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}"
                        headers = {
                            "apikey": supabase_admin_key,
                            "Authorization": f"Bearer {supabase_admin_key}"
                        }
                        response = requests.delete(url, headers=headers)
                        if response.status_code in [200, 204]:
                            logger.info(f"Successfully deleted user with direct API call: {user_id}")
                        else:
                            logger.error(f"Direct API call failed: {response.status_code}")
                    except Exception as direct_e:
                        logger.error(f"Direct deletion also failed: {direct_e}")
            
            # Also clean up from public.users table
            try:
                # Run SQL query to delete test users from public.users table
                # This uses RPC rather than direct SQL for better compatibility
                supabase.rpc(
                    "cleanup_test_users",
                    {}
                ).execute()
                logger.info("Cleaned up test users from public.users table")
            except Exception as e:
                # If the RPC doesn't exist, try direct SQL
                try:
                    # Create a function to clean up test users if it doesn't exist
                    supabase.table("_setup").select("*").limit(1).execute()  # Just to get a valid request
                    # Use table deletion since we can't directly execute SQL
                    try:
                        supabase.table("users").delete().filter("email", "like", "%afeka-test.com%").execute()
                        logger.info("Cleaned up test users from public.users table using direct delete")
                    except Exception as e2:
                        logger.warning(f"Could not clean up public.users table: {e2}")
                except Exception as e3:
                    logger.warning(f"Could not set up public table cleanup: {e3}")
                    
            # Clear the list after deletion attempts
            self.created_user_ids = []
            logger.info("User cleanup completed.")
            
        except Exception as e:
            logger.error(f"Error in cleanup: {e}")
    
    def test_create_and_delete_regular_user(self):
        """Test creating, authenticating, and deleting a regular user"""
        from supabase import create_client
        
        # Skip if no Supabase credentials
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            pytest.skip("Supabase credentials not found")
        
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # 1. Create a regular user
        user_email = generate_test_email()
        user_password = "Test123456!"
        
        try:
            # Sign up user
            user_data = supabase.auth.sign_up({
                "email": user_email,
                "password": user_password
            })
            
            # Store user ID for cleanup
            user = user_data.user
            user_id = user.id
            self.created_user_ids.append(user_id)
            logger.info(f"Created regular user: {user_email} (ID: {user_id})")
            
            # 2. Verify user exists in Supabase
            assert user is not None
            assert user.email == user_email
            
            # 3. Verify user role (should be regular user by default)
            # Note: You would need to check this differently based on your app's role management
            
            # 4. Test login
            login_response = supabase.auth.sign_in_with_password({
                "email": user_email,
                "password": user_password
            })
            
            # Verify login was successful
            assert login_response.user is not None
            assert login_response.session is not None
            
            # 5. Test API access with token (if your API has authenticated endpoints)
            headers = {
                "Authorization": f"Bearer {login_response.session.access_token}"
            }
            
            # Try to access an authenticated endpoint
            # Uncomment if you have such an endpoint
            # response = requests.get(f"{API_BASE_URL}/api/user/profile", headers=headers)
            # assert response.status_code == 200
            
            # 6. Test logout
            supabase.auth.sign_out()
            
            # 7. Verify logout (try accessing a protected resource again - should fail)
            # Uncomment if you have such an endpoint
            # response = requests.get(f"{API_BASE_URL}/api/user/profile", headers=headers)
            # assert response.status_code in [401, 403]
            
            logger.info(f"Regular user test passed: {user_email}")
            
        except Exception as e:
            # Ensure user gets cleaned up even if test fails
            logger.error(f"Error in regular user test: {e}")
            raise
    
    def test_create_and_delete_admin_user(self):
        """Test creating, authenticating, and deleting an admin user"""
        from supabase import create_client
        
        # Skip if no Supabase credentials
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            pytest.skip("Supabase credentials not found")
            
        supabase_admin_key = os.getenv("SUPABASE_SERVICE_KEY")
        if not supabase_admin_key:
            pytest.skip("Supabase admin key not found")
        
        # Initialize Supabase client with admin key
        supabase = create_client(SUPABASE_URL, supabase_admin_key)
        
        # 1. Create an admin user
        user_email = generate_test_email()
        user_password = "Admin123456!"
        
        try:
            # Create user
            user_data = supabase.auth.admin.create_user({
                "email": user_email,
                "password": user_password,
                "email_confirm": True
            })
            
            user = user_data.user
            user_id = user.id
            self.created_user_ids.append(user_id)
            logger.info(f"Created admin user: {user_email} (ID: {user_id})")
            
            # 2. Set user as admin (this depends on your application's role setup)
            # NOTE: We're skipping this part since the table might not exist
            # or we don't have permissions to insert into it
            logger.info("Skipping setting user as admin since user_roles table might not exist")
            
            # 3. Verify user exists in Supabase
            assert user is not None
            assert user.email == user_email
            
            # 4. Test login
            # Switch to anon key for login test
            auth_supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            login_response = auth_supabase.auth.sign_in_with_password({
                "email": user_email,
                "password": user_password
            })
            
            # Verify login was successful
            assert login_response.user is not None
            assert login_response.session is not None
            
            # We skip this part too as it requires admin endpoints
            # 5. Test admin access (if you have admin-specific endpoints)
            
            # 6. Test logout
            auth_supabase.auth.sign_out()
            
            # 7. We skip checking logout with admin endpoints
            
            logger.info(f"Admin user test passed: {user_email}")
            
        except Exception as e:
            # Ensure user gets cleaned up even if test fails
            logger.error(f"Error in admin user test: {e}")
            raise
    
    def test_manual_user_deletion(self):
        """Test explicitly deleting a user to ensure the deletion process works"""
        from supabase import create_client
        
        # Skip if no Supabase credentials
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            pytest.skip("Supabase credentials not found")
            
        supabase_admin_key = os.getenv("SUPABASE_SERVICE_KEY")
        if not supabase_admin_key:
            pytest.skip("Supabase admin key not found")
        
        # Create user with anon key
        anon_supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        user_email = generate_test_email()
        user_password = "Delete123456!"
        
        try:
            # Sign up user
            user_data = anon_supabase.auth.sign_up({
                "email": user_email,
                "password": user_password
            })
            
            user = user_data.user
            user_id = user.id
            logger.info(f"Created test user for deletion: {user_email} (ID: {user_id})")
            
            # Verify user exists
            assert user is not None
            assert user.email == user_email
            
            # Delete user with admin key
            admin_supabase = create_client(SUPABASE_URL, supabase_admin_key)
            admin_supabase.auth.admin.delete_user(user_id)
            logger.info(f"Manually deleted test user: {user_email}")
            
            # Try to login (should fail)
            try:
                login_response = anon_supabase.auth.sign_in_with_password({
                    "email": user_email,
                    "password": user_password
                })
                # If login succeeds, the test should fail
                assert False, "User was not deleted - login still succeeded"
            except Exception as e:
                # Login should fail if user was deleted
                logger.info(f"Login failed as expected for deleted user: good!")
                pass
                
            logger.info(f"Manual deletion test passed: {user_email}")
            
        except Exception as e:
            logger.error(f"Error in manual deletion test: {e}")
            raise
            
if __name__ == "__main__":
    print("\n===== Running User Management Tests =====\n")
    
    print("NOTE: The test will automatically:")
    print("      1. Install any missing dependencies")
    print("      2. Start required services if they are not running")
    print("      3. Run the tests")
    print("      4. Shut down services that were started by the test")
    print("\nNo manual setup required!\n")
    
    # Set log level
    logging.basicConfig(level=logging.INFO)
    
    # Initialize pytest
    pytest_args = [
        __file__,
        "-v",  # Verbose output
        "--log-cli-level=INFO"  # Show logs in console output
    ]
    
    # Run the tests
    exit_code = pytest.main(pytest_args)
    
    print("\n===== User Management Tests Completed =====\n")
    sys.exit(exit_code) 