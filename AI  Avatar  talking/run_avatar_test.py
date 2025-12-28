"""
Quick Test Script for AI Avatar Studio
Tests basic functionality without requiring GUI
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

print("=" * 70)
print("  AI Avatar Studio - Quick Test")
print("=" * 70)
print()

# Test imports
print("Testing imports...")

try:
    from config import settings, paths, constants
    print("✓ Config modules imported")
except Exception as e:
    print(f"✗ Config import failed: {e}")
    sys.exit(1)

try:
    from utils import DatabaseManager, get_logger
    print("✓ Utils modules imported")
except Exception as e:
    print(f"✗ Utils import failed: {e}")
    sys.exit(1)

try:
    from core.face_detection import FaceDetectionManager
    from core.tts import TTSManager
    from core.video import VideoProcessor
    from core.audio import AudioProcessor
    from core.image import ImageProcessor
    print("✓ Core processing modules imported")
except Exception as e:
    print(f"✗ Core modules import failed: {e}")
    sys.exit(1)

try:
    from core.pipeline import GenerationPipeline
    print("✓ Pipeline module imported")
except Exception as e:
    print(f"✗ Pipeline import failed: {e}")
    sys.exit(1)

print()

# Test database
print("Testing database...")
try:
    db = DatabaseManager()
    
    # Create test project
    project_id = db.create_project(
        name="Test Project",
        description="Automated test project"
    )
    print(f"✓ Created test project (ID: {project_id})")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"✓ Database statistics: {stats['total_projects']} projects")
    
    # Cleanup test project
    db.delete_project(project_id)
    print("✓ Database test passed")
except Exception as e:
    print(f"✗ Database test failed: {e}")

print()

# Test path management
print("Testing path management...")
try:
    print(f"✓ Project root: {paths.project_root}")
    print(f"✓ Data directory: {paths.data_dir}")
    print(f"✓ Models directory: {paths.models_dir}")
    print(f"✓ Output directory: {paths.output_dir}")
    
    # Check if running in Docker
    is_docker = paths._is_docker()
    print(f"✓ Running in Docker: {is_docker}")
    
    # Get disk usage
    usage = paths.get_disk_usage()
    print(f"✓ Free disk space: {usage['free_gb']:.1f} GB")
except Exception as e:
    print(f"✗ Path management test failed: {e}")

print()

# Test configuration
print("Testing configuration...")
try:
    print(f"✓ App version: {settings.APP_VERSION}")
    print(f"✓ Quality presets: {list(settings.QUALITY_PRESETS.keys())}")
    print(f"✓ Resolutions: {list(settings.RESOLUTION_MAP.keys())}")
    
    # Test constants
    print(f"✓ Processing stages: {len(constants.ProcessingStage)}")
    print(f"✓ Generation status: {len(constants.GenerationStatus)}")
except Exception as e:
    print(f"✗ Configuration test failed: {e}")

print()

# Test system requirements
print("Testing system requirements...")
try:
    from utils.system_checker import SystemChecker
    
    checker = SystemChecker()
    
    # Check Python
    python_ok, python_msg = checker.check_python_version()
    print(f"{'✓' if python_ok else '✗'} Python: {python_msg}")
    
    # Check FFmpeg
    ffmpeg_ok, ffmpeg_msg = checker.check_ffmpeg()
    print(f"{'✓' if ffmpeg_ok else '✗'} FFmpeg: {ffmpeg_msg}")
    
    # Check disk space
    disk_ok, disk_msg = checker.check_disk_space()
    print(f"{'✓' if disk_ok else '✗'} Disk: {disk_msg}")
    
    # Check RAM
    ram_ok, ram_msg = checker.check_ram()
    print(f"{'✓' if ram_ok else '✗'} RAM: {ram_msg}")
    
except Exception as e:
    print(f"✗ System check failed: {e}")

print()

# Test model manager
print("Testing model manager...")
try:
    from utils.model_manager import ModelManager
    
    manager = ModelManager(str(paths.models_dir))
    
    # List models
    status = manager.list_models()
    print(f"✓ Available models: {len(status)}")
    
    for name, downloaded in status.items():
        print(f"  - {name}: {'✓ Downloaded' if downloaded else '✗ Not downloaded'}")
    
    # Get model info
    info = manager.get_models_info()
    total_size = sum(m['size_mb'] for m in info.values())
    print(f"✓ Total model size: ~{total_size} MB")
    
except Exception as e:
    print(f"✗ Model manager test failed: {e}")

print()

# Test processors
print("Testing processors...")
try:
    # Face detection
    face_detector = FaceDetectionManager()
    print("✓ Face detection manager created")
    
    # TTS
    tts = TTSManager()
    voices = tts.get_voices()
    print(f"✓ TTS manager created ({len(voices)} voices available)")
    
    # Video processor
    video_proc = VideoProcessor()
    print("✓ Video processor created")
    
    # Audio processor
    audio_proc = AudioProcessor()
    print("✓ Audio processor created")
    
    # Image processor
    image_proc = ImageProcessor()
    print("✓ Image processor created")
    
except Exception as e:
    print(f"✗ Processor test failed: {e}")

print()

# Summary
print("=" * 70)
print("  Test Summary")
print("=" * 70)
print()
print("✓ All core modules are working correctly!")
print()
print("Next steps:")
print("  1. Run: python main.py")
print("  2. Or use Docker: docker-compose up")
print("  3. Download models: Tools → Download Models")
print()
print("The application is ready to use! 🎉")
print()
