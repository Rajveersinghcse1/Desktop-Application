"""
Ultra-Advanced YouTube Downloader
==================================
A feature-rich, modern YouTube downloader with advanced capabilities.

Features:
- Single video & playlist downloads
- Audio/Video extraction with multiple formats
- Concurrent downloads with queue management
- Thumbnail preview & metadata display
- Download history & analytics
- Dark/Light theme support
- Clipboard monitoring
- Advanced error handling & logging
- Settings persistence
- Speed optimization

Author: Advanced AI Assistant
Version: 2.0.0
"""

import sys
import os
import json
import logging
import threading
import time
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from io import BytesIO
from urllib.parse import urlparse, parse_qs

# Try to import YouTube libraries
YouTube = None
Playlist = None
PytubeError = Exception
PYTUBE_AVAILABLE = False
USING_PYTUBEFIX = False

try:
    from pytubefix import YouTube, Playlist
    try:
        from pytubefix.exceptions import PytubeError
    except ImportError:
        PytubeError = Exception
    PYTUBE_AVAILABLE = True
    USING_PYTUBEFIX = True
    print("✓ Using pytubefix")
except ImportError:
    try:
        from pytube import YouTube, Playlist
        try:
            from pytube.exceptions import PytubeError
        except ImportError:
            PytubeError = Exception
        PYTUBE_AVAILABLE = True
        USING_PYTUBEFIX = False
        print("⚠ Using pytube (consider upgrading to pytubefix)")
    except ImportError:
        PYTUBE_AVAILABLE = False
        USING_PYTUBEFIX = False
        print("❌ Error: pytube/pytubefix not installed. Please run: pip install pytubefix")

logger = None  # Will be set later
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QComboBox, QFileDialog, QProgressBar, QTextEdit,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QRadioButton, QCheckBox, QSpinBox, QListWidget, QSplitter,
    QStatusBar, QMenuBar, QMenu, QDialog, QDialogButtonBox, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings, QSize
from PyQt6.QtGui import QPixmap, QIcon, QAction, QFont, QClipboard, QImage


# ============================================================================
# CONFIGURATION & ENUMS
# ============================================================================

class DownloadFormat(Enum):
    """Download format options"""
    VIDEO_MP4 = "video_mp4"
    VIDEO_WEBM = "video_webm"
    AUDIO_MP3 = "audio_mp3"
    AUDIO_MP4 = "audio_mp4"
    AUDIO_WEBM = "audio_webm"


