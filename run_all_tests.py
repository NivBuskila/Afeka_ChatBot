#!/usr/bin/env python
"""
Test Orchestrator for Afeka ChatBot
Runs all test scripts and summarizes results
"""
import os
import sys
import time
import subprocess
import socket
import logging
import importlib
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Services configuration - all services required for the project
REQUIRED_SERVICES = {
    "api": {
        "name": "Backend API",
        "check_url": "http://localhost:8000/api/health",
        "start_command": "cd src/backend && uvicorn main:app --host 0.0.0.0 --port 8000",
        "port": 8000,
    },
    "frontend": {
        "name": "Frontend",
        "check_url": "http://localhost:5173",
        "start_command": "cd src/frontend && npm run dev",
        "port": 5173,
    }
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
        "script": "test_user_management.py"  # Using the real test file instead of mock
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
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} - {name} ({duration:.2f}s)")

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
                import requests
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

def start_services():
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
    print_header("STARTING REQUIRED SERVICES")
    logger.info("Checking and starting all required services...")
    
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
            # For npm/frontend services
            elif "start_command" in service_config and "npm" in service_config["start_command"]:
                # Extract directory if command starts with cd
                dir_path = None
                if service_config["start_command"].startswith("cd "):
                    parts = service_config["start_command"].split("&&")
                    if len(parts) >= 2:
                        cd_part = parts[0].strip()
                        dir_path = cd_part.replace("cd ", "").strip()
                        
                        # Extract the actual command
                        actual_command = "&&".join(parts[1:]).strip()
                        
                        if os.path.exists(dir_path):
                            logger.info(f"Starting frontend using npm in {dir_path}")
                            
                            try:
                                # Start the npm service
                                process = subprocess.Popen(
                                    actual_command,
                                    shell=True,
                                    cwd=dir_path,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True
                                )
                                
                                # Store the process for later cleanup
                                started_processes[service_id] = process
                                
                                # Wait longer for npm to start (it can take time)
                                logger.info("Waiting for frontend to start (this may take a moment)...")
                                time.sleep(10)
                                
                                # Verify the service started
                                if is_service_running(service_config):
                                    logger.info(f"Successfully started {service_config['name']}")
                                else:
                                    logger.warning(f"Started {service_config['name']} but health check failed. Continuing anyway...")
                            except Exception as e:
                                logger.error(f"Error starting frontend: {e}")
                        else:
                            logger.error(f"Frontend directory not found: {dir_path}")
            # Other services - handle cd command separately for better reliability 
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
    
    # Print summary of what's running
    all_services_running = True
    for service_id, service_config in REQUIRED_SERVICES.items():
        is_running = is_service_running(service_config)
        status = "RUNNING" if is_running else "NOT RUNNING"
        print(f"- {service_config['name']}: {status}")
        if not is_running:
            all_services_running = False
    
    if all_services_running:
        print("\nAll required services are running. Proceeding with tests.\n")
    else:
        print("\nWARNING: Some services could not be started. Tests may fail.\n")
    
    return started_processes

def shutdown_services(started_processes):
    """Shutdown services that were started specifically for the tests.
    
    This function only shuts down processes that were started by the start_services function.
    Any services that were already running before the tests began will not be affected.
    
    Args:
        started_processes (dict): Dictionary of service_id -> process to shut down
    """
    if not started_processes:
        logger.info("No services to shut down - all were already running before tests")
        return
        
    print_header("SHUTTING DOWN SERVICES")
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
    
    # First, ensure all services are running
    started_processes = start_services()
    
    try:
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
        
    finally:
        # Always attempt to shut down services at the end
        shutdown_services(started_processes)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 