"""Configuration management for OpenUP application."""

import json
import logging
from pathlib import Path
from typing import Any, Dict


class Config:
    """Application configuration manager with persistent storage."""
    
    DEFAULT_CONFIG = {
        'cache_size_mb': 500,
        'max_file_size_mb': 1000,
        'theme': 'dark',
        'recent_files_count': 10,
        'plugins_enabled': True,
        'auto_refresh': False,
        'show_hidden_files': False,
        'thumbnail_size': 256,
        'worker_threads': 4,
        'enable_gpu': True,
        'log_level': 'INFO',
        'default_domain': 'All',
        'point_cloud_max_points': 1000000,
        'csv_preview_rows': 1000,
        'pdf_render_dpi': 150,
        'video_thumbnail_time': 1.0,
        'image_cache_enabled': True,
        'last_directory': str(Path.home()),
        'window_geometry': None,
        'window_state': None,
        'splitter_state': None
    }
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to config file. If None, uses default location.
        """
        if config_path is None:
            self.config_dir = Path.home() / '.openup'
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = self.config_dir / 'config.json'
        else:
            self.config_path = Path(config_path)
            self.config_dir = self.config_path.parent
            
        self.cache_dir = self.config_dir / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._config: Dict[str, Any] = {}
        self._recent_files: list = []
        self.load()
        
    def load(self):
        """Load configuration from disk or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._config = data.get('settings', {})
                    self._recent_files = data.get('recent_files', [])
                    
                # Merge with defaults for any missing keys
                for key, value in self.DEFAULT_CONFIG.items():
                    if key not in self._config:
                        self._config[key] = value
                        
                logging.info(f"Configuration loaded from {self.config_path}")
            except Exception as e:
                logging.error(f"Failed to load config: {e}. Using defaults.")
                self._config = self.DEFAULT_CONFIG.copy()
        else:
            logging.info("No config file found. Creating default configuration.")
            self._config = self.DEFAULT_CONFIG.copy()
            self.save()
            
    def save(self):
        """Save configuration to disk."""
        try:
            data = {
                'settings': self._config,
                'recent_files': self._recent_files
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logging.debug(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
        
    def set(self, key: str, value: Any):
        """Set configuration value and save."""
        self._config[key] = value
        self.save()
        
    def get_recent_files(self) -> list:
        """Get list of recently opened files."""
        return self._recent_files.copy()
        
    def add_recent_file(self, filepath: str):
        """Add file to recent files list."""
        filepath = str(Path(filepath).absolute())
        
        # Remove if already exists
        if filepath in self._recent_files:
            self._recent_files.remove(filepath)
            
        # Add to beginning
        self._recent_files.insert(0, filepath)
        
        # Limit list size
        max_recent = self.get('recent_files_count', 10)
        self._recent_files = self._recent_files[:max_recent]
        
        self.save()
        
    def clear_recent_files(self):
        """Clear recent files list."""
        self._recent_files = []
        self.save()
        
    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self._config = self.DEFAULT_CONFIG.copy()
        self._recent_files = []
        self.save()
        logging.info("Configuration reset to defaults")
        
    def get_cache_dir(self) -> Path:
        """Get cache directory path."""
        return self.cache_dir
        
    def get_log_dir(self) -> Path:
        """Get log directory path."""
        log_dir = self.config_dir / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
