"""
Constants for AI Avatar Studio
"""

# Application info
APP_NAME = "AI Avatar Studio"
APP_VERSION = "1.0.0"
APP_AUTHOR = "AI Avatar Team"
APP_DESCRIPTION = "Transform static images into lifelike talking avatars"

# Processing stages
STAGE_FACE_DETECTION = "face_detection"
STAGE_IMAGE_PREPROCESSING = "image_preprocessing"
STAGE_TTS_GENERATION = "tts_generation"
STAGE_AUDIO_ENHANCEMENT = "audio_enhancement"
STAGE_LIP_SYNC = "lip_sync"
STAGE_VIDEO_ENCODING = "video_encoding"
STAGE_QUALITY_CONTROL = "quality_control"
STAGE_POSTPROCESSING = "postprocessing"

# Status codes
STATUS_QUEUED = "queued"
STATUS_PROCESSING = "processing"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_DRAFT = "draft"

# File size limits (in bytes)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_TEXT_LENGTH = 5000  # characters

# Image constraints
MIN_IMAGE_WIDTH = 256
MIN_IMAGE_HEIGHT = 256
MAX_IMAGE_WIDTH = 4096
MAX_IMAGE_HEIGHT = 4096

# Video constraints
MIN_VIDEO_FPS = 20
MAX_VIDEO_FPS = 60
MIN_VIDEO_DURATION = 1  # seconds
MAX_VIDEO_DURATION = 300  # 5 minutes

# Audio constraints
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
MIN_AUDIO_DURATION = 0.5  # seconds
MAX_AUDIO_DURATION = 300  # 5 minutes

# Face detection
MIN_FACE_SIZE = 128
MIN_FACE_CONFIDENCE = 0.5
MAX_FACES = 1  # Only process single face

# Processing timeouts (seconds)
TIMEOUT_FACE_DETECTION = 30
TIMEOUT_TTS = 120
TIMEOUT_AUDIO_PROCESSING = 60
TIMEOUT_LIP_SYNC = 1800  # 30 minutes
TIMEOUT_VIDEO_ENCODING = 600  # 10 minutes

# Cache settings
CACHE_EXPIRY_HOURS = 24
MAX_CACHE_SIZE_MB = 2048

# Batch processing
MAX_BATCH_SIZE = 100
BATCH_PRIORITY_HIGH = 10
BATCH_PRIORITY_NORMAL = 5
BATCH_PRIORITY_LOW = 1

# Error messages
ERROR_NO_FACE_DETECTED = "No face detected in the image"
ERROR_MULTIPLE_FACES = "Multiple faces detected. Please use an image with a single face"
ERROR_IMAGE_TOO_SMALL = "Image resolution is too small"
ERROR_IMAGE_TOO_LARGE = "Image file size exceeds maximum limit"
ERROR_AUDIO_TOO_LONG = "Audio duration exceeds maximum limit"
ERROR_TEXT_TOO_LONG = "Text length exceeds maximum limit"
ERROR_INVALID_FORMAT = "Invalid file format"
ERROR_PROCESSING_FAILED = "Processing failed. Please try again"
ERROR_MODEL_NOT_FOUND = "Required AI model not found"
ERROR_INSUFFICIENT_MEMORY = "Insufficient memory to process request"
ERROR_TIMEOUT = "Processing timeout exceeded"

# Success messages
SUCCESS_GENERATION_COMPLETE = "Avatar generated successfully!"
SUCCESS_PROJECT_SAVED = "Project saved successfully"
SUCCESS_MODEL_DOWNLOADED = "Model downloaded successfully"

# UI Constants
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 768
WINDOW_DEFAULT_WIDTH = 1280
WINDOW_DEFAULT_HEIGHT = 800

# Colors (for GUI themes)
COLOR_PRIMARY = "#1f538d"
COLOR_SECONDARY = "#14375e"
COLOR_SUCCESS = "#2ecc71"
COLOR_ERROR = "#e74c3c"
COLOR_WARNING = "#f39c12"
COLOR_INFO = "#3498db"
COLOR_DARK_BG = "#1e1e1e"
COLOR_LIGHT_BG = "#f5f5f5"
COLOR_TEXT_DARK = "#ffffff"
COLOR_TEXT_LIGHT = "#2c3e50"

# Processing stages with estimated time percentages
STAGE_PROGRESS_MAP = {
    STAGE_FACE_DETECTION: (0, 5),      # 0-5%
    STAGE_IMAGE_PREPROCESSING: (5, 10),  # 5-10%
    STAGE_TTS_GENERATION: (10, 25),     # 10-25%
    STAGE_AUDIO_ENHANCEMENT: (25, 30),  # 25-30%
    STAGE_LIP_SYNC: (30, 85),          # 30-85% (longest stage)
    STAGE_VIDEO_ENCODING: (85, 95),    # 85-95%
    STAGE_QUALITY_CONTROL: (95, 98),   # 95-98%
    STAGE_POSTPROCESSING: (98, 100),   # 98-100%
}

