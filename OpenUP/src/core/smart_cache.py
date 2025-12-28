"""
Enhanced Cache Manager for OpenUP
=================================
Smart caching with LRU eviction, TTL support, and memory awareness.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import pickle
import shutil
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Generic

T = TypeVar('T')

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Metadata for a cached item."""
    key: str
    size_bytes: int
    created_at: float
    accessed_at: float
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    
    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl_seconds is None:
            return False
        return time.time() > self.created_at + self.ttl_seconds
    
    @property
    def age_seconds(self) -> float:
        """Get age of entry in seconds."""
        return time.time() - self.created_at


class CacheStats:
    """Statistics tracking for cache operations."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.writes = 0
        self.bytes_written = 0
        self.bytes_read = 0
        self._lock = threading.Lock()
    
    def record_hit(self, bytes_read: int = 0):
        with self._lock:
            self.hits += 1
            self.bytes_read += bytes_read
    
    def record_miss(self):
        with self._lock:
            self.misses += 1
    
    def record_write(self, bytes_written: int):
        with self._lock:
            self.writes += 1
            self.bytes_written += bytes_written
    
    def record_eviction(self):
        with self._lock:
            self.evictions += 1
    
    @property
    def hit_rate(self) -> float:
        """Calculate hit rate percentage."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate_percent': round(self.hit_rate, 2),
            'evictions': self.evictions,
            'writes': self.writes,
            'bytes_written': self.bytes_written,
            'bytes_read': self.bytes_read
        }


