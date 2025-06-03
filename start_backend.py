#!/usr/bin/env python
"""
Simple script to start the backend server directly.
This bypasses the run_rag_server.py script that's having issues.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main function to start the backend server"""
    # Get the backend directory path
    backend_dir = Path(__file__).parent / "src" / "backend"
    
    if not backend_dir.exists():
        print(f"Error: Backend directory not found at {backend_dir}")
        sys.exit(1)
    
    # Change to the backend directory
    os.chdir(backend_dir)
    print(f"Changed to directory: {os.getcwd()}")
    
    # Check if main.py exists
    if not (backend_dir / "main.py").exists():
        print(f"Error: main.py not found in {backend_dir}")
        sys.exit(1)
    
    # Start the server using uvicorn
    cmd = [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    print(f"Starting server with command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 