"""Plugin management system for OpenUP."""

import importlib
import importlib.util
import inspect
import logging
from pathlib import Path
from typing import Dict, List, Optional, Type
from src.core.plugin_base import PreviewPlugin, PluginLoadError


class PluginManager:
    """
    Manages loading, registration, and retrieval of preview plugins.
    
    Plugins are automatically discovered from the plugins directory and
    registered by file extension.
    """
    
    def __init__(self, plugins_dir: str = None):
        """
        Initialize plugin manager.
        
        Args:
            plugins_dir: Directory containing plugin modules. If None, uses default.
        """
        self.logger = logging.getLogger(__name__)
        
        if plugins_dir is None:
            self.plugins_dir = Path(__file__).parent.parent / 'plugins'
        else:
            self.plugins_dir = Path(plugins_dir)
            
        # Registry: extension -> plugin instance
        self._extension_registry: Dict[str, PreviewPlugin] = {}
        
        # Registry: domain -> list of plugins
        self._domain_registry: Dict[str, List[PreviewPlugin]] = {}
        
        # All loaded plugins
        self._plugins: List[PreviewPlugin] = []
        
        # Failed plugins (for diagnostics)
        self._failed_plugins: Dict[str, str] = {}
        
        self.logger.info(f"PluginManager initialized with plugins_dir: {self.plugins_dir}")
        
    def discover_and_load_plugins(self):
        """
        Discover and load all plugins from plugins directory.
        
        Scans for Python modules and attempts to load plugin classes.
        """
        self.logger.info("Discovering plugins...")
        
        if not self.plugins_dir.exists():
            self.logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return
            
        # Find all Python files in plugins directory
        plugin_files = list(self.plugins_dir.glob('*.py'))
        plugin_files = [f for f in plugin_files if not f.name.startswith('_')]
        
        self.logger.info(f"Found {len(plugin_files)} potential plugin files")
        
        for plugin_file in plugin_files:
            try:
                self._load_plugin_from_file(plugin_file)
            except Exception as e:
                self.logger.error(f"Failed to load plugin from {plugin_file}: {e}", exc_info=True)
                self._failed_plugins[plugin_file.name] = str(e)
                
        self.logger.info(
            f"Plugin discovery complete. "
            f"Loaded: {len(self._plugins)}, Failed: {len(self._failed_plugins)}"
        )
        
    def _load_plugin_from_file(self, plugin_file: Path):
        """
        Load plugin class from a Python file.
        
        Args:
            plugin_file: Path to plugin Python file
        """
        module_name = f"plugins.{plugin_file.stem}"
        
        try:
            # Import module
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            if spec is None or spec.loader is None:
                raise PluginLoadError(f"Failed to create module spec for {plugin_file}")
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes in module
            plugin_classes = []
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, PreviewPlugin) and 
                    obj is not PreviewPlugin and 
                    not inspect.isabstract(obj)):
                    plugin_classes.append(obj)
                    
            if not plugin_classes:
                self.logger.warning(f"No plugin classes found in {plugin_file}")
                return
                
            # Instantiate and register each plugin class
            for plugin_class in plugin_classes:
                try:
                    plugin = plugin_class()
                    self.register_plugin(plugin)
                    self.logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
                except Exception as e:
                    self.logger.error(f"Failed to instantiate plugin {plugin_class}: {e}")
                    raise
                    
        except Exception as e:
            raise PluginLoadError(f"Error loading plugin from {plugin_file}: {e}")
            
    def register_plugin(self, plugin: PreviewPlugin):
        """
        Register a plugin instance.
        
        Args:
            plugin: Plugin instance to register
        """
        # Add to plugin list
        self._plugins.append(plugin)
        
        # Register by extensions
        for ext in plugin.extensions:
            ext_lower = ext.lower()
            if ext_lower in self._extension_registry:
                self.logger.warning(
                    f"Extension {ext} already registered by "
                    f"{self._extension_registry[ext_lower].name}. "
                    f"Overriding with {plugin.name}"
                )
            self._extension_registry[ext_lower] = plugin
            
        # Register by domain
        domain = plugin.domain
        if domain not in self._domain_registry:
            self._domain_registry[domain] = []
        self._domain_registry[domain].append(plugin)
        
    def get_plugin_for_file(self, filepath: str) -> Optional[PreviewPlugin]:
        """
        Get appropriate plugin for a file.
        
        Args:
            filepath: Absolute path to file
            
        Returns:
            Plugin instance if found, None otherwise
        """
        from pathlib import Path
        
        path = Path(filepath)
        ext = path.suffix.lower()
        
        # Try exact extension match
        if ext in self._extension_registry:
            plugin = self._extension_registry[ext]
            
            # Verify plugin can handle file size
            file_size = path.stat().st_size if path.exists() else 0
            if plugin.can_handle_file(filepath, file_size):
                return plugin
                
        # Fallback: probe all plugins
        for plugin in self._plugins:
            if plugin.probe(filepath):
                file_size = path.stat().st_size if path.exists() else 0
                if plugin.can_handle_file(filepath, file_size):
                    return plugin
                    
        return None
        
    def get_plugins_by_domain(self, domain: str) -> List[PreviewPlugin]:
        """
        Get all plugins for a specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of plugins in that domain
        """
        return self._domain_registry.get(domain, [])
        
    def get_all_domains(self) -> List[str]:
        """
        Get list of all available domains.
        
        Returns:
            Sorted list of domain names
        """
        return sorted(self._domain_registry.keys())
        
    def get_all_extensions(self) -> List[str]:
        """
        Get list of all supported extensions.
        
        Returns:
            Sorted list of file extensions
        """
        return sorted(self._extension_registry.keys())
        
    def get_plugin_info(self) -> List[Dict[str, any]]:
        """
        Get information about all loaded plugins.
        
        Returns:
            List of plugin info dictionaries
        """
        info = []
        for plugin in self._plugins:
            info.append({
                'name': plugin.name,
                'version': plugin.version,
                'domain': plugin.domain,
                'extensions': plugin.extensions,
                'description': plugin.description,
                'author': plugin.author,
                'supports_streaming': plugin.supports_streaming,
                'max_file_size_mb': plugin.max_file_size_mb
            })
        return info
        
    def cleanup_all(self):
        """Cleanup all plugins."""
        for plugin in self._plugins:
            try:
                plugin.cleanup()
            except Exception as e:
                self.logger.error(f"Error cleaning up plugin {plugin.name}: {e}")