class SmartCacheManager:
    """
    Advanced cache manager with LRU eviction and memory awareness.
    
    Features:
    - LRU (Least Recently Used) eviction policy
    - TTL (Time To Live) support
    - Memory-aware caching
    - Tag-based cache invalidation
    - Persistent index for fast lookups
    - Thread-safe operations
    """
    
    def __init__(
        self,
        cache_dir: Path,
        max_size_mb: int = 500,
        default_ttl_seconds: Optional[int] = None,
        cleanup_threshold: float = 0.9
    ):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory for cache storage
            max_size_mb: Maximum cache size in megabytes
            default_ttl_seconds: Default TTL for entries (None = no expiry)
            cleanup_threshold: Trigger cleanup when usage exceeds this ratio
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.default_ttl = default_ttl_seconds
        self.cleanup_threshold = cleanup_threshold
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.stats = CacheStats()
        
        # Initialize index database
        self._db_path = self.cache_dir / '.cache_index.db'
        self._init_database()
        
        # Perform initial cleanup
        self._cleanup_expired()
        
        logger.info(f"Cache initialized: {self.cache_dir}, max {max_size_mb}MB")
    
    def _init_database(self):
        """Initialize SQLite index database."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    created_at REAL NOT NULL,
                    accessed_at REAL NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    ttl_seconds INTEGER,
                    tags TEXT
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_accessed_at ON cache_entries(accessed_at)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON cache_entries(created_at)')
    
    def _get_cache_path(self, key: str) -> Path:
        """Get file path for a cache key."""
        # Use hash to create safe filename
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash[:2]}" / f"{key_hash}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            entry = self._get_entry(key)
            
            if entry is None:
                self.stats.record_miss()
                return None
            
            if entry.is_expired:
                self.stats.record_miss()
                self.delete(key)
                return None
            
            # Load data
            cache_path = self._get_cache_path(key)
            if not cache_path.exists():
                self.stats.record_miss()
                self._delete_entry(key)
                return None
            
            try:
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                
                # Update access time
                self._update_access(key)
                self.stats.record_hit(entry.size_bytes)
                
                return data
                
            except Exception as e:
                logger.error(f"Cache read error for {key}: {e}")
                self.stats.record_miss()
                self.delete(key)
                return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Store item in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live (None uses default)
            tags: Tags for grouped invalidation
            
        Returns:
            True if successful
        """
        with self._lock:
            try:
                # Serialize data
                data = pickle.dumps(value)
                size = len(data)
                
                # Check if too large for cache
                if size > self.max_size_bytes * 0.5:
                    logger.warning(f"Cache item too large: {size} bytes")
                    return False
                
                # Ensure space
                self._ensure_space(size)
                
                # Write data
                cache_path = self._get_cache_path(key)
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(cache_path, 'wb') as f:
                    f.write(data)
                
                # Update index
                ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
                now = time.time()
                
                with sqlite3.connect(self._db_path) as conn:
                    conn.execute('''
                        INSERT OR REPLACE INTO cache_entries 
                        (key, filename, size_bytes, created_at, accessed_at, access_count, ttl_seconds, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (key, str(cache_path), size, now, now, 0, ttl, 
                          json.dumps(tags or [])))
                
                self.stats.record_write(size)
                return True
                
            except Exception as e:
                logger.error(f"Cache write error for {key}: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """Delete item from cache."""
        with self._lock:
            cache_path = self._get_cache_path(key)
            
            try:
                if cache_path.exists():
                    cache_path.unlink()
                self._delete_entry(key)
                return True
            except Exception as e:
                logger.error(f"Cache delete error for {key}: {e}")
                return False
    
    def clear(self):
        """Clear entire cache."""
        with self._lock:
            try:
                # Delete all cache files
                for item in self.cache_dir.iterdir():
                    if item.is_dir() and len(item.name) == 2:  # Hash subdirs
                        shutil.rmtree(item)
                
                # Clear index
                with sqlite3.connect(self._db_path) as conn:
                    conn.execute('DELETE FROM cache_entries')
                
                logger.info("Cache cleared")
                
            except Exception as e:
                logger.error(f"Cache clear error: {e}")
    
    def invalidate_by_tag(self, tag: str):
        """Invalidate all entries with a specific tag."""
        with self._lock:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute(
                    'SELECT key, tags FROM cache_entries'
                )
                
                keys_to_delete = []
                for row in cursor:
                    tags = json.loads(row[1]) if row[1] else []
                    if tag in tags:
                        keys_to_delete.append(row[0])
                
            for key in keys_to_delete:
                self.delete(key)
            
            logger.info(f"Invalidated {len(keys_to_delete)} entries with tag '{tag}'")
    
    def _get_entry(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry metadata."""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'SELECT key, size_bytes, created_at, accessed_at, access_count, ttl_seconds, tags '
                'FROM cache_entries WHERE key = ?',
                (key,)
            )
            row = cursor.fetchone()
            
            if row:
                return CacheEntry(
                    key=row[0],
                    size_bytes=row[1],
                    created_at=row[2],
                    accessed_at=row[3],
                    access_count=row[4],
                    ttl_seconds=row[5],
                    tags=json.loads(row[6]) if row[6] else []
                )
            return None
    
    def _delete_entry(self, key: str):
        """Delete entry from index."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute('DELETE FROM cache_entries WHERE key = ?', (key,))
    
    def _update_access(self, key: str):
        """Update access time and count."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                'UPDATE cache_entries SET accessed_at = ?, access_count = access_count + 1 '
                'WHERE key = ?',
                (time.time(), key)
            )
    
    def _get_current_size(self) -> int:
        """Get current cache size in bytes."""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('SELECT SUM(size_bytes) FROM cache_entries')
            result = cursor.fetchone()[0]
            return result or 0
    
    def _ensure_space(self, needed_bytes: int):
        """Ensure enough space for new item."""
        current_size = self._get_current_size()
        target_size = self.max_size_bytes * self.cleanup_threshold
        
        if current_size + needed_bytes <= target_size:
            return
        
        # Need to evict items
        bytes_to_free = current_size + needed_bytes - int(target_size * 0.8)
        
        with sqlite3.connect(self._db_path) as conn:
            # Get least recently accessed items
            cursor = conn.execute(
                'SELECT key, size_bytes FROM cache_entries ORDER BY accessed_at ASC'
            )
            
            freed = 0
            keys_to_delete = []
            
            for row in cursor:
                if freed >= bytes_to_free:
                    break
                keys_to_delete.append(row[0])
                freed += row[1]
        
        for key in keys_to_delete:
            self.delete(key)
            self.stats.record_eviction()
        
        logger.info(f"Evicted {len(keys_to_delete)} items, freed {freed} bytes")
    
    def _cleanup_expired(self):
        """Remove expired entries."""
        now = time.time()
        
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'SELECT key FROM cache_entries '
                'WHERE ttl_seconds IS NOT NULL AND created_at + ttl_seconds < ?',
                (now,)
            )
            
            expired_keys = [row[0] for row in cursor]
        
        for key in expired_keys:
            self.delete(key)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], T],
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> T:
        """
        Get cached value or compute and cache it.
        
        Args:
            key: Cache key
            compute_fn: Function to compute value if not cached
            ttl_seconds: TTL for new entry
            tags: Tags for new entry
            
        Returns:
            Cached or computed value
        """
        cached = self.get(key)
        if cached is not None:
            return cached
        
        value = compute_fn()
        self.set(key, value, ttl_seconds, tags)
        return value
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            **self.stats.to_dict(),
            'current_size_bytes': self._get_current_size(),
            'max_size_bytes': self.max_size_bytes,
            'usage_percent': round(self._get_current_size() / self.max_size_bytes * 100, 2)
        }


# Backwards compatibility alias
CacheManager = SmartCacheManager
