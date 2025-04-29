import os
import sys
import subprocess
import shutil
import importlib.util

# Add the src directory to the Python path
src_backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, src_backend_path)

# Create a properly structured backend module for testing
backend_module_path = os.path.join(src_backend_path, 'backend')
temp_backend_path = os.path.join(os.getcwd(), 'temp_backend')

try:
    # Create temporary directory for backend module
    if os.path.exists(temp_backend_path):
        shutil.rmtree(temp_backend_path)
    
    os.makedirs(temp_backend_path, exist_ok=True)
    
    # Create __init__.py file
    with open(os.path.join(temp_backend_path, '__init__.py'), 'w') as f:
        pass
    
    # Copy core module
    core_src = os.path.join(src_backend_path, 'backend', 'core')
    core_dest = os.path.join(temp_backend_path, 'core')
    
    if os.path.exists(core_src):
        if not os.path.exists(core_dest):
            os.makedirs(core_dest, exist_ok=True)
        
        # Copy core files
        for file in os.listdir(core_src):
            if file.endswith('.py'):
                shutil.copy(os.path.join(core_src, file), os.path.join(core_dest, file))
        
        # Create __init__.py file in core
        with open(os.path.join(core_dest, '__init__.py'), 'w') as f:
            pass
        
        # Add temp_backend to sys.path
        sys.path.insert(0, os.getcwd())
        
        print(f"Copied core module to {temp_backend_path}")
        
        # Modify PYTHONPATH environment variable
        os.environ['PYTHONPATH'] = os.getcwd()
        
        # Run backend tests with verbose output
        print("Running backend tests...")
        backend_test_cmd = [
            "python", "-m", "pytest", 
            "tests/backend/api/test_api.py", "-v"
        ]
        result = subprocess.run(backend_test_cmd)
        print(f"Test exit code: {result.returncode}")
        
    else:
        print(f"Error: Core module not found at {core_src}")

except Exception as e:
    print(f"Error: {e}")

finally:
    # Clean up
    if os.path.exists(temp_backend_path):
        try:
            shutil.rmtree(temp_backend_path)
        except:
            print(f"Warning: Could not remove {temp_backend_path}")

# Run frontend tests (if needed)
# print("Running frontend tests...")
# frontend_test_cmd = ["cd", "src/frontend", "&&", "npm", "test"]
# subprocess.run(frontend_test_cmd, shell=True) 