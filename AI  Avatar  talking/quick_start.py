"""
Quick Start Setup Script for AI Avatar Studio.

This script guides you through complete setup:
1. Verify system requirements
2. Download required models
3. Setup configuration
4. Run test generation
5. Launch application

Usage:
    python quick_start.py

Author: AI Avatar Studio
Date: 2025-12-22
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


class QuickStart:
    """Handles quick start setup process."""
    
    def __init__(self):
        """Initialize quick start."""
        self.base_dir = Path(__file__).parent
    
    def print_header(self, title: str) -> None:
        """Print section header."""
        print("\n" + "="*70)
        print(title.center(70))
        print("="*70 + "\n")
    
    def print_step(self, step: int, total: int, title: str) -> None:
        """Print step header."""
        print(f"\n{'='*70}")
        print(f"STEP {step}/{total}: {title}")
        print("="*70 + "\n")
    
    def wait_for_user(self, message: str = "Press Enter to continue...") -> bool:
        """Wait for user input."""
        response = input(f"\n{message} ").strip().lower()
        if response == 'q' or response == 'quit':
            print("\nSetup cancelled.")
            return False
        return True
    
    def check_python_version(self) -> bool:
        """Check Python version."""
        version = sys.version_info
        
        print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
        
        if version.major == 3 and 8 <= version.minor <= 11:
            print("✅ Python version is compatible")
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor} is not supported")
            print("   Required: Python 3.8-3.11")
            return False
    
    def check_ffmpeg(self) -> bool:
        """Check FFmpeg installation."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print("✅ FFmpeg is installed")
                return True
            else:
                print("❌ FFmpeg not working properly")
                return False
        
        except FileNotFoundError:
            print("❌ FFmpeg not found in PATH")
            print("\nInstall FFmpeg:")
            print("  Windows: https://ffmpeg.org/download.html")
            print("  Linux: sudo apt install ffmpeg")
            print("  Mac: brew install ffmpeg")
            return False
        except Exception as e:
            print(f"❌ Error checking FFmpeg: {str(e)}")
            return False
    
    def check_dependencies(self) -> bool:
        """Check if dependencies are installed."""
        print("Checking Python dependencies...\n")
        
        required = [
            "torch", "torchvision", "opencv-cv2", "numpy",
            "PIL", "customtkinter", "librosa"
        ]
        
        missing = []
        
        for package in required:
            try:
                if package == "PIL":
                    __import__("PIL")
                elif package == "opencv-cv2":
                    __import__("cv2")
                else:
                    __import__(package)
                print(f"  ✅ {package}")
            except ImportError:
                print(f"  ❌ {package}")
                missing.append(package)
        
        if missing:
            print(f"\n❌ Missing {len(missing)} package(s)")
            print("\nInstall dependencies:")
            print("  pip install -r requirements.txt")
            return False
        
        print("\n✅ All dependencies installed")
        return True
    
    def check_models(self) -> bool:
        """Check if models are downloaded."""
        try:
            from setup_models import ModelDownloader
            
            downloader = ModelDownloader()
            all_present, missing = downloader.check_all_required()
            
            if all_present:
                print("✅ All required models are present")
                return True
            else:
                print(f"❌ Missing {len(missing)} required model(s)")
                for model_id in missing:
                    model_info = downloader.MODELS[model_id]
                    print(f"  • {model_info['name']}")
                return False
        
        except Exception as e:
            print(f"❌ Error checking models: {str(e)}")
            return False
    
    def download_models(self) -> bool:
        """Download required models."""
        print("Downloading required models...\n")
        
        try:
            result = subprocess.run(
                [sys.executable, "setup_models.py", "--required"],
                cwd=self.base_dir
            )
            
            return result.returncode == 0
        
        except Exception as e:
            print(f"❌ Error downloading models: {str(e)}")
            return False
    
    def setup_config(self) -> bool:
        """Setup configuration file."""
        env_file = self.base_dir / ".env"
        env_example = self.base_dir / ".env.example"
        
        if env_file.exists():
            print("✅ Configuration file already exists")
            return True
        
        if not env_example.exists():
            print("⚠️  .env.example not found, skipping config setup")
            return True
        
        try:
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ Configuration file created (.env)")
            print("   You can customize settings in this file later")
            return True
        
        except Exception as e:
            print(f"⚠️  Could not create config file: {str(e)}")
            print("   This is optional, continuing...")
            return True
    
    def run_verification(self) -> bool:
        """Run verification script."""
        print("Running system verification...\n")
        
        try:
            result = subprocess.run(
                [sys.executable, "verify_setup.py"],
                cwd=self.base_dir
            )
            
            return result.returncode == 0
        
        except Exception as e:
            print(f"❌ Error running verification: {str(e)}")
            return False
    
    def launch_app(self) -> None:
        """Launch the application."""
        print("\n🚀 Launching AI Avatar Studio...\n")
        
        try:
            subprocess.run(
                [sys.executable, "main.py"],
                cwd=self.base_dir
            )
        
        except KeyboardInterrupt:
            print("\n\nApplication closed.")
        except Exception as e:
            print(f"\n❌ Error launching app: {str(e)}")
    
    def run(self) -> None:
        """Run complete quick start process."""
        self.print_header("AI AVATAR STUDIO - QUICK START SETUP")
        
        print("This wizard will guide you through setting up Avatar Studio.\n")
        print("You can quit at any time by pressing Ctrl+C or typing 'q'\n")
        
        if not self.wait_for_user("Press Enter to begin setup..."):
            return
        
        # Step 1: Check system requirements
        self.print_step(1, 6, "Checking System Requirements")
        
        python_ok = self.check_python_version()
        ffmpeg_ok = self.check_ffmpeg()
        deps_ok = self.check_dependencies()
        
        if not python_ok:
            print("\n❌ Python version incompatible. Please install Python 3.8-3.11")
            return
        
        if not ffmpeg_ok:
            print("\n❌ FFmpeg required. Please install FFmpeg and restart setup.")
            return
        
        if not deps_ok:
            print("\n⚠️  Dependencies missing.")
            if not self.wait_for_user("Install now? [Y/n]: "):
                return
            
            print("\nInstalling dependencies...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                    cwd=self.base_dir,
                    check=True
                )
                print("✅ Dependencies installed")
            except subprocess.CalledProcessError:
                print("❌ Installation failed. Please install manually:")
                print("   pip install -r requirements.txt")
                return
        
        # Step 2: Check GPU (optional)
        self.print_step(2, 6, "GPU Detection (Optional)")
        
        print("Checking for GPU acceleration...\n")
        
        try:
            result = subprocess.run(
                [sys.executable, "setup_gpu.py", "diagnose"],
                cwd=self.base_dir,
                capture_output=True
            )
            
            # GPU check is optional, continue regardless
            if result.returncode != 0:
                print("ℹ️  GPU not detected, will use CPU (slower)")
        except:
            print("ℹ️  Could not check GPU, will use CPU")
        
        # Step 3: Setup configuration
        self.print_step(3, 6, "Configuration Setup")
        
        if not self.setup_config():
            print("\n⚠️  Config setup had issues, but continuing...")
        
        if not self.wait_for_user():
            return
        
        # Step 4: Download models
        self.print_step(4, 6, "Downloading AI Models")
        
        models_ok = self.check_models()
        
        if not models_ok:
            print("\n📥 Need to download AI models (~400 MB)")
            print("⏱️  This will take 5-15 minutes depending on your connection\n")
            
            if not self.wait_for_user("Download models now? [Y/n]: "):
                print("\n⚠️  Models required to run. You can download later with:")
                print("   python setup_models.py --required")
                return
            
            if not self.download_models():
                print("\n❌ Model download failed. Try again:")
                print("   python setup_models.py --required")
                return
        
        # Step 5: Verification
        self.print_step(5, 6, "System Verification")
        
        if not self.run_verification():
            print("\n⚠️  Verification had warnings, but you can try running the app")
        
        if not self.wait_for_user():
            return
        
        # Step 6: Launch
        self.print_step(6, 6, "Launch Application")
        
        print("✅ Setup complete!\n")
        print("You can now:")
        print("  • Generate talking avatar videos")
        print("  • Process batches of images")
        print("  • Export videos in various qualities\n")
        
        if self.wait_for_user("Launch Avatar Studio now? [Y/n]: "):
            self.launch_app()
        else:
            print("\nYou can launch later with:")
            print("  python main.py")
        
        self.print_header("SETUP COMPLETE! 🎉")


def main():
    """Main entry point."""
    try:
        starter = QuickStart()
        starter.run()
    
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
