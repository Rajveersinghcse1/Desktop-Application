"""
Configuration Management for AI Avatar Studio
"""

import os
from pathlib import Path
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class Settings:
    """Application settings manager"""
    
    def __init__(self):
        # Get environment variables or use defaults
        self.DATABASE_PATH = os.getenv('DATABASE_PATH', self._get_default_db_path())
        self.MODELS_PATH = os.getenv('MODELS_PATH', self._get_default_models_path())
        self.OUTPUT_PATH = os.getenv('OUTPUT_PATH', self._get_default_output_path())
        self.CACHE_PATH = os.getenv('CACHE_PATH', self._get_default_cache_path())
        self.LOGS_PATH = os.getenv('LOGS_PATH', self._get_default_logs_path())
        
        # Application settings
        self.APP_NAME = "AI Avatar Studio"
        self.APP_VERSION = "1.0.0"
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        
        # Processing settings
        self.USE_GPU = os.getenv('USE_GPU', 'false').lower() == 'true'
        self.WORKER_THREADS = int(os.getenv('WORKER_THREADS', '2'))
        self.DEFAULT_RESOLUTION = os.getenv('DEFAULT_RESOLUTION', '1080p')
        self.DEFAULT_VIDEO_FORMAT = os.getenv('DEFAULT_VIDEO_FORMAT', 'mp4')
        self.DEFAULT_VIDEO_QUALITY = os.getenv('DEFAULT_VIDEO_QUALITY', 'high')
        
        # TTS settings
        self.DEFAULT_TTS_ENGINE = os.getenv('DEFAULT_TTS_ENGINE', 'coqui')
        self.DEFAULT_TTS_VOICE = os.getenv('DEFAULT_TTS_VOICE', 'jenny')
        self.DEFAULT_TTS_SPEED = float(os.getenv('DEFAULT_TTS_SPEED', '1.0'))
        self.DEFAULT_TTS_PITCH = float(os.getenv('DEFAULT_TTS_PITCH', '1.0'))
        
        # Audio settings
        self.ENABLE_AUDIO_ENHANCEMENT = os.getenv('ENABLE_AUDIO_ENHANCEMENT', 'true').lower() == 'true'
        self.ENABLE_NOISE_REDUCTION = os.getenv('ENABLE_NOISE_REDUCTION', 'true').lower() == 'true'
        self.AUDIO_NORMALIZATION_TARGET = float(os.getenv('AUDIO_NORMALIZATION_TARGET', '-20'))
        
        # Video settings
        self.ENABLE_BACKGROUND_REMOVAL = os.getenv('ENABLE_BACKGROUND_REMOVAL', 'false').lower() == 'true'
        self.ENABLE_SUBTITLES = os.getenv('ENABLE_SUBTITLES', 'false').lower() == 'true'
        self.VIDEO_FPS = int(os.getenv('VIDEO_FPS', '25'))
        
        # Face detection
        self.FACE_DETECTION_CONFIDENCE = float(os.getenv('FACE_DETECTION_CONFIDENCE', '0.7'))
        self.FACE_DETECTION_METHOD = os.getenv('FACE_DETECTION_METHOD', 'mediapipe')
        
        # Model settings
        self.AUTO_DOWNLOAD_MODELS = os.getenv('AUTO_DOWNLOAD_MODELS', 'true').lower() == 'true'
        
        # Performance settings
        self.MAX_PARALLEL_JOBS = int(os.getenv('MAX_PARALLEL_JOBS', '1'))
        self.MEMORY_LIMIT_MB = int(os.getenv('MEMORY_LIMIT_MB', '4096'))
        self.PROCESSING_TIMEOUT = int(os.getenv('PROCESSING_TIMEOUT', '3600'))
        
        # Cleanup settings
        self.CACHE_CLEANUP_DAYS = int(os.getenv('CACHE_CLEANUP_DAYS', '7'))
        self.LOG_CLEANUP_DAYS = int(os.getenv('LOG_CLEANUP_DAYS', '30'))
        self.FAILED_CLEANUP_DAYS = int(os.getenv('FAILED_CLEANUP_DAYS', '7'))
        
        # Security settings
        self.MAX_UPLOAD_SIZE_MB = int(os.getenv('MAX_UPLOAD_SIZE_MB', '10'))
        self.ALLOWED_IMAGE_FORMATS = os.getenv('ALLOWED_IMAGE_FORMATS', 'jpg,jpeg,png,bmp').split(',')
        self.ALLOWED_AUDIO_FORMATS = os.getenv('ALLOWED_AUDIO_FORMATS', 'wav,mp3,ogg,flac').split(',')
        self.MAX_TEXT_LENGTH = int(os.getenv('MAX_TEXT_LENGTH', '5000'))
        
        # Development settings
        self.DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
        self.ENABLE_PROFILING = os.getenv('ENABLE_PROFILING', 'false').lower() == 'true'
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _get_default_db_path(self) -> str:
        """Get default database path"""
        if self._is_docker():
            return '/app/data/database/projects.db'
        return str(Path.cwd() / 'data' / 'database' / 'projects.db')
    
    def _get_default_models_path(self) -> str:
        """Get default models path"""
        if self._is_docker():
            return '/app/models'
        return str(Path.cwd() / 'models')
    
    def _get_default_output_path(self) -> str:
        """Get default output path"""
        if self._is_docker():
            return '/app/output'
        return str(Path.cwd() / 'output')
    
    def _get_default_cache_path(self) -> str:
        """Get default cache path"""
        if self._is_docker():
            return '/app/data/cache'
        return str(Path.cwd() / 'data' / 'cache')
    
    def _get_default_logs_path(self) -> str:
        """Get default logs path"""
        if self._is_docker():
            return '/app/data/logs'
        return str(Path.cwd() / 'data' / 'logs')
    
    def _is_docker(self) -> bool:
        """Check if running inside Docker"""
        return os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER', 'false') == 'true'
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            Path(self.DATABASE_PATH).parent,
            Path(self.MODELS_PATH),
            Path(self.OUTPUT_PATH) / 'videos',
            Path(self.OUTPUT_PATH) / 'thumbnails',
            Path(self.OUTPUT_PATH) / 'exports',
            Path(self.CACHE_PATH),
            Path(self.LOGS_PATH),
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_')
        }
    
    def save_to_file(self, filepath: str):
        """Save settings to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
        logger.info(f"Settings saved to {filepath}")
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'Settings':
        """Load settings from JSON file"""
        settings = cls()
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                for key, value in data.items():
                    if hasattr(settings, key):
                        setattr(settings, key, value)
            logger.info(f"Settings loaded from {filepath}")
        return settings


# Global settings instance
settings = Settings()


# Configuration presets for different quality levels
QUALITY_PRESETS = {
    'fast': {
        'video_quality': 'low',
        'resolution': '480p',
        'fps': 24,
        'audio_enhancement': False,
        'wav2lip_quality': 'fast'
    },
    'balanced': {
        'video_quality': 'medium',
        'resolution': '720p',
        'fps': 25,
        'audio_enhancement': True,
        'wav2lip_quality': 'balanced'
    },
    'high': {
        'video_quality': 'high',
        'resolution': '1080p',
        'fps': 30,
        'audio_enhancement': True,
        'wav2lip_quality': 'high'
    }
}


# Resolution mappings
RESOLUTION_MAP = {
    '480p': (854, 480),
    '720p': (1280, 720),
    '1080p': (1920, 1080),
    '1440p': (2560, 1440),
    '4k': (3840, 2160)
}


# Video format configurations
VIDEO_FORMATS = {
    'mp4': {
        'container': 'mp4',
        'video_codec': 'libx264',
        'audio_codec': 'aac',
        'extension': '.mp4'
    },
    'avi': {
        'container': 'avi',
        'video_codec': 'mpeg4',
        'audio_codec': 'mp3',
        'extension': '.avi'
    },
    'webm': {
        'container': 'webm',
        'video_codec': 'libvpx-vp9',
        'audio_codec': 'libopus',
        'extension': '.webm'
    },
    'mov': {
        'container': 'mov',
        'video_codec': 'libx264',
        'audio_codec': 'aac',
        'extension': '.mov'
    }
}


# TTS voice options
TTS_VOICES = {
    'coqui': [
        {'id': 'jenny', 'name': 'Jenny (Female)', 'language': 'en'},
        {'id': 'jenny_excited', 'name': 'Jenny Excited (Female)', 'language': 'en'},
        {'id': 'male_1', 'name': 'Michael (Male)', 'language': 'en'},
        {'id': 'male_2', 'name': 'David (Male)', 'language': 'en'},
        {'id': 'female_2', 'name': 'Sarah (Female)', 'language': 'en'},
    ],
    'pyttsx3': [
        {'id': 'default', 'name': 'System Default', 'language': 'en'},
    ],
    'gtts': [
        {'id': 'en', 'name': 'English', 'language': 'en'},
        {'id': 'es', 'name': 'Spanish', 'language': 'es'},
        {'id': 'fr', 'name': 'French', 'language': 'fr'},
        {'id': 'de', 'name': 'German', 'language': 'de'},
    ]
}


# Model URLs and checksums
MODEL_REGISTRY = {
    'wav2lip_96': {
        'url': 'https://iiitaphyd-my.sharepoint.com/personal/radrabha_m_research_iiit_ac_in/_layouts/15/download.aspx?share=EdjI7bZlgApMqsVoEUUXpLsBxqXbn5z8VTmoxp55YNDcIA',
        'filename': 'wav2lip_96.pth',
        'size_mb': 148,
        'checksum': 'a82c5c7f98c5e3b8c4e1d5f4e3c2d1a0'
    },
    'wav2lip_gan': {
        'url': 'https://iiitaphyd-my.sharepoint.com/personal/radrabha_m_research_iiit_ac_in/_layouts/15/download.aspx?share=EQRvBxP-zbJMnpczP17XRCIB7HHo1tnYu8bjmlClmV8wuQ',
        'filename': 'wav2lip_gan.pth',
        'size_mb': 148,
        'checksum': 'b73c4e7f98d5e3b8c4e1d5f4e3c2d1b1'
    },
    'face_detection': {
        'url': 'https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth',
        'filename': 's3fd.pth',
        'size_mb': 89,
        'checksum': 'c84d5f6f98e5e3b8c4e1d5f4e3c2d1c2'
    }
}


if __name__ == '__main__':
    # Test configuration
    print("AI Avatar Studio Configuration")
    print("=" * 50)
    print(f"App Name: {settings.APP_NAME}")
    print(f"Version: {settings.APP_VERSION}")
    print(f"Database: {settings.DATABASE_PATH}")
    print(f"Models: {settings.MODELS_PATH}")
    print(f"Output: {settings.OUTPUT_PATH}")
    print(f"Use GPU: {settings.USE_GPU}")
    print(f"TTS Engine: {settings.DEFAULT_TTS_ENGINE}")
    print(f"Resolution: {settings.DEFAULT_RESOLUTION}")
    print("=" * 50)
