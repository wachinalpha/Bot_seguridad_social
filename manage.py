import sys
import subprocess
import os
import shutil
from pathlib import Path

def run_command(command, cwd=None, exit_on_error=True):
    print(f">> Running: {command}")
    try:
        subprocess.check_call(command, shell=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"!! Error: Command failed with code {e.returncode}")
        if exit_on_error:
            sys.exit(e.returncode)

def setup():
    print(">> Starting Setup...")
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("!! Warning: Python 3.10+ recommended")
        
    # Backend Setup
    print("\n>> Setting up Backend (rag_app)...")
    if shutil.which("uv"):
        run_command("uv sync", cwd="rag_app")
    else:
        print("!! 'uv' not found. Installing via pip...")
        run_command(f"{sys.executable} -m pip install uv")
        run_command("uv sync", cwd="rag_app")
        
    # Frontend Setup
    print("\n>> Setting up Frontend (front)...")
    if shutil.which("npm"):
        run_command("npm install", cwd="front")
    else:
        print("!! Error: 'npm' not found. Please install Node.js")
        sys.exit(1)
        
    print("\n>> Setup complete!")

def dev():
    print(">> Starting Development Servers...")
    
    # We want to run both in parallel. 
    # On Windows, we can use 'start' to open new console windows, or just run one and tell user to run other.
    # For a simple script, let's run backend in background (or separate window) and frontend in current.
    
    if os.name == 'nt':
        # Windows
        print("   - Launching Backend (New Window)...")
        # Use 'py' or sys.executable if it's not the store shim
        python_exe = sys.executable
        subprocess.Popen(f'start cmd /k "{python_exe}" api_main.py', shell=True, cwd="rag_app", creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        # Unix/Mac
        print("   - Launching Backend (Background)...")
        subprocess.Popen(f'"{sys.executable}" api_main.py &', shell=True, cwd="rag_app")

    print("   - Launching Frontend...")
    try:
        run_command("npm run dev", cwd="front")
    except KeyboardInterrupt:
        print("\n>> Stopping...")

def context_build():
    print(">> Building Context Dump...")
    run_command(f'"{sys.executable}" tools/context_builder.py')

def help():
    print("""
Usage: python manage.py [command]

Commands:
  setup    Install dependencies for backend (uv) and frontend (npm)
  dev      Start development servers (Backend in new window, Frontend here)
  context  Generate context_dump.txt using tools/context_builder.py
  test     Run backend tests
    """)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        help()
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "setup":
        setup()
    elif cmd == "dev":
        dev()
    elif cmd == "context":
        context_build()
    elif cmd == "test":
        run_command("pytest", cwd="rag_app")
    else:
        help()
