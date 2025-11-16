"""Base plugin interface for OpenUP file preview plugins."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import QWidget
import logging


class PreviewPlugin(ABC):
    """
    Abstract base class for file preview plugins.
    
    All plugins must implement this interface to provide:
    1. File format support detection
    2. Metadata extraction
    3. Metadata widget creation
    4. Visual preview widget creation
    """
    
    # List of supported file extensions (lowercase, including dot)
    extensions: List[str] = []
    
    # Domain categorization
    domain: str = "Uncategorized"
    
    # Plugin metadata
    name: str = "Unknown Plugin"
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    
    # Performance hints
    supports_streaming: bool = False  # Can handle large files via streaming
    supports_caching: bool = True     # Can use cached metadata
    max_file_size_mb: Optional[int] = None  # Max file size, None = unlimited
    
    def __init__(self):
        """Initialize plugin."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._metadata_cache: Dict[str, Any] = {}
        
    def probe(self, filepath: str) -> bool:
        """
        Quick check if this plugin can handle the file.
        
        This is called for files with ambiguous extensions or MIME types.
        Default implementation checks file extension.
        
        Args:
            filepath: Absolute path to file
            
        Returns:
            True if plugin can handle this file, False otherwise
        """
        from pathlib import Path
        ext = Path(filepath).suffix.lower()
        return ext in self.extensions
        
    def can_handle_file(self, filepath: str, file_size_bytes: int = 0) -> bool:
        """
        Check if plugin can handle file based on size and other constraints.
        
        Args:
            filepath: Absolute path to file
            file_size_bytes: File size in bytes
            
        Returns:
            True if plugin can handle this file, False otherwise
        """
        # Check file size limit
        if self.max_file_size_mb is not None:
            max_size_bytes = self.max_file_size_mb * 1024 * 1024
            if file_size_bytes > max_size_bytes:
                self.logger.warning(
                    f"File size ({file_size_bytes} bytes) exceeds limit "
                    f"({max_size_bytes} bytes) for {self.name}"
                )
                return False
                
        # Check extension
        if not self.probe(filepath):
            return False
            
        return True
        
    @abstractmethod
    def get_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        Extract metadata from file.
        
        Should return a dictionary with at least:
        {
            'file_name': str,
            'file_size': int,  # bytes
            'file_type': str,
            'summary': str,  # Human-readable summary
            'table': list[dict] or pandas.DataFrame,  # Optional tabular data
            'stats': dict,  # Optional statistics
            # ... plugin-specific metadata
        }
        
        Args:
            filepath: Absolute path to file
            
        Returns:
            Dictionary containing file metadata
        """
        pass
        
    @abstractmethod
    def create_metadata_widget(self, metadata: Dict[str, Any], parent: QWidget = None) -> QWidget:
        """
        Create widget to display metadata and tabular information.
        
        Args:
            metadata: Metadata dictionary from get_metadata()
            parent: Parent widget
            
        Returns:
            QWidget displaying metadata/table
        """
        pass
        
    @abstractmethod
    def create_visual_widget(self, filepath: str, parent: QWidget = None) -> QWidget:
        """
        Create widget to display visual preview.
        
        This can be:
        - Image viewer with zoom/pan
        - 3D canvas with interactive controls
        - Audio/video player
        - Text editor with syntax highlighting
        - Any custom visualization
        
        Args:
            filepath: Absolute path to file
            parent: Parent widget
            
        Returns:
            QWidget displaying visual preview
        """
        pass
        
    def cleanup(self):
        """
        Cleanup resources when plugin is unloaded or file is closed.
        
        Override this to release file handles, stop background workers, etc.
        """
        self._metadata_cache.clear()
        
    def get_cache_key(self, filepath: str) -> str:
        """
        Generate cache key for file.
        
        Args:
            filepath: Absolute path to file
            
        Returns:
            Cache key string
        """
        from pathlib import Path
        import hashlib
        
        path = Path(filepath)
        # Include file modification time in cache key
        mtime = path.stat().st_mtime if path.exists() else 0
        key_str = f"{filepath}:{mtime}:{self.name}:{self.version}"
        return hashlib.md5(key_str.encode()).hexdigest()
        
    def __repr__(self) -> str:
        """String representation of plugin."""
        return (
            f"<{self.__class__.__name__} "
            f"domain={self.domain} "
            f"extensions={self.extensions}>"
        )


class PluginError(Exception):
    """Base exception for plugin-related errors."""
    pass


class PluginLoadError(PluginError):
    """Raised when plugin fails to load."""
    pass


class PluginExecutionError(PluginError):
    """Raised when plugin execution fails."""
    pass