# Model types
MODEL_TYPE_WAV2LIP = "wav2lip"
MODEL_TYPE_TTS = "tts"
MODEL_TYPE_FACE_DETECTION = "face_detection"
MODEL_TYPE_BACKGROUND_REMOVAL = "background_removal"

# Log format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# File naming patterns
FILENAME_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
FILENAME_PATTERN_VIDEO = "avatar_{timestamp}_{id}.{ext}"
FILENAME_PATTERN_AUDIO = "audio_{timestamp}_{id}.wav"
FILENAME_PATTERN_THUMBNAIL = "thumb_{timestamp}_{id}.jpg"

# Supported formats
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
SUPPORTED_AUDIO_FORMATS = ['.wav', '.mp3', '.ogg', '.flac', '.m4a']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.webm']

# GPU detection
CUDA_AVAILABLE_CHECK = "torch.cuda.is_available()"
CUDA_DEVICE_COUNT = "torch.cuda.device_count()"

# System requirements
MIN_RAM_GB = 8
RECOMMENDED_RAM_GB = 16
MIN_DISK_SPACE_GB = 10
RECOMMENDED_DISK_SPACE_GB = 20

# API keys placeholder (for future use)
API_KEY_PLACEHOLDER = "your_api_key_here"

# Feature flags
FEATURE_BATCH_PROCESSING = True
FEATURE_BACKGROUND_REMOVAL = True
FEATURE_SUBTITLES = True
FEATURE_MULTIPLE_VOICES = True
FEATURE_AUDIO_UPLOAD = True
FEATURE_VIDEO_EFFECTS = False  # Coming soon
FEATURE_REAL_TIME_PREVIEW = False  # Coming soon
FEATURE_WEB_INTERFACE = False  # Coming soon

# Default values
DEFAULT_VIDEO_BITRATE = "5000k"
DEFAULT_AUDIO_BITRATE = "192k"
DEFAULT_THUMBNAIL_SIZE = (320, 180)
DEFAULT_PREVIEW_SIZE = (640, 360)

# Processing quality levels
QUALITY_LOW = "low"
QUALITY_MEDIUM = "medium"
QUALITY_HIGH = "high"
QUALITY_ULTRA = "ultra"

# Quality to bitrate mapping
QUALITY_BITRATE_MAP = {
    QUALITY_LOW: "2000k",
    QUALITY_MEDIUM: "5000k",
    QUALITY_HIGH: "8000k",
    QUALITY_ULTRA: "15000k"
}

# Quality to CRF mapping (for x264)
QUALITY_CRF_MAP = {
    QUALITY_LOW: 28,
    QUALITY_MEDIUM: 23,
    QUALITY_HIGH: 18,
    QUALITY_ULTRA: 15
}

# Database table names
TABLE_PROJECTS = "projects"
TABLE_GENERATIONS = "generations"
TABLE_SETTINGS = "settings"
TABLE_PROCESSING_LOGS = "processing_logs"
TABLE_MODEL_VERSIONS = "model_versions"
TABLE_USER_PREFERENCES = "user_preferences"
TABLE_BATCH_QUEUE = "batch_queue"

# Preference keys
PREF_THEME = "theme"
PREF_LANGUAGE = "language"
PREF_AUTO_SAVE = "auto_save"
PREF_SHOW_CONSOLE = "show_console"
PREF_LAST_TTS_ENGINE = "last_tts_engine"
PREF_LAST_VOICE = "last_voice"
PREF_LAST_RESOLUTION = "last_resolution"
PREF_LAST_FORMAT = "last_format"
PREF_NOTIFICATION_ENABLED = "notification_enabled"
PREF_SOUND_ENABLED = "sound_enabled"

# UI Themes
THEME_DARK = "dark"
THEME_LIGHT = "light"
THEME_AUTO = "auto"

# Languages (for future i18n)
LANG_ENGLISH = "en"
LANG_SPANISH = "es"
LANG_FRENCH = "fr"
LANG_GERMAN = "de"
LANG_CHINESE = "zh"
LANG_JAPANESE = "ja"

# Notification types
NOTIFICATION_INFO = "info"
NOTIFICATION_SUCCESS = "success"
NOTIFICATION_WARNING = "warning"
NOTIFICATION_ERROR = "error"

# Export options
EXPORT_VIDEO_ONLY = "video_only"
EXPORT_WITH_AUDIO = "with_audio"
EXPORT_SEPARATE_FILES = "separate_files"
EXPORT_PACKAGE = "package"  # ZIP with all files

# Statistics
STAT_TOTAL_PROJECTS = "total_projects"
STAT_TOTAL_GENERATIONS = "total_generations"
STAT_SUCCESS_RATE = "success_rate"
STAT_AVG_PROCESSING_TIME = "avg_processing_time"
STAT_TOTAL_VIDEO_DURATION = "total_video_duration"
STAT_TOTAL_STORAGE_USED = "total_storage_used"
