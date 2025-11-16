"""Utility helper functions for OpenUP."""

import os
import mimetypes
import humanize
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def ensure_directories():
    """Ensure all required application directories exist."""
    config_dir = Path.home() / '.openup'
    required_dirs = [
        config_dir,
        config_dir / 'cache',
        config_dir / 'cache' / 'metadata',
        config_dir / 'cache' / 'thumbnails',
        config_dir / 'cache' / 'processed',
        config_dir / 'logs',
    ]
    
    for dir_path in required_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    logger.debug("Application directories ensured")


def get_file_info(filepath: str) -> dict:
    """
    Get basic file information.
    
    Args:
        filepath: Absolute path to file
        
    Returns:
        Dictionary with file info
    """
    path = Path(filepath)
    
    if not path.exists():
        return {
            'exists': False,
            'name': path.name,
            'path': str(path),
        }
    
    stat = path.stat()
    
    return {
        'exists': True,
        'name': path.name,
        'path': str(path.absolute()),
        'directory': str(path.parent),
        'extension': path.suffix.lower(),
        'size_bytes': stat.st_size,
        'size_human': humanize.naturalsize(stat.st_size),
        'modified': stat.st_mtime,
        'modified_human': humanize.naturaltime(stat.st_mtime),
        'mime_type': get_mime_type(filepath),
        'is_file': path.is_file(),
        'is_dir': path.is_dir(),
    }


def get_mime_type(filepath: str) -> Optional[str]:
    """
    Get MIME type for file.
    
    Args:
        filepath: Absolute path to file
        
    Returns:
        MIME type string or None
    """
    mime_type, _ = mimetypes.guess_type(filepath)
    return mime_type


def format_file_size(size_bytes: int) -> str:
    """
    Format file size to human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    return humanize.naturalsize(size_bytes, binary=True)


def is_text_file(filepath: str, sample_size: int = 8192) -> bool:
    """
    Check if file is likely a text file.
    
    Args:
        filepath: Absolute path to file
        sample_size: Number of bytes to sample
        
    Returns:
        True if file appears to be text, False otherwise
    """
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(sample_size)
        
        # Check for null bytes (binary indicator)
        if b'\x00' in chunk:
            return False
        
        # Try to decode as UTF-8
        try:
            chunk.decode('utf-8')
            return True
        except UnicodeDecodeError:
            # Try other encodings
            for encoding in ['latin-1', 'cp1252']:
                try:
                    chunk.decode(encoding)
                    return True
                except UnicodeDecodeError:
                    continue
        
        return False
    except Exception:
        return False


def safe_filename(filename: str) -> str:
    """
    Convert string to safe filename.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    safe = ''.join(c if c not in unsafe_chars else '_' for c in filename)
    
    # Limit length
    if len(safe) > 255:
        name, ext = os.path.splitext(safe)
        safe = name[:255-len(ext)] + ext
    
    return safe


def get_extension_domain(extension: str) -> str:
    """
    Map file extension to domain category.
    
    Args:
        extension: File extension (with or without dot)
        
    Returns:
        Domain string
    """
    if not extension.startswith('.'):
        extension = '.' + extension
    
    extension = extension.lower()
    
    # Domain mappings
    domains = {
        'Documents': ['.txt', '.md', '.pdf', '.docx', '.doc', '.odt', '.rtf'],
        'Data': ['.csv', '.tsv', '.xlsx', '.xls', '.json', '.xml', '.parquet', '.feather'],
        'Images': ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif', '.webp', '.svg'],
        'Audio': ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a'],
        'Video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'],
        'Geospatial': ['.las', '.laz', '.shp', '.geojson', '.kml', '.gpx'],
        'Medical': ['.dcm', '.nii', '.nii.gz', '.edf'],
        '3D': ['.obj', '.stl', '.ply', '.fbx', '.gltf', '.glb'],
        'Code': ['.py', '.js', '.ts', '.html', '.css', '.c', '.cpp', '.java', '.yaml', '.toml', '.go', '.rs'],
        'Archives': ['.zip', '.tar', '.gz', '.tar.gz', '.rar', '.7z'],
    }
    
    for domain, extensions in domains.items():
        if extension in extensions:
            return domain
    
    return 'Unknown'


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def parse_csv_delimiter(filepath: str, sample_size: int = 4096) -> str:
    """
    Detect CSV delimiter.
    
    Args:
        filepath: Path to CSV file
        sample_size: Number of bytes to sample
        
    Returns:
        Detected delimiter character
    """
    import csv
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            sample = f.read(sample_size)
        
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample).delimiter
        return delimiter
    except Exception:
        return ','  # Default to comma


def get_video_thumbnail_time(duration: float) -> float:
    """
    Calculate optimal time for video thumbnail.
    
    Args:
        duration: Video duration in seconds
        
    Returns:
        Time in seconds for thumbnail
    """
    # Use 10% into video, but at least 1 second, max 30 seconds
    time = max(1.0, min(duration * 0.1, 30.0))
    return time


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max."""
    return max(min_val, min(value, max_val))


class FileWatcher:
    """Watch file for changes."""
    
    def __init__(self, filepath: str):
        """Initialize file watcher."""
        self.filepath = Path(filepath)
        self.last_mtime = self._get_mtime()
    
    def _get_mtime(self) -> float:
        """Get file modification time."""
        if self.filepath.exists():
            return self.filepath.stat().st_mtime
        return 0.0
    
    def has_changed(self) -> bool:
        """Check if file has changed."""
        current_mtime = self._get_mtime()
        if current_mtime != self.last_mtime:
            self.last_mtime = current_mtime
            return True
        return False
