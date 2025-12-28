"""Core package - Main processing engines"""

# This package contains the core AI processing engines:
# - TTS (Text-to-Speech)
# - Face Detection
# - Lip Synchronization
# - Video Processing
# - Audio Processing
# - Image Processing
# - Pipeline Orchestration

from . import face_detection
from . import tts
from . import video
from . import audio
from . import image
from . import lip_sync
from . import pipeline

__all__ = [
    'face_detection',
    'tts',
    'video',
    'audio',
    'image',
    'lip_sync',
    'pipeline'
]
