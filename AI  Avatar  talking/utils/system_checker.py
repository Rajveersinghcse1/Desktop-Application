"""
System Checker for AI Avatar Studio
Validates all dependencies and system requirements
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class SystemChecker:
    """Check system requirements and dependencies"""
    
    def __init__(self):
        self.checks = []
        self.warnings = []
        self.errors = []
    
    def check_all(self) -> Dict[str, bool]:
        """Run all system checks"""
        results = {
            'python_version': self.check_python_version(),
            'disk_space': self.check_disk_space(),
            'memory': self.check_memory(),
            'ffmpeg': self.check_ffmpeg(),
            'gpu': self.check_gpu(),
            'python_packages': self.check_python_packages(),
        }
        
        return results
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        version = sys.version_info
        
        if version.major == 3 and 8 <= version.minor <= 11:
            self.checks.append(f"✓ Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            self.errors.append(
                f"✗ Python {version.major}.{version.minor} is not supported. "
                f"Please use Python 3.8-3.11"
            )
            return False
    
    def check_disk_space(self, min_gb: int = 10) -> bool:
        """Check available disk space"""
        try:
            import shutil
            stat = shutil.disk_usage(Path.cwd())
            free_gb = stat.free / (1024 ** 3)
            
            if free_gb >= min_gb:
                self.checks.append(f"✓ Disk space: {free_gb:.2f} GB free")
                return True
            else:
                self.warnings.append(
                    f"⚠ Low disk space: {free_gb:.2f} GB "
                    f"(recommended: {min_gb}+ GB)"
                )
                return False
        except Exception as e:
            self.warnings.append(f"⚠ Could not check disk space: {e}")
            return False
    
    def check_memory(self, min_gb: int = 8) -> bool:
        """Check available RAM"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            total_gb = mem.total / (1024 ** 3)
            available_gb = mem.available / (1024 ** 3)
            
            if total_gb >= min_gb:
                self.checks.append(
                    f"✓ RAM: {total_gb:.1f} GB total, "
                    f"{available_gb:.1f} GB available"
                )
                return True
            else:
                self.warnings.append(
                    f"⚠ Limited RAM: {total_gb:.1f} GB "
                    f"(recommended: {min_gb}+ GB)"
                )
                return False
        except ImportError:
            self.warnings.append("⚠ psutil not installed, cannot check memory")
            return False
        except Exception as e:
            self.warnings.append(f"⚠ Could not check memory: {e}")
            return False
    
    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is installed"""
        ffmpeg_path = shutil.which('ffmpeg')
        
        if ffmpeg_path:
            try:
                result = subprocess.run(
                    ['ffmpeg', '-version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                version_line = result.stdout.split('\n')[0]
                self.checks.append(f"✓ FFmpeg found: {version_line}")
                return True
            except Exception as e:
                self.warnings.append(f"⚠ FFmpeg found but error checking version: {e}")
                return False
        else:
            self.errors.append(
                "✗ FFmpeg not found. Please install FFmpeg:\n"
                "  Windows: Download from https://ffmpeg.org/download.html\n"
                "  Linux: sudo apt-get install ffmpeg\n"
                "  macOS: brew install ffmpeg"
            )
            return False
    
    def check_gpu(self) -> bool:
        """Check for GPU availability"""
        try:
            import torch
            
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0)
                self.checks.append(
                    f"✓ GPU available: {gpu_name} "
                    f"({gpu_count} device{'s' if gpu_count > 1 else ''})"
                )
                return True
            else:
                self.warnings.append(
                    "⚠ No GPU detected. Processing will use CPU (slower)"
                )
                return False
        except ImportError:
            self.warnings.append("⚠ PyTorch not installed, cannot check GPU")
            return False
        except Exception as e:
            self.warnings.append(f"⚠ Error checking GPU: {e}")
            return False
    
    def check_python_packages(self) -> bool:
        """Check if required Python packages are installed"""
        # Map package names to their import names
        required_packages = {
            'torch': 'torch',
            'torchvision': 'torchvision',
            'numpy': 'numpy',
            'opencv-python': 'cv2',
            'pillow': 'PIL',
            'pydub': 'pydub',
            'librosa': 'librosa',
            'scipy': 'scipy',
        }
        
        optional_packages = {
            'customtkinter': 'customtkinter',
            'TTS': 'TTS',
            'pyttsx3': 'pyttsx3',
            'mediapipe': 'mediapipe',
            'rembg': 'rembg',
            'psutil': 'psutil',
        }
        
        missing_required = []
        missing_optional = []
        
        for package, import_name in required_packages.items():
            try:
                __import__(import_name)
            except ImportError:
                missing_required.append(package)
        
        for package, import_name in optional_packages.items():
            try:
                __import__(import_name)
            except ImportError:
                missing_optional.append(package)
        
        if not missing_required:
            installed_count = len(required_packages)
            self.checks.append(f"✓ Core Python packages installed ({installed_count})")
        else:
            self.errors.append(
                f"✗ Missing required packages: {', '.join(missing_required)}\n"
                f"  Install with: pip install {' '.join(missing_required)}"
            )
        
        if missing_optional:
            self.warnings.append(
                f"⚠ Missing optional packages: {', '.join(missing_optional)}\n"
                f"  Some features may be limited"
            )
        
        return len(missing_required) == 0
    
    def print_report(self):
        """Print system check report"""
        print("\n" + "=" * 60)
        print("AI AVATAR STUDIO - SYSTEM CHECK REPORT")
        print("=" * 60)
        
        if self.checks:
            print("\n✅ PASSED CHECKS:")
            for check in self.checks:
                print(f"  {check}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  {error}")
        
        print("\n" + "=" * 60)
        
        if self.errors:
            print("❌ System check FAILED. Please fix errors above.")
            return False
        elif self.warnings:
            print("⚠️  System check passed with warnings.")
            return True
        else:
            print("✅ System check PASSED. All requirements met!")
            return True
    
    def get_system_info(self) -> Dict[str, str]:
        """Get detailed system information"""
        info = {
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'platform': sys.platform,
            'os': os.name,
        }
        
        # CPU info
        try:
            import platform
            info['processor'] = platform.processor()
            info['machine'] = platform.machine()
        except Exception:
            pass
        
        # Memory info
        try:
            import psutil
            mem = psutil.virtual_memory()
            info['total_memory_gb'] = f"{mem.total / (1024**3):.2f}"
            info['available_memory_gb'] = f"{mem.available / (1024**3):.2f}"
        except Exception:
            pass
        
        # GPU info
        try:
            import torch
            if torch.cuda.is_available():
                info['gpu'] = torch.cuda.get_device_name(0)
                info['gpu_count'] = str(torch.cuda.device_count())
                info['cuda_version'] = torch.version.cuda
            else:
                info['gpu'] = 'Not available'
        except Exception:
            info['gpu'] = 'Unknown'
        
        # Disk space
        try:
            import shutil
            stat = shutil.disk_usage(Path.cwd())
            info['free_space_gb'] = f"{stat.free / (1024**3):.2f}"
            info['total_space_gb'] = f"{stat.total / (1024**3):.2f}"
        except Exception:
            pass
        
        return info


def check_system_requirements() -> bool:
    """
    Main function to check system requirements
    Returns True if all critical checks pass
    """
    checker = SystemChecker()
    results = checker.check_all()
    success = checker.print_report()
    
    return success


if __name__ == '__main__':
    # Run system check
    success = check_system_requirements()
    sys.exit(0 if success else 1)
