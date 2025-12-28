"""
File Manager
Utilities for file operations and management
"""

import logging
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FileManager:
    """Manage temporary files and cleanup"""
    
    def __init__(self, temp_dir: str):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def create_temp_file(self, prefix: str = '', suffix: str = '') -> Path:
        """Create a temporary file"""
        import tempfile
        
        fd, path = tempfile.mkstemp(
            prefix=prefix,
            suffix=suffix,
            dir=str(self.temp_dir)
        )
        
        # Close file descriptor
        import os
        os.close(fd)
        
        return Path(path)
    
    def create_temp_dir(self, prefix: str = '') -> Path:
        """Create a temporary directory"""
        import tempfile
        
        path = tempfile.mkdtemp(
            prefix=prefix,
            dir=str(self.temp_dir)
        )
        
        return Path(path)
    
    def cleanup_old_files(self, older_than_hours: int = 24) -> int:
        """
        Clean up old temporary files
        
        Args:
            older_than_hours: Delete files older than this many hours
        
        Returns:
            Number of files deleted
        """
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        deleted_count = 0
        
        try:
            for item in self.temp_dir.rglob('*'):
                if item.is_file():
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    if mtime < cutoff_time:
                        try:
                            item.unlink()
                            deleted_count += 1
                        except Exception as e:
                            logger.warning(f"Could not delete {item}: {e}")
            
            logger.info(f"Cleaned up {deleted_count} old files")
            return deleted_count
        
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return deleted_count
    
    def get_disk_usage(self) -> dict:
        """Get disk usage statistics"""
        total_size = 0
        file_count = 0
        
        try:
            for item in self.temp_dir.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
                    file_count += 1
            
            return {
                'total_size_mb': total_size / (1024 ** 2),
                'file_count': file_count
            }
        
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
            return {'total_size_mb': 0, 'file_count': 0}
    
    def copy_file(self, src: str, dst: str) -> bool:
        """Copy file"""
        try:
            shutil.copy2(src, dst)
            logger.debug(f"Copied: {src} -> {dst}")
            return True
        except Exception as e:
            logger.error(f"Error copying file: {e}")
            return False
    
    def move_file(self, src: str, dst: str) -> bool:
        """Move file"""
        try:
            shutil.move(src, dst)
            logger.debug(f"Moved: {src} -> {dst}")
            return True
        except Exception as e:
            logger.error(f"Error moving file: {e}")
            return False
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        try:
            Path(file_path).unlink()
            logger.debug(f"Deleted: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def list_files(self, pattern: str = '*') -> List[Path]:
        """List files matching pattern"""
        try:
            return list(self.temp_dir.glob(pattern))
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []


class Validators:
    """Input validation utilities"""
    
    @staticmethod
    def validate_text(text: str, max_length: int = 5000) -> tuple[bool, str]:
        """Validate input text"""
        if not text or not text.strip():
            return False, "Text cannot be empty"
        
        if len(text) > max_length:
            return False, f"Text exceeds maximum length ({max_length} characters)"
        
        return True, "Valid text"
    
    @staticmethod
    def validate_audio_file(file_path: str) -> tuple[bool, str]:
        """Validate audio file"""
        path = Path(file_path)
        
        if not path.exists():
            return False, "File does not exist"
        
        if not path.is_file():
            return False, "Not a file"
        
        # Check extension
        valid_extensions = ['.wav', '.mp3', '.ogg', '.flac', '.m4a']
        if path.suffix.lower() not in valid_extensions:
            return False, f"Invalid audio format (supported: {', '.join(valid_extensions)})"
        
        # Check file size (max 50 MB)
        size_mb = path.stat().st_size / (1024 ** 2)
        if size_mb > 50:
            return False, f"File too large ({size_mb:.1f} MB, max 50 MB)"
        
        return True, "Valid audio file"
    
    @staticmethod
    def validate_speed(speed: float) -> tuple[bool, str]:
        """Validate speed parameter"""
        if not 0.5 <= speed <= 2.0:
            return False, "Speed must be between 0.5 and 2.0"
        return True, "Valid speed"
    
    @staticmethod
    def validate_pitch(pitch: float) -> tuple[bool, str]:
        """Validate pitch parameter"""
        if not 0.5 <= pitch <= 2.0:
            return False, "Pitch must be between 0.5 and 2.0"
        return True, "Valid pitch"


if __name__ == '__main__':
    # Test file manager
    from config import paths
    
    manager = FileManager(str(paths.cache_dir))
    
    print("File Manager Test")
    print("=" * 60)
    
    # Create temp file
    temp_file = manager.create_temp_file(prefix='test_', suffix='.txt')
    print(f"Created temp file: {temp_file}")
    
    # Get disk usage
    usage = manager.get_disk_usage()
    print(f"Disk usage: {usage['total_size_mb']:.2f} MB ({usage['file_count']} files)")
    
    # Cleanup
    deleted = manager.cleanup_old_files(older_than_hours=0)
    print(f"Cleaned up {deleted} files")