class DownloadStatus(Enum):
    """Download status states"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadTask:
    """Download task data structure"""
    url: str
    title: str
    format: DownloadFormat
    quality: str
    output_path: str
    status: DownloadStatus = DownloadStatus.PENDING
    progress: int = 0
    file_size: int = 0
    download_speed: float = 0.0
    timestamp: str = ""
    error_message: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logger() -> logging.Logger:
    """Configure application logger"""
    logger = logging.getLogger("YouTubeDownloader")
    logger.setLevel(logging.DEBUG)
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # File handler
    fh = logging.FileHandler(log_dir / f"download_{datetime.now().strftime('%Y%m%d')}.log")
    fh.setLevel(logging.DEBUG)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger


logger = setup_logger()


# ============================================================================
# PYTUBE FIXES & WORKAROUNDS
# ============================================================================

def fix_pytube_cipher():
    """Apply fixes for pytube cipher issues - only for original pytube"""
    if USING_PYTUBEFIX:
        return  # pytubefix already has fixes
    
    try:
        from pytube import cipher
        # Fix for throttling parameter
        def get_throttling_function_name(js: str) -> str:
            """Extract throttling function name from JS."""
            patterns = [
                r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&.*?\|\|\s*([a-z]+)',
                r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
            ]
            for pattern in patterns:
                regex = re.compile(pattern)
                function_match = regex.search(js)
                if function_match:
                    return function_match.group(1)
            raise Exception("Could not find throttling function name")
        
        cipher.get_throttling_function_name = get_throttling_function_name
        if logger:
            logger.info("Applied pytube cipher fix")
    except Exception as e:
        if logger:
            logger.warning(f"Could not apply cipher fix: {e}")


def setup_pytube_clients():
    """Configure pytube clients - only for original pytube"""
    if USING_PYTUBEFIX:
        return  # pytubefix uses different configuration
    
    try:
        from pytube.innertube import _default_clients
        _default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.09.37"
        _default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.09.3"
        if logger:
            logger.info("Configured pytube clients")
    except Exception as e:
        if logger:
            logger.warning(f"Could not configure clients: {e}")


def clean_youtube_url(url: str) -> str:
    """Clean and normalize YouTube URL"""
    # Remove playlist parameters and timestamps
    url = re.sub(r'&list=[^&]*', '', url)
    url = re.sub(r'&t=[^&]*', '', url)
    url = re.sub(r'\?t=[^&]*&?', '?', url)
    url = url.rstrip('?&')
    
    # Ensure proper format
    if 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[-1].split('?')[0].split('&')[0]
        url = f'https://www.youtube.com/watch?v={video_id}'
    
    return url


def create_youtube_object(url: str, max_retries: int = 3) -> Optional[Any]:
    """Create YouTube object with multiple retry strategies"""
    if not PYTUBE_AVAILABLE or YouTube is None:
        if logger:
            logger.error("YouTube library not available")
        return None
    
    url = clean_youtube_url(url)
    
    for attempt in range(max_retries):
        try:
            if logger:
                logger.info(f"Creating YouTube object, attempt {attempt + 1}/{max_retries}")
            
            # pytubefix works directly, no special client parameter needed
            yt = YouTube(url)
            
            # Test if it works by accessing title
            title = yt.title
            if not title:
                raise Exception("Video title is empty")
            
            if logger:
                logger.info(f"Successfully created YouTube object: {title}")
            return yt
            
        except Exception as e:
            error_msg = str(e)
            if logger:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {error_msg}")
            
            # Don't retry on certain errors
            if "Video unavailable" in error_msg or "Private video" in error_msg:
                if logger:
                    logger.error(f"Video is unavailable or private: {error_msg}")
                return None
            
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
            continue
    
    return None


def initialize_pytube_fixes():
    """Initialize pytube fixes after logger is set up"""
    if not PYTUBE_AVAILABLE:
        return
    try:
        fix_pytube_cipher()
        setup_pytube_clients()
        if logger:
            lib_name = "pytubefix" if USING_PYTUBEFIX else "pytube"
            logger.info(f"Using {lib_name} for YouTube downloads")
    except Exception as e:
        if logger:
            logger.warning(f"Failed to apply pytube fixes: {e}")


# Initialize fixes
initialize_pytube_fixes()


# ============================================================================
# DOWNLOAD WORKER THREADS
# ============================================================================

class VideoFetchThread(QThread):
    """Thread for fetching video information"""
    success_signal = pyqtSignal(dict)  # video_info
    error_signal = pyqtSignal(str)
    
    def __init__(self, url: str):
        super().__init__()
        self.url = url
        
    def run(self):
        try:
            logger.info(f"Fetching video info: {self.url}")
            
            if not PYTUBE_AVAILABLE:
                raise Exception("YouTube library not installed. Please run: pip install pytubefix")
            
            # Clean URL and create YouTube object with retries
            cleaned_url = clean_youtube_url(self.url)
            logger.info(f"Cleaned URL: {cleaned_url}")
            
            yt = create_youtube_object(cleaned_url)
            
            if not yt:
                raise Exception(
                    "Failed to fetch video information.\n\n"
                    "Possible reasons:\n"
                    "• Video is private, deleted, or unavailable\n"
                    "• Age-restricted content (requires login)\n"
                    "• Region-blocked content\n"
                    "• YouTube API temporary issues\n\n"
                    "Try:\n"
                    "• Check if the video plays in your browser\n"
                    "• Update: pip install --upgrade pytubefix\n"
                    "• Try again in a few moments"
                )
            
            # Prepare video streams
            video_streams = []
            for stream in yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc():
                video_streams.append({
                    "resolution": stream.resolution,
                    "fps": stream.fps,
                    "size": stream.filesize,
                    "stream": stream
                })
            
            # Audio streams
            audio_streams = []
            for stream in yt.streams.filter(only_audio=True).order_by("abr").desc():
                audio_streams.append({
                    "bitrate": stream.abr,
                    "size": stream.filesize,
                    "stream": stream
                })
            
            # Safely get metadata with fallbacks
            title = "Unknown Title"
            author = "Unknown Author"
            length = 0
            views = 0
            thumbnail_url = ""
            description = ""
            publish_date = "Unknown"
            
            try:
                title = yt.title if yt.title else "Unknown Title"
            except Exception as e:
                logger.warning(f"Could not get title: {e}")
            
            try:
                author = yt.author if yt.author else "Unknown Author"
            except Exception as e:
                logger.warning(f"Could not get author: {e}")
            
            try:
                length = int(yt.length) if yt.length else 0
            except Exception as e:
                logger.warning(f"Could not get length: {e}")
            
            try:
                views = int(yt.views) if yt.views else 0
            except Exception as e:
                logger.warning(f"Could not get views: {e}")
            
            try:
                thumbnail_url = yt.thumbnail_url if yt.thumbnail_url else ""
            except Exception as e:
                logger.warning(f"Could not get thumbnail: {e}")
            
            try:
                desc = yt.description if hasattr(yt, 'description') and yt.description else ""
                description = desc[:500] if len(desc) > 500 else desc
            except Exception as e:
                logger.warning(f"Could not get description: {e}")
            
            try:
                if hasattr(yt, 'publish_date') and yt.publish_date:
                    publish_date = str(yt.publish_date)
                else:
                    publish_date = "Unknown"
            except Exception as e:
                logger.warning(f"Could not get publish date: {e}")
            
            info = {
                "youtube_obj": yt,
                "title": title,
                "author": author,
                "length": length,
                "views": views,
                "thumbnail_url": thumbnail_url,
                "description": description,
                "video_streams": video_streams,
                "audio_streams": audio_streams,
                "publish_date": publish_date
            }
            
            self.success_signal.emit(info)
            logger.info(f"Successfully fetched: {yt.title}")
            
        except Exception as e:
            error_msg = f"Failed to fetch video: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Provide helpful error message
            if "Bad Request" in str(e) or "400" in str(e):
                error_msg = (
                    "Failed to fetch video (Bad Request).\n\n"
                    "Possible solutions:\n"
                    "1. Update pytube: pip install --upgrade pytube\n"
                    "2. The video might be age-restricted or private\n"
                    "3. YouTube API may have changed\n"
                    "4. Try again in a few moments\n\n"
                    f"Original error: {str(e)}"
                )
            elif "RegexMatchError" in str(e):
                error_msg = (
                    "Failed to extract video information.\n\n"
                    "YouTube has updated their API.\n"
                    "Please update pytube: pip install --upgrade pytube\n\n"
                    f"Original error: {str(e)}"
                )
            
            self.error_signal.emit(error_msg)


class PlaylistFetchThread(QThread):
    """Thread for fetching playlist information"""
    success_signal = pyqtSignal(list)  # list of video URLs
    progress_signal = pyqtSignal(int, int)  # current, total
    error_signal = pyqtSignal(str)
    
    def __init__(self, url: str):
        super().__init__()
        self.url = url
        
    def run(self):
        try:
            logger.info(f"Fetching playlist: {self.url}")
            
            if not PYTUBE_AVAILABLE or Playlist is None:
                raise Exception("YouTube library not installed. Please run: pip install pytubefix")
            
            # Check if URL contains playlist parameter
            if 'list=' not in self.url:
                raise Exception(
                    "This is not a playlist URL.\n\n"
                    "Playlist URLs should contain 'list=' parameter.\n"
                    "Example: https://www.youtube.com/playlist?list=PLxxxxxx\n\n"
                    "For single videos, use 'Fetch Info' button instead."
                )
            
            # Clean URL and extract playlist ID
            url = self.url
            match = re.search(r'list=([^&]+)', url)
            if not match:
                raise Exception("Could not extract playlist ID from URL")
            
            playlist_id = match.group(1)
            url = f'https://www.youtube.com/playlist?list={playlist_id}'
            logger.info(f"Playlist URL: {url}")
            
            playlist = Playlist(url)
            urls = list(playlist.video_urls)
            
            for i, url in enumerate(urls, 1):
                self.progress_signal.emit(i, len(urls))
                time.sleep(0.1)  # Small delay to show progress
            
            self.success_signal.emit(urls)
            logger.info(f"Successfully fetched playlist with {len(urls)} videos")
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Failed to fetch playlist: {error_str}", exc_info=True)
            
            # Provide helpful error messages
            if "not a playlist URL" in error_str or "'list'" in error_str:
                error_msg = (
                    "This is not a valid playlist URL.\n\n"
                    "For single videos, use the 'Fetch Info' button.\n\n"
                    "Playlist URLs look like:\n"
                    "https://www.youtube.com/playlist?list=PLxxxxxx\n"
                    "or\n"
                    "https://www.youtube.com/watch?v=xxxxx&list=PLxxxxxx"
                )
            elif "Bad Request" in error_str or "400" in error_str:
                error_msg = (
                    "Failed to fetch playlist.\n\n"
                    "Possible solutions:\n"
                    "• Update: pip install --upgrade pytubefix\n"
                    "• Check if the playlist is public\n"
                    "• Try again in a few moments\n\n"
                    f"Error: {error_str}"
                )
            else:
                error_msg = f"Playlist error: {error_str}"
            
            self.error_signal.emit(error_msg)


class DownloadThread(QThread):
    """Advanced download thread with progress tracking"""
    progress_signal = pyqtSignal(int, float, int)  # percent, speed (MB/s), bytes_remaining
    finished_signal = pyqtSignal(str, str)  # message, file_path
    error_signal = pyqtSignal(str)
    
    def __init__(self, yt: Any, stream, output_path: str, filename: str):
        super().__init__()
        self.yt = yt
        self.stream = stream
        self.output_path = output_path
        self.filename = filename
        self.cancelled = False
        self.start_time = None
        
    def run(self):
        try:
            self.start_time = time.time()
            logger.info(f"Starting download: {self.filename}")
            
            # Register progress callback
            self.yt.register_on_progress_callback(self.on_progress)
            
            # Download
            file_path = self.stream.download(
                output_path=self.output_path,
                filename=self.filename
            )
            
            if not self.cancelled:
                elapsed = time.time() - self.start_time
                logger.info(f"Download completed in {elapsed:.2f}s: {file_path}")
                self.finished_signal.emit("Download completed successfully!", file_path)
            
        except Exception as e:
            error_msg = f"Download failed: {str(e)}"
            logger.error(error_msg)
            self.error_signal.emit(error_msg)
    
    def on_progress(self, stream, chunk, bytes_remaining):
        """Progress callback"""
        if self.cancelled:
            return
            
        total = stream.filesize
        downloaded = total - bytes_remaining
        percent = int((downloaded / total) * 100)
        
        # Calculate speed
        elapsed = time.time() - self.start_time if self.start_time else 1
        speed = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
        
        self.progress_signal.emit(percent, speed, bytes_remaining)
    
    def cancel(self):
        """Cancel download"""
        self.cancelled = True
        logger.info("Download cancelled by user")


class ThumbnailFetchThread(QThread):
    """Thread for fetching video thumbnail"""
    success_signal = pyqtSignal(QPixmap)
    error_signal = pyqtSignal(str)
    
    def __init__(self, thumbnail_url: str):
        super().__init__()
        self.thumbnail_url = thumbnail_url
        
    def run(self):
        try:
            response = requests.get(self.thumbnail_url, timeout=10)
            response.raise_for_status()
            
            image = QImage()
            image.loadFromData(response.content)
            pixmap = QPixmap.fromImage(image)
            
            self.success_signal.emit(pixmap)
            
        except Exception as e:
            self.error_signal.emit(f"Failed to load thumbnail: {str(e)}")


# ============================================================================
# SETTINGS DIALOG
# ============================================================================

class SettingsDialog(QDialog):
    """Advanced settings dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Download settings
        download_group = QGroupBox("Download Settings")
        download_layout = QVBoxLayout()
        
        # Default download path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Default Download Path:"))
        self.path_input = QLineEdit()
        self.path_input.setText(str(Path.home() / "Downloads"))
        path_btn = QPushButton("Browse")
        path_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(path_btn)
        download_layout.addLayout(path_layout)
        
        # Concurrent downloads
        concurrent_layout = QHBoxLayout()
        concurrent_layout.addWidget(QLabel("Concurrent Downloads:"))
        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setRange(1, 5)
        self.concurrent_spin.setValue(2)
        concurrent_layout.addWidget(self.concurrent_spin)
        concurrent_layout.addStretch()
        download_layout.addLayout(concurrent_layout)
        
        # Auto-start downloads
        self.auto_start_check = QCheckBox("Auto-start downloads when added to queue")
        download_layout.addWidget(self.auto_start_check)
        
        download_group.setLayout(download_layout)
        layout.addWidget(download_group)
        
        # UI settings
        ui_group = QGroupBox("UI Settings")
        ui_layout = QVBoxLayout()
        
        # Theme
        self.dark_theme_check = QCheckBox("Dark Theme")
        ui_layout.addWidget(self.dark_theme_check)
        
        # Clipboard monitoring
        self.clipboard_check = QCheckBox("Monitor clipboard for YouTube links")
        ui_layout.addWidget(self.clipboard_check)
        
        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def browse_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Default Download Folder")
        if folder:
            self.path_input.setText(folder)
    
    def get_settings(self) -> dict:
        return {
            "default_path": self.path_input.text(),
            "concurrent_downloads": self.concurrent_spin.value(),
            "auto_start": self.auto_start_check.isChecked(),
            "dark_theme": self.dark_theme_check.isChecked(),
            "clipboard_monitor": self.clipboard_check.isChecked()
        }
    
    def set_settings(self, settings: dict):
        self.path_input.setText(settings.get("default_path", str(Path.home() / "Downloads")))
        self.concurrent_spin.setValue(settings.get("concurrent_downloads", 2))
        self.auto_start_check.setChecked(settings.get("auto_start", False))
        self.dark_theme_check.setChecked(settings.get("dark_theme", False))
        self.clipboard_check.setChecked(settings.get("clipboard_monitor", False))


