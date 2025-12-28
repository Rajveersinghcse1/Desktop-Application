"""
AI Avatar Studio - Version Information

Version: 1.0.0
Release Date: 2025-12-22
"""

__version__ = '1.0.0'
__release_date__ = '2025-12-22'
__author__ = 'AI Avatar Studio Team'
__license__ = 'MIT'
__status__ = 'Production'

# Version components
VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION_INFO = (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)

# Feature flags for this version
FEATURES = {
    'face_detection': True,
    'tts': True,
    'lip_sync': True,
    'gpu_acceleration': True,
    'batch_processing': True,
    'docker_support': True,
    'gui': True,
    'cli': True,
    'background_removal': False,  # Planned for future
    'subtitles': False,           # Planned for future
    'web_interface': False,       # Planned for future
}

# Minimum requirements
MIN_PYTHON_VERSION = (3, 8, 0)
MAX_PYTHON_VERSION = (3, 11, 999)

# Component versions
COMPONENTS = {
    'database_schema': '1.0',
    'config_format': '1.0',
    'model_format': '1.0',
}


def get_version_string():
    """Get full version string."""
    return f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"


def get_version_info():
    """Get version information dictionary."""
    return {
        'version': __version__,
        'release_date': __release_date__,
        'author': __author__,
        'license': __license__,
        'status': __status__,
        'features': FEATURES,
        'min_python': '.'.join(map(str, MIN_PYTHON_VERSION)),
        'max_python': '.'.join(map(str, MAX_PYTHON_VERSION[:2])),
    }


def check_version_compatibility():
    """Check if current Python version is compatible."""
    import sys
    current = sys.version_info[:3]
    
    if current < MIN_PYTHON_VERSION:
        return False, f"Python {'.'.join(map(str, MIN_PYTHON_VERSION))}+ required"
    
    if current >= MAX_PYTHON_VERSION:
        return False, f"Python {'.'.join(map(str, MAX_PYTHON_VERSION[:2]))} maximum"
    
    return True, "Compatible"


if __name__ == "__main__":
    import json
    print(json.dumps(get_version_info(), indent=2))
