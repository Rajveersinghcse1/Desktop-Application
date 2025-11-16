#!/usr/bin/env python3
"""
OpenUP Setup and Launch Script
Automates environment setup and application launch.
"""

import sys
import subprocess
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.11 or higher."""
    print("Checking Python version...")
    if sys.version_info < (3, 11):
        print(f"❌ Python 3.11+ required. Current version: {sys.version}")
        print("Please install Python 3.11 or higher from https://www.python.org/")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def check_venv():
    """Check if running in virtual environment."""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if not in_venv:
        print("⚠️  Not running in virtual environment")
        print("   Recommendation: Create and activate venv first")
        print("   Run: python -m venv venv")
        print("   Then activate: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Mac/Linux)")
        
        response = input("Continue anyway? (y/n): ")
        return response.lower() == 'y'
    print("✅ Virtual environment detected")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\nInstalling dependencies...")
    req_file = Path(__file__).parent / 'requirements.txt'
    
    if not req_file.exists():
        print("❌ requirements.txt not found!")
        return False
        
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', str(req_file)
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_dependencies():
    """Check if key dependencies are installed."""
    print("\nChecking dependencies...")
    
    required = {
        'PyQt6': 'PyQt6',
        'pandas': 'pandas',
        'PIL': 'Pillow',
        'numpy': 'numpy'
    }
    
    missing = []
    for import_name, package_name in required.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - not installed")
            missing.append(package_name)
            
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        response = input("Install missing packages? (y/n): ")
        if response.lower() == 'y':
            return install_dependencies()
        return False
        
    return True


def create_directories():
    """Create required directories."""
    print("\nCreating required directories...")
    
    dirs = [
        Path.home() / '.openup',
        Path.home() / '.openup' / 'cache',
        Path.home() / '.openup' / 'logs',
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ {dir_path}")
        
    return True


def launch_application(file_arg=None):
    """Launch the OpenUP application."""
    print("\n" + "="*60)
    print("🚀 Launching OpenUP...")
    print("="*60 + "\n")
    
    main_py = Path(__file__).parent / 'main.py'
    
    if not main_py.exists():
        print("❌ main.py not found!")
        return False
        
    try:
        args = [sys.executable, str(main_py)]
        if file_arg:
            args.append(file_arg)
            
        subprocess.run(args)
        return True
    except Exception as e:
        print(f"❌ Failed to launch application: {e}")
        return False


def main():
    """Main setup and launch routine."""
    print("="*60)
    print("   OpenUP - Universal File Preview & Visualization")
    print("   Setup and Launch Script")
    print("="*60 + "\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
        
    # Check virtual environment
    if not check_venv():
        sys.exit(1)
        
    # Check/install dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed!")
        print("   Try manually installing: pip install -r requirements.txt")
        sys.exit(1)
        
    # Create directories
    create_directories()
    
    # Launch application
    file_arg = sys.argv[1] if len(sys.argv) > 1 else None
    if not launch_application(file_arg):
        sys.exit(1)
        
    print("\n✅ OpenUP closed successfully")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
