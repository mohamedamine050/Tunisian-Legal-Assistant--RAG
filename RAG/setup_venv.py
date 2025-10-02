import os
import subprocess
import sys

def create_venv():
    """Create a virtual environment if it doesn't exist."""
    if not os.path.exists("venv"):
        print("Virtual environment not found. Creating one...")
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print("Virtual environment created.")
    else:
        print("Virtual environment already exists.")

def install_dependencies():
    """Install dependencies from requirements.txt using the virtual environment's pip."""
    # Determine pip path based on OS
    if os.name == "nt":
        pip_executable = os.path.join("venv", "Scripts", "pip")
    else:
        pip_executable = os.path.join("venv", "bin", "pip")
    
    print("Installing dependencies...")
    subprocess.check_call([pip_executable, "install", "-r", "requirements.txt"])
    print("Dependencies installed.")

if __name__ == "__main__":
    create_venv()
    install_dependencies()
