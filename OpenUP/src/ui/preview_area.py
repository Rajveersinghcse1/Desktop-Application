"""Preview area widget with dual-tab interface."""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QLabel,
    QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt

from src.core.plugin_manager import PluginManager
from src.core.worker_pool import WorkerPool
from src.core.cache_manager import CacheManager
from src.utils.helpers import get_file_info


class PreviewArea(QWidget):
    """
    Preview area with metadata and visualization tabs.
    
    Manages file preview by delegating to appropriate plugin.
    """
    
    def __init__(
        self,
        plugin_manager: PluginManager,
        worker_pool: WorkerPool,
        cache_manager: CacheManager,
        parent=None
    ):
        """Initialize preview area."""
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.plugin_manager = plugin_manager
        self.worker_pool = worker_pool
        self.cache_manager = cache_manager
        
        self.current_file = None
        self.current_plugin = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Initial placeholder
        self._show_placeholder()
        
    def _show_placeholder(self):
        """Show placeholder when no file is loaded."""
        self.tab_widget.clear()
        
        placeholder = QLabel(
            "<center>"
            "<h2>No File Loaded</h2>"
            "<p>Open a file to preview</p>"
            "<p>Drag & drop files or use File > Open</p>"
            "</center>"
        )
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.tab_widget.addTab(placeholder, "Welcome")
        
    def load_file(self, filepath: str, force_refresh: bool = False):
        """
        Load file for preview.
        
        Args:
            filepath: Absolute path to file
            force_refresh: If True, bypass cache
        """
        self.logger.info(f"Loading file: {filepath}")
        
        # Clear existing tabs
        self.tab_widget.clear()
        
        # Get file info
        file_info = get_file_info(filepath)
        
        if not file_info['exists']:
            self._show_error("File not found", f"File does not exist:\n{filepath}")
            return
            
        # Find appropriate plugin
        plugin = self.plugin_manager.get_plugin_for_file(filepath)
        
        if plugin is None:
            self._show_unsupported_file(file_info)
            return
            
        self.logger.info(f"Using plugin: {plugin.name}")
        
        # Store current state
        self.current_file = filepath
        self.current_plugin = plugin
        
        # Check cache for metadata (unless force refresh)
        metadata = None
        if not force_refresh and plugin.supports_caching:
            metadata = self.cache_manager.get_metadata(filepath)
            
        # Load metadata
        if metadata is None:
            try:
                # Extract metadata (potentially heavy operation)
                signals = self.worker_pool.submit_task(
                    f"metadata:{filepath}",
                    plugin.get_metadata,
                    filepath
                )
                
                # For now, do it synchronously (TODO: async with signals)
                metadata = plugin.get_metadata(filepath)
                
                # Cache metadata
                if plugin.supports_caching:
                    self.cache_manager.set_metadata(filepath, metadata)
                    
            except Exception as e:
                self.logger.error(f"Failed to extract metadata: {e}", exc_info=True)
                self._show_error("Metadata Error", f"Failed to extract metadata:\n{str(e)}")
                return
                
        # Create tabs
        try:
            # Metadata tab
            metadata_widget = plugin.create_metadata_widget(metadata, self)
            self.tab_widget.addTab(metadata_widget, "📊 Metadata / Table")
            
            # Visual tab
            visual_widget = plugin.create_visual_widget(filepath, self)
            self.tab_widget.addTab(visual_widget, "👁 Visualization")
            
            self.logger.info("File loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create preview widgets: {e}", exc_info=True)
            self._show_error("Preview Error", f"Failed to create preview:\n{str(e)}")
            
    def _show_error(self, title: str, message: str):
        """Show error message."""
        self.tab_widget.clear()
        
        error_widget = QTextEdit()
        error_widget.setReadOnly(True)
        error_widget.setHtml(
            f"<h2 style='color: red;'>{title}</h2>"
            f"<pre>{message}</pre>"
        )
        
        self.tab_widget.addTab(error_widget, "⚠ Error")
        
    def _show_unsupported_file(self, file_info: dict):
        """Show message for unsupported file type."""
        self.logger.warning(f"Unsupported file type: {file_info['extension']}")
        
        self.tab_widget.clear()
        
        info_text = f"""
        <h2>Unsupported File Type</h2>
        <p><b>File:</b> {file_info['name']}</p>
        <p><b>Extension:</b> {file_info['extension']}</p>
        <p><b>Size:</b> {file_info['size_human']}</p>
        <p><b>MIME:</b> {file_info['mime_type']}</p>
        <hr>
        <p>No plugin available to preview this file type.</p>
        <p>Try opening with system default application.</p>
        """
        
        info_widget = QLabel(info_text)
        info_widget.setWordWrap(True)
        info_widget.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        info_widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        self.tab_widget.addTab(info_widget, "ℹ File Information")
