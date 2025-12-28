"""
Setup Verification Script
Verify complete installation and system readiness
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

print("=" * 70)
print("  AI Avatar Studio - Setup Verification")
print("=" * 70)
print()

# Color codes for terminal
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_status(message, status):
    """Print formatted status message"""
    if status == 'OK':
        symbol = f"{GREEN}✓{RESET}"
    elif status == 'WARNING':
        symbol = f"{YELLOW}⚠{RESET}"
    else:
        symbol = f"{RED}✗{RESET}"
    
    print(f"{symbol} {message}")

def check_python():
    """Check Python version"""
    version = sys.version_info
    if 3.8 <= version.major + version.minor / 10 <= 3.11:
        print_status(f"Python {version.major}.{version.minor}.{version.micro}", 'OK')
        return True
    else:
        print_status(f"Python {version.major}.{version.minor} (need 3.8-3.11)", 'ERROR')
        return False

def check_directory_structure():
    """Check if all directories exist"""
    dirs = [
        'config',
        'core',
        'core/face_detection',
        'core/tts',
        'core/video',
        'core/audio',
        'core/image',
        'core/lip_sync',
        'core/pipeline',
        'utils',
        'gui',
        'scripts',
        'docs'
    ]
    
    all_ok = True
    for d in dirs:
        path = project_root / d
        if path.exists():
            print_status(f"Directory: {d}", 'OK')
        else:
            print_status(f"Directory: {d} (missing)", 'ERROR')
            all_ok = False
    
    return all_ok

def check_core_files():
    """Check if core files exist"""
    files = [
        'main.py',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml',
        '.env.example',
        'config/settings.py',
        'config/constants.py',
        'config/paths.py',
        'utils/database.py',
        'utils/logger.py',
        'utils/system_checker.py',
        'utils/model_manager.py',
        'utils/file_manager.py',
        'core/face_detection/detector_base.py',
        'core/tts/tts_manager.py',
        'core/video/video_processor.py',
        'core/audio/audio_processor.py',
        'core/image/image_processor.py',
        'core/lip_sync/wav2lip_engine.py',
        'core/lip_sync/wav2lip_model.py',
        'core/pipeline/generation_pipeline.py',
        'gui/splash_screen.py',
        'gui/main_window.py'
    ]
    
    all_ok = True
    for f in files:
        path = project_root / f
        if path.exists():
            print_status(f"File: {f}", 'OK')
        else:
            print_status(f"File: {f} (missing)", 'ERROR')
            all_ok = False
    
    return all_ok

def check_dependencies():
    """Check if key dependencies are installed"""
    deps = [
        ('numpy', 'numpy'),
        ('PIL', 'pillow'),
        ('cv2', 'opencv-python'),
        ('requests', 'requests'),
        ('tqdm', 'tqdm'),
    ]
    
    all_ok = True
    for module_name, package_name in deps:
        try:
            __import__(module_name)
            print_status(f"Package: {package_name}", 'OK')
        except ImportError:
            print_status(f"Package: {package_name} (not installed)", 'WARNING')
            all_ok = False
    
    return all_ok

def check_optional_dependencies():
    """Check optional dependencies"""
    deps = [
        ('customtkinter', 'CustomTkinter (GUI)'),
        ('torch', 'PyTorch (AI models)'),
        ('librosa', 'librosa (audio)'),
        ('pyttsx3', 'pyttsx3 (TTS)'),
        ('mediapipe', 'MediaPipe (face detection)')
    ]
    
    for module_name, description in deps:
        try:
            __import__(module_name)
            print_status(f"Optional: {description}", 'OK')
        except ImportError:
            print_status(f"Optional: {description} (not installed)", 'WARNING')

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    import subprocess
    
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print_status(f"FFmpeg: {version.split()[2]}", 'OK')
            return True
        else:
            print_status("FFmpeg (not working)", 'ERROR')
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print_status("FFmpeg (not found in PATH)", 'ERROR')
        return False

def check_docker():
    """Check if Docker is available"""
    import subprocess
    
    try:
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_status(f"Docker: {result.stdout.strip()}", 'OK')
            return True
        else:
            print_status("Docker (not working)", 'WARNING')
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print_status("Docker (not found)", 'WARNING')
        return False

def check_disk_space():
    """Check available disk space"""
    import shutil
    
    total, used, free = shutil.disk_usage(project_root)
    free_gb = free / (1024 ** 3)
    
    if free_gb >= 10:
        print_status(f"Disk space: {free_gb:.1f} GB available", 'OK')
        return True
    elif free_gb >= 5:
        print_status(f"Disk space: {free_gb:.1f} GB available (low)", 'WARNING')
        return True
    else:
        print_status(f"Disk space: {free_gb:.1f} GB available (insufficient)", 'ERROR')
        return False

def main():
    """Run all checks"""
    results = {}
    
    print(f"\n{BOLD}1. Checking Python...{RESET}")
    results['python'] = check_python()
    
    print(f"\n{BOLD}2. Checking Directory Structure...{RESET}")
    results['directories'] = check_directory_structure()
    
    print(f"\n{BOLD}3. Checking Core Files...{RESET}")
    results['files'] = check_core_files()
    
    print(f"\n{BOLD}4. Checking Dependencies...{RESET}")
    results['dependencies'] = check_dependencies()
    
    print(f"\n{BOLD}5. Checking Optional Dependencies...{RESET}")
    check_optional_dependencies()
    
    print(f"\n{BOLD}6. Checking FFmpeg...{RESET}")
    results['ffmpeg'] = check_ffmpeg()
    
    print(f"\n{BOLD}7. Checking Docker...{RESET}")
    check_docker()
    
    print(f"\n{BOLD}8. Checking Disk Space...{RESET}")
    results['disk'] = check_disk_space()
    
    # Summary
    print("\n" + "=" * 70)
    print("  Summary")
    print("=" * 70)
    
    critical_checks = ['python', 'directories', 'files', 'disk']
    all_critical_ok = all(results.get(k, False) for k in critical_checks)
    
    if all_critical_ok:
        print(f"\n{GREEN}{BOLD}✓ Setup verification PASSED!{RESET}")
        print("\nCore application files are present and system meets requirements.")
        
        if not results.get('dependencies', False):
            print(f"\n{YELLOW}Note:{RESET} Some Python packages are missing.")
            print("Install with: pip install -r requirements.txt")
        
        if not results.get('ffmpeg', False):
            print(f"\n{YELLOW}Note:{RESET} FFmpeg is required for video processing.")
            print("Install FFmpeg and add to PATH.")
        
        print("\nYou can now run:")
        print("  python main.py")
        return 0
    else:
        print(f"\n{RED}{BOLD}✗ Setup verification FAILED!{RESET}")
        print("\nSome critical components are missing.")
        print("Please review the errors above and fix them.")
        return 1

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Error during verification: {e}{RESET}")
        sys.exit(1)
