"""Unit tests for OpenUP core components."""

import pytest
import tempfile
from pathlib import Path

from src.core.config import Config
from src.core.plugin_manager import PluginManager
from src.core.cache_manager import CacheManager
from src.utils.helpers import get_file_info, safe_filename


class TestConfig:
    """Test configuration management."""
    
    def test_config_creation(self, tmp_path):
        """Test config file creation."""
        config_file = tmp_path / "config.json"
        config = Config(str(config_file))
        
        assert config.config_path.exists()
        assert config.get('theme') == 'dark'
        
    def test_config_get_set(self, tmp_path):
        """Test get/set operations."""
        config_file = tmp_path / "config.json"
        config = Config(str(config_file))
        
        config.set('test_key', 'test_value')
        assert config.get('test_key') == 'test_value'
        
    def test_recent_files(self, tmp_path):
        """Test recent files management."""
        config_file = tmp_path / "config.json"
        config = Config(str(config_file))
        
        config.add_recent_file('/path/to/file1.txt')
        config.add_recent_file('/path/to/file2.txt')
        
        recent = config.get_recent_files()
        assert len(recent) == 2
        assert recent[0] == '/path/to/file2.txt'  # Most recent first


class TestPluginManager:
    """Test plugin management."""
    
    def test_plugin_discovery(self):
        """Test plugin discovery."""
        manager = PluginManager()
        manager.discover_and_load_plugins()
        
        # Should find at least our bundled plugins
        assert len(manager._plugins) >= 3
        
    def test_get_plugin_for_file(self):
        """Test plugin selection by file extension."""
        manager = PluginManager()
        manager.discover_and_load_plugins()
        
        # Test text file
        plugin = manager.get_plugin_for_file('/test/file.txt')
        assert plugin is not None
        assert '.txt' in plugin.extensions
        
        # Test image file
        plugin = manager.get_plugin_for_file('/test/image.png')
        assert plugin is not None
        assert '.png' in plugin.extensions
        
    def test_get_domains(self):
        """Test domain retrieval."""
        manager = PluginManager()
        manager.discover_and_load_plugins()
        
        domains = manager.get_all_domains()
        assert 'Documents' in domains
        assert 'Images' in domains
        assert 'Data' in domains


class TestCacheManager:
    """Test cache management."""
    
    def test_metadata_caching(self, tmp_path):
        """Test metadata cache operations."""
        cache = CacheManager(tmp_path / 'cache')
        
        metadata = {'test': 'value', 'number': 42}
        filepath = '/test/file.txt'
        
        # Set metadata
        cache.set_metadata(filepath, metadata)
        
        # Get metadata
        retrieved = cache.get_metadata(filepath)
        assert retrieved == metadata
        
    def test_cache_clear(self, tmp_path):
        """Test cache clearing."""
        cache = CacheManager(tmp_path / 'cache')
        
        # Add some data
        cache.set_metadata('/test1.txt', {'data': 1})
        cache.set_metadata('/test2.txt', {'data': 2})
        
        # Clear cache
        cache.clear_cache()
        
        # Verify cleared
        assert cache.get_metadata('/test1.txt') is None
        assert cache.get_metadata('/test2.txt') is None


class TestHelpers:
    """Test utility helper functions."""
    
    def test_safe_filename(self):
        """Test filename sanitization."""
        assert safe_filename('test<file>name.txt') == 'test_file_name.txt'
        assert safe_filename('file:name?.txt') == 'file_name_.txt'
        
    def test_get_file_info(self, tmp_path):
        """Test file info extraction."""
        # Create test file
        test_file = tmp_path / 'test.txt'
        test_file.write_text('Hello World')
        
        info = get_file_info(str(test_file))
        
        assert info['exists'] is True
        assert info['name'] == 'test.txt'
        assert info['extension'] == '.txt'
        assert info['size_bytes'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