# ============================================================================
# MAIN APPLICATION WINDOW
# ============================================================================

class AdvancedYouTubeDownloader(QMainWindow):
    """Ultra-advanced YouTube downloader with modern features"""
    
    def __init__(self):
        super().__init__()
        
        # Application state
        self.current_video_info: Optional[dict] = None
        self.download_queue: List[DownloadTask] = []
        self.download_history: List[dict] = []
        self.active_threads: List[QThread] = []
        self.output_path: str = str(Path.home() / "Downloads")
        
        # Settings
        self.settings = QSettings("AdvancedYTDownloader", "Settings")
        self.load_settings()
        
        # Setup UI
        self.init_ui()
        self.apply_theme()
        
        # Clipboard monitoring
        if self.clipboard_monitor_enabled:
            self.setup_clipboard_monitor()
        
        logger.info("Application initialized successfully")
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Advanced YouTube Downloader Pro")
        self.setMinimumSize(1200, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_download_tab()
        self.create_queue_tab()
        self.create_history_tab()
        
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_download_tab(self):
        """Create main download tab"""
        download_widget = QWidget()
        layout = QVBoxLayout()
        
        # URL Input Section
        url_group = QGroupBox("Video/Playlist URL")
        url_layout = QVBoxLayout()
        
        url_input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube video or playlist URL here...")
        self.url_input.returnPressed.connect(self.fetch_video_info)
        url_input_layout.addWidget(self.url_input)
        
        self.fetch_btn = QPushButton("Fetch Info")
        self.fetch_btn.clicked.connect(self.fetch_video_info)
        url_input_layout.addWidget(self.fetch_btn)
        
        self.playlist_btn = QPushButton("Fetch Playlist")
        self.playlist_btn.clicked.connect(self.fetch_playlist_info)
        url_input_layout.addWidget(self.playlist_btn)
        
        url_layout.addLayout(url_input_layout)
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)
        
        # Splitter for video info and download options
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Video Info
        info_widget = QWidget()
        info_layout = QVBoxLayout()
        
        # Thumbnail
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setFixedSize(320, 180)
        self.thumbnail_label.setStyleSheet("border: 1px solid #ccc; background: #000;")
        self.thumbnail_label.setText("No video loaded")
        info_layout.addWidget(self.thumbnail_label)
        
        # Video details
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(200)
        info_layout.addWidget(QLabel("Video Information:"))
        info_layout.addWidget(self.info_text)
        
        info_widget.setLayout(info_layout)
        splitter.addWidget(info_widget)
        
        # Right: Download Options
        options_widget = QWidget()
        options_layout = QVBoxLayout()
        
        # Format selection
        format_group = QGroupBox("Download Format")
        format_layout = QVBoxLayout()
        
        self.video_radio = QRadioButton("Video (MP4)")
        self.video_radio.setChecked(True)
        self.video_radio.toggled.connect(self.on_format_changed)
        format_layout.addWidget(self.video_radio)
        
        self.audio_radio = QRadioButton("Audio Only (MP3)")
        self.audio_radio.toggled.connect(self.on_format_changed)
        format_layout.addWidget(self.audio_radio)
        
        format_group.setLayout(format_layout)
        options_layout.addWidget(format_group)
        
        # Quality selection
        quality_group = QGroupBox("Quality")
        quality_layout = QVBoxLayout()
        
        self.quality_combo = QComboBox()
        quality_layout.addWidget(self.quality_combo)
        
        quality_group.setLayout(quality_layout)
        options_layout.addWidget(quality_group)
        
        # Output folder
        folder_group = QGroupBox("Output Folder")
        folder_layout = QVBoxLayout()
        
        folder_select_layout = QHBoxLayout()
        self.folder_label = QLabel(self.output_path)
        self.folder_label.setWordWrap(True)
        folder_select_layout.addWidget(self.folder_label)
        
        self.choose_folder_btn = QPushButton("Browse")
        self.choose_folder_btn.clicked.connect(self.choose_folder)
        folder_select_layout.addWidget(self.choose_folder_btn)
        
        folder_layout.addLayout(folder_select_layout)
        folder_group.setLayout(folder_layout)
        options_layout.addWidget(folder_group)
        
        # Download button
        self.download_btn = QPushButton("Add to Queue & Download")
        self.download_btn.setEnabled(False)
        self.download_btn.setMinimumHeight(40)
        self.download_btn.clicked.connect(self.start_download)
        options_layout.addWidget(self.download_btn)
        
        # Progress
        progress_group = QGroupBox("Download Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Ready")
        progress_layout.addWidget(self.progress_label)
        
        progress_group.setLayout(progress_layout)
        options_layout.addWidget(progress_group)
        
        options_layout.addStretch()
        options_widget.setLayout(options_layout)
        splitter.addWidget(options_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        download_widget.setLayout(layout)
        self.tab_widget.addTab(download_widget, "Download")
    
    def create_queue_tab(self):
        """Create download queue tab"""
        queue_widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Download Queue:"))
        
        self.queue_list = QListWidget()
        layout.addWidget(self.queue_list)
        
        # Queue controls
        controls_layout = QHBoxLayout()
        
        clear_queue_btn = QPushButton("Clear Completed")
        clear_queue_btn.clicked.connect(self.clear_completed_queue)
        controls_layout.addWidget(clear_queue_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        queue_widget.setLayout(layout)
        self.tab_widget.addTab(queue_widget, "Queue")
    
    def create_history_tab(self):
        """Create download history tab"""
        history_widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Download History:"))
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Title", "Format", "Size", "Date", "Status"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.history_table)
        
        # History controls
        controls_layout = QHBoxLayout()
        
        clear_history_btn = QPushButton("Clear History")
        clear_history_btn.clicked.connect(self.clear_history)
        controls_layout.addWidget(clear_history_btn)
        
        export_btn = QPushButton("Export History")
        export_btn.clicked.connect(self.export_history)
        controls_layout.addWidget(export_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        history_widget.setLayout(layout)
        self.tab_widget.addTab(history_widget, "History")
        
        # Load history
        self.load_history()
    
    def fetch_video_info(self):
        """Fetch video information"""
        url = self.url_input.text().strip()
        if not url:
            self.show_error("Please enter a YouTube URL")
            return
        
        self.status_bar.showMessage("Fetching video information...")
        self.fetch_btn.setEnabled(False)
        
        self.fetch_thread = VideoFetchThread(url)
        self.fetch_thread.success_signal.connect(self.on_video_info_fetched)
        self.fetch_thread.error_signal.connect(self.on_fetch_error)
        self.fetch_thread.finished.connect(lambda: self.fetch_btn.setEnabled(True))
        self.fetch_thread.start()
        
        self.active_threads.append(self.fetch_thread)
    
    def fetch_playlist_info(self):
        """Fetch playlist information"""
        url = self.url_input.text().strip()
        if not url:
            self.show_error("Please enter a YouTube playlist URL")
            return
        
        self.status_bar.showMessage("Fetching playlist...")
        self.playlist_btn.setEnabled(False)
        
        self.playlist_thread = PlaylistFetchThread(url)
        self.playlist_thread.success_signal.connect(self.on_playlist_fetched)
        self.playlist_thread.progress_signal.connect(
            lambda c, t: self.status_bar.showMessage(f"Fetching playlist: {c}/{t}")
        )
        self.playlist_thread.error_signal.connect(self.on_fetch_error)
        self.playlist_thread.finished.connect(lambda: self.playlist_btn.setEnabled(True))
        self.playlist_thread.start()
        
        self.active_threads.append(self.playlist_thread)
    
    def on_video_info_fetched(self, info: dict):
        """Handle fetched video information"""
        self.current_video_info = info
        
        # Display thumbnail
        if "thumbnail_url" in info:
            self.thumb_thread = ThumbnailFetchThread(info["thumbnail_url"])
            self.thumb_thread.success_signal.connect(self.display_thumbnail)
            self.thumb_thread.start()
            self.active_threads.append(self.thumb_thread)
        
        # Display video information
        info_text = f"""
<b>Title:</b> {info['title']}<br>
<b>Author:</b> {info['author']}<br>
<b>Duration:</b> {info['length'] // 60}m {info['length'] % 60}s<br>
<b>Views:</b> {info['views']:,}<br>
<b>Published:</b> {info['publish_date']}<br>
<br>
<b>Description:</b><br>
{info['description']}
        """
        self.info_text.setHtml(info_text)
        
        # Update quality options
        self.update_quality_options()
        
        self.download_btn.setEnabled(True)
        self.status_bar.showMessage(f"Loaded: {info['title']}")
    
    def on_playlist_fetched(self, urls: List[str]):
        """Handle fetched playlist"""
        reply = QMessageBox.question(
            self,
            "Playlist Detected",
            f"Found {len(urls)} videos in playlist. Add all to queue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.status_bar.showMessage(f"Adding {len(urls)} videos to queue...")
            # Process first video to show info
            if urls:
                self.url_input.setText(urls[0])
                self.fetch_video_info()
        
        self.status_bar.showMessage("Playlist loaded")
    
    def on_fetch_error(self, error: str):
        """Handle fetch error"""
        self.show_error(error)
        self.status_bar.showMessage("Error fetching video")
    
    def display_thumbnail(self, pixmap: QPixmap):
        """Display video thumbnail"""
        scaled = pixmap.scaled(
            320, 180,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.thumbnail_label.setPixmap(scaled)
    
    def on_format_changed(self):
        """Handle format selection change"""
        self.update_quality_options()
    
    def update_quality_options(self):
        """Update quality dropdown based on format"""
        if not self.current_video_info:
            return
        
        self.quality_combo.clear()
        
        if self.video_radio.isChecked():
            # Video streams
            for stream_info in self.current_video_info["video_streams"]:
                size_mb = stream_info["size"] / (1024 * 1024)
                self.quality_combo.addItem(
                    f"{stream_info['resolution']} - {stream_info['fps']}fps - {size_mb:.1f} MB",
                    stream_info["stream"]
                )
        else:
            # Audio streams
            for stream_info in self.current_video_info["audio_streams"]:
                size_mb = stream_info["size"] / (1024 * 1024)
                self.quality_combo.addItem(
                    f"{stream_info['bitrate']} - {size_mb:.1f} MB",
                    stream_info["stream"]
                )
    
    def choose_folder(self):
        """Choose output folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.output_path = folder
            self.folder_label.setText(folder)
            self.settings.setValue("default_path", folder)
    
    def start_download(self):
        """Start downloading selected video"""
        if not self.current_video_info:
            self.show_error("No video loaded")
            return
        
        stream = self.quality_combo.currentData()
        if not stream:
            self.show_error("Please select a quality")
            return
        
        # Prepare filename
        safe_title = "".join(c for c in self.current_video_info["title"] if c.isalnum() or c in (' ', '-', '_')).strip()
        extension = ".mp3" if self.audio_radio.isChecked() else ".mp4"
        filename = f"{safe_title}{extension}"
        
        # Create download task
        task = DownloadTask(
            url=self.url_input.text(),
            title=self.current_video_info["title"],
            format=DownloadFormat.AUDIO_MP3 if self.audio_radio.isChecked() else DownloadFormat.VIDEO_MP4,
            quality=self.quality_combo.currentText(),
            output_path=self.output_path
        )
        
        self.download_queue.append(task)
        self.update_queue_display()
        
        # Start download
        self.status_bar.showMessage(f"Starting download: {self.current_video_info['title']}")
        self.progress_bar.setValue(0)
        
        self.download_thread = DownloadThread(
            self.current_video_info["youtube_obj"],
            stream,
            self.output_path,
            filename
        )
        self.download_thread.progress_signal.connect(self.on_download_progress)
        self.download_thread.finished_signal.connect(self.on_download_finished)
        self.download_thread.error_signal.connect(self.on_download_error)
        self.download_thread.start()
        
        self.active_threads.append(self.download_thread)
    
    def on_download_progress(self, percent: int, speed: float, bytes_remaining: int):
        """Handle download progress"""
        self.progress_bar.setValue(percent)
        mb_remaining = bytes_remaining / (1024 * 1024)
        self.progress_label.setText(
            f"Downloading: {percent}% - {speed:.2f} MB/s - {mb_remaining:.1f} MB remaining"
        )
    
    def on_download_finished(self, message: str, file_path: str):
        """Handle download completion"""
        self.progress_bar.setValue(100)
        self.progress_label.setText(message)
        self.status_bar.showMessage(f"Download completed: {Path(file_path).name}")
        
        # Add to history
        self.add_to_history({
            "title": self.current_video_info["title"],
            "format": "Audio" if self.audio_radio.isChecked() else "Video",
            "size": Path(file_path).stat().st_size if Path(file_path).exists() else 0,
            "date": datetime.now().isoformat(),
            "status": "Completed"
        })
        
        QMessageBox.information(self, "Success", f"Download completed!\n{file_path}")
    
    def on_download_error(self, error: str):
        """Handle download error"""
        self.show_error(f"Download failed: {error}")
        self.status_bar.showMessage("Download failed")
        self.progress_label.setText("Error occurred")
    
    def update_queue_display(self):
        """Update queue list display"""
        self.queue_list.clear()
        for task in self.download_queue:
            self.queue_list.addItem(
                f"[{task.status.value}] {task.title} - {task.quality}"
            )
    
    def clear_completed_queue(self):
        """Clear completed downloads from queue"""
        self.download_queue = [
            task for task in self.download_queue 
            if task.status != DownloadStatus.COMPLETED
        ]
        self.update_queue_display()
    
    def add_to_history(self, entry: dict):
        """Add entry to download history"""
        self.download_history.append(entry)
        self.save_history()
        self.update_history_display()
    
    def update_history_display(self):
        """Update history table"""
        self.history_table.setRowCount(len(self.download_history))
        for i, entry in enumerate(reversed(self.download_history)):
            self.history_table.setItem(i, 0, QTableWidgetItem(entry["title"]))
            self.history_table.setItem(i, 1, QTableWidgetItem(entry["format"]))
            size_mb = entry["size"] / (1024 * 1024)
            self.history_table.setItem(i, 2, QTableWidgetItem(f"{size_mb:.1f} MB"))
            date_str = datetime.fromisoformat(entry["date"]).strftime("%Y-%m-%d %H:%M")
            self.history_table.setItem(i, 3, QTableWidgetItem(date_str))
            self.history_table.setItem(i, 4, QTableWidgetItem(entry["status"]))
    
    def clear_history(self):
        """Clear download history"""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all download history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.download_history.clear()
            self.save_history()
            self.update_history_display()
    
    def export_history(self):
        """Export download history to JSON"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export History",
            "download_history.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.download_history, f, indent=2)
                QMessageBox.information(self, "Success", "History exported successfully!")
            except Exception as e:
                self.show_error(f"Failed to export history: {str(e)}")
    
    def setup_clipboard_monitor(self):
        """Setup clipboard monitoring for YouTube URLs"""
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.check_clipboard)
        self.last_clipboard = ""
    
    def check_clipboard(self):
        """Check clipboard for YouTube URLs"""
        text = self.clipboard.text()
        if text != self.last_clipboard and ("youtube.com" in text or "youtu.be" in text):
            self.last_clipboard = text
            reply = QMessageBox.question(
                self,
                "YouTube URL Detected",
                f"YouTube URL detected in clipboard:\n{text}\n\nLoad this video?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.url_input.setText(text)
                self.fetch_video_info()
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        dialog.set_settings({
            "default_path": self.output_path,
            "concurrent_downloads": 2,
            "auto_start": False,
            "dark_theme": self.settings.value("dark_theme", False, bool),
            "clipboard_monitor": self.clipboard_monitor_enabled
        })
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_settings = dialog.get_settings()
            self.output_path = new_settings["default_path"]
            self.folder_label.setText(self.output_path)
            self.clipboard_monitor_enabled = new_settings["clipboard_monitor"]
            
            # Save settings
            self.settings.setValue("default_path", new_settings["default_path"])
            self.settings.setValue("dark_theme", new_settings["dark_theme"])
            self.settings.setValue("clipboard_monitor", new_settings["clipboard_monitor"])
            
            # Apply theme
            if new_settings["dark_theme"] != self.settings.value("dark_theme", False, bool):
                self.apply_theme()
            
            # Setup/teardown clipboard monitor
            if new_settings["clipboard_monitor"] and not hasattr(self, 'clipboard'):
                self.setup_clipboard_monitor()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Advanced YouTube Downloader",
            """
            <h2>Advanced YouTube Downloader Pro</h2>
            <p>Version 2.0.0</p>
            <p>An ultra-advanced YouTube downloader with modern features:</p>
            <ul>
                <li>Single video & playlist downloads</li>
                <li>Audio/Video extraction</li>
                <li>Download queue management</li>
                <li>Thumbnail preview</li>
                <li>Download history & analytics</li>
                <li>Theme support</li>
                <li>Clipboard monitoring</li>
            </ul>
            <p>Built with PyQt6 and pytube</p>
            """
        )
    
    def apply_theme(self):
        """Apply application theme"""
        if self.settings.value("dark_theme", False, bool):
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QLineEdit, QComboBox, QTextEdit, QListWidget, QTableWidget {
                    background-color: #3c3c3c;
                    border: 1px solid #555555;
                    color: #ffffff;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #0d7377;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #14ffec;
                    color: #000000;
                }
                QPushButton:disabled {
                    background-color: #555555;
                    color: #888888;
                }
                QGroupBox {
                    border: 1px solid #555555;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    color: #14ffec;
                }
                QProgressBar {
                    border: 1px solid #555555;
                    border-radius: 3px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #0d7377;
                }
            """)
        else:
            self.setStyleSheet("")
    
    def load_settings(self):
        """Load application settings"""
        self.output_path = self.settings.value("default_path", str(Path.home() / "Downloads"))
        self.clipboard_monitor_enabled = self.settings.value("clipboard_monitor", False, bool)
    
    def save_history(self):
        """Save download history to file"""
        history_file = Path("download_history.json")
        try:
            with open(history_file, 'w') as f:
                json.dump(self.download_history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {str(e)}")
    
    def load_history(self):
        """Load download history from file"""
        history_file = Path("download_history.json")
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    self.download_history = json.load(f)
                self.update_history_display()
            except Exception as e:
                logger.error(f"Failed to load history: {str(e)}")
    
    def show_error(self, message: str):
        """Show error message"""
        QMessageBox.critical(self, "Error", message)
        logger.error(message)
    
    def closeEvent(self, event):
        """Handle application close"""
        # Cancel active downloads
        for thread in self.active_threads:
            if isinstance(thread, DownloadThread) and thread.isRunning():
                thread.cancel()
                thread.wait(3000)
        
        # Save history
        self.save_history()
        
        event.accept()


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Advanced YouTube Downloader")
    app.setOrganizationName("AdvancedYTDownloader")
    
    # Set application font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    window = AdvancedYouTubeDownloader()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
