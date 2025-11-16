"""Cache management for OpenUP."""

import json
import pickle
import hashlib
import logging
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timedelta


class CacheManager:
    """
    Manages caching of metadata, thumbnails, and processed data.
    
    Cache structure:
    cache/
      metadata/  - JSON metadata files
      thumbnails/  - Image thumbnails
      processed/  - Processed data (downsampled point clouds, etc.)
    """
    
    def __init__(self, cache_dir: Path, max_size_mb: int = 500):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Root cache directory
            max_size_mb: Maximum cache size in megabytes
        """
        self.logger = logging.getLogger(__name__)
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        
        # Create cache subdirectories
        self.metadata_dir = self.cache_dir / 'metadata'
        self.thumbnail_dir = self.cache_dir / 'thumbnails'
        self.processed_dir = self.cache_dir / 'processed'
        
        for dir_path in [self.metadata_dir, self.thumbnail_dir, self.processed_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        self.logger.info(f"CacheManager initialized at {self.cache_dir}")
        
    def _get_cache_key(self, filepath: str, suffix: str = '') -> str:
        """
        Generate cache key from filepath.
        
        Args:
            filepath: Absolute file path
            suffix: Optional suffix for cache key
            
        Returns:
            Hash-based cache key
        """
        path = Path(filepath)
        # Include modification time in key
        mtime = path.stat().st_mtime if path.exists() else 0
        key_str = f"{filepath}:{mtime}{suffix}"
        return hashlib.md5(key_str.encode()).hexdigest()
        
    def get_metadata(self, filepath: str) -> Optional[dict]:
        """
        Retrieve cached metadata for file.
        
        Args:
            filepath: Absolute file path
            
        Returns:
            Cached metadata dict or None if not found
        """
        cache_key = self._get_cache_key(filepath, ':metadata')
        cache_file = self.metadata_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.logger.debug(f"Cache hit for metadata: {filepath}")
                    return data
            except Exception as e:
                self.logger.warning(f"Failed to load cached metadata: {e}")
                cache_file.unlink(missing_ok=True)
        return None
        
    def set_metadata(self, filepath: str, metadata: dict):
        """
        Cache metadata for file.
        
        Args:
            filepath: Absolute file path
            metadata: Metadata dictionary to cache
        """
        cache_key = self._get_cache_key(filepath, ':metadata')
        cache_file = self.metadata_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)
            self.logger.debug(f"Cached metadata for: {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to cache metadata: {e}")
            
    def get_processed_data(self, filepath: str, data_type: str = 'default') -> Optional[Any]:
        """
        Retrieve cached processed data.
        
        Args:
            filepath: Absolute file path
            data_type: Type of processed data
            
        Returns:
            Cached data or None if not found
        """
        cache_key = self._get_cache_key(filepath, f':{data_type}')
        cache_file = self.processed_dir / f"{cache_key}.pkl"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    self.logger.debug(f"Cache hit for processed data: {filepath}")
                    return data
            except Exception as e:
                self.logger.warning(f"Failed to load cached processed data: {e}")
                cache_file.unlink(missing_ok=True)
        return None
        
    def set_processed_data(self, filepath: str, data: Any, data_type: str = 'default'):
        """
        Cache processed data.
        
        Args:
            filepath: Absolute file path
            data: Data to cache
            data_type: Type of processed data
        """
        cache_key = self._get_cache_key(filepath, f':{data_type}')
        cache_file = self.processed_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            self.logger.debug(f"Cached processed data for: {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to cache processed data: {e}")
            
    def get_thumbnail_path(self, filepath: str) -> Optional[Path]:
        """
        Get path to cached thumbnail.
        
        Args:
            filepath: Absolute file path
            
        Returns:
            Path to thumbnail if exists, None otherwise
        """
        cache_key = self._get_cache_key(filepath, ':thumbnail')
        thumb_file = self.thumbnail_dir / f"{cache_key}.png"
        return thumb_file if thumb_file.exists() else None
        
    def set_thumbnail(self, filepath: str, thumbnail_path: Path):
        """
        Cache thumbnail image.
        
        Args:
            filepath: Absolute file path
            thumbnail_path: Path to thumbnail image to cache
        """
        cache_key = self._get_cache_key(filepath, ':thumbnail')
        thumb_file = self.thumbnail_dir / f"{cache_key}.png"
        
        try:
            import shutil
            shutil.copy2(thumbnail_path, thumb_file)
            self.logger.debug(f"Cached thumbnail for: {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to cache thumbnail: {e}")
            
    def clear_cache(self, older_than_days: int = None):
        """
        Clear cache, optionally only entries older than specified days.
        
        Args:
            older_than_days: If specified, only clear entries older than this
        """
        cutoff_time = None
        if older_than_days:
            cutoff_time = datetime.now() - timedelta(days=older_than_days)
            
        total_cleared = 0
        for cache_subdir in [self.metadata_dir, self.thumbnail_dir, self.processed_dir]:
            for cache_file in cache_subdir.iterdir():
                if cache_file.is_file():
                    if cutoff_time:
                        file_mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
                        if file_mtime < cutoff_time:
                            cache_file.unlink()
                            total_cleared += 1
                    else:
                        cache_file.unlink()
                        total_cleared += 1
                        
        self.logger.info(f"Cleared {total_cleared} cache entries")
        
    def get_cache_size(self) -> int:
        """
        Get total cache size in bytes.
        
        Returns:
            Cache size in bytes
        """
        total_size = 0
        for cache_subdir in [self.metadata_dir, self.thumbnail_dir, self.processed_dir]:
            for cache_file in cache_subdir.rglob('*'):
                if cache_file.is_file():
                    total_size += cache_file.stat().st_size
        return total_size
        
    def enforce_size_limit(self):
        """Remove oldest cache entries if size exceeds limit."""
        current_size = self.get_cache_size()
        
        if current_size <= self.max_size_bytes:
            return
            
        self.logger.info(
            f"Cache size ({current_size} bytes) exceeds limit "
            f"({self.max_size_bytes} bytes). Cleaning up..."
        )
        
        # Get all cache files with modification times
        all_files = []
        for cache_subdir in [self.metadata_dir, self.thumbnail_dir, self.processed_dir]:
            for cache_file in cache_subdir.iterdir():
                if cache_file.is_file():
                    all_files.append((cache_file, cache_file.stat().st_mtime))
                    
        # Sort by modification time (oldest first)
        all_files.sort(key=lambda x: x[1])
        
        # Remove oldest files until under limit
        for cache_file, _ in all_files:
            if current_size <= self.max_size_bytes:
                break
            file_size = cache_file.stat().st_size
            cache_file.unlink()
            current_size -= file_size
            
        self.logger.info(f"Cache cleanup complete. New size: {current_size} bytes")
