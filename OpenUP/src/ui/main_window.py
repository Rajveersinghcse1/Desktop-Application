"""Main window for OpenUP application."""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QToolBar, QStatusBar, QFileDialog,
    QMessageBox, QLabel, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QDragEnterEvent, QDropEvent

from src.core.config import Config
from src.core.plugin_manager import PluginManager
from src.core.worker_pool import WorkerPool
from src.core.cache_manager import CacheManager
from src.ui.file_browser import FileBrowser
from src.ui.domain_filter import DomainFilter
from src.ui.preview_area import PreviewArea
from src.utils.helpers import get_file_info


class MainWindow(QMainWindow):
    """Main application window."""
    
    file_opened = pyqtSignal(str)  # Emitted when file is opened
    
    def __init__(self, config: Config):
        """
        Initialize main window.
        
        Args:
            config: Application configuration
        """
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Core components
        self.plugin_manager = PluginManager()
        self.worker_pool = WorkerPool(max_workers=config.get('worker_threads', 4))
        self.cache_manager = CacheManager(
            config.get_cache_dir(),
            max_size_mb=config.get('cache_size_mb', 500)
        )
        
        # Current file
        self.current_file = None
        
        # Initialize UI
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()
        self._load_plugins()
        self._restore_window_state()
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        self.logger.info("MainWindow initialized")
        
    def _setup_ui(self):
        """Setup user interface layout."""
        self.setWindowTitle("OpenUP - Universal File Preview")
        self.setMinimumSize(1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for resizable panes
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left pane: Domain filter + File browser
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(4, 4, 4, 4)
        
        self.domain_filter = DomainFilter()
        self.file_browser = FileBrowser(
            start_path=self.config.get('last_directory', str(Path.home()))
        )
        
        left_layout.addWidget(QLabel("<b>Filter by Domain</b>"))
        left_layout.addWidget(self.domain_filter)
        left_layout.addWidget(QLabel("<b>File Browser</b>"))
        left_layout.addWidget(self.file_browser, stretch=1)
        
        # Right pane: Preview area
        self.preview_area = PreviewArea(
            plugin_manager=self.plugin_manager,
            worker_pool=self.worker_pool,
            cache_manager=self.cache_manager
        )
        
        # Add to splitter
        self.splitter.addWidget(left_pane)
        self.splitter.addWidget(self.preview_area)
        
        # Set initial splitter sizes (20% left, 80% right)
        self.splitter.setSizes([250, 950])
        
        main_layout.addWidget(self.splitter)
        
    def _setup_menu_bar(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open File...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Recent files submenu
        self.recent_files_menu = file_menu.addMenu("Recent Files")
        self._update_recent_files_menu()
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self.refresh_current_file)
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        toggle_browser_action = QAction("Toggle File Browser", self)
        toggle_browser_action.setShortcut(QKeySequence("Ctrl+B"))
        toggle_browser_action.triggered.connect(self._toggle_file_browser)
        view_menu.addAction(toggle_browser_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        clear_cache_action = QAction("Clear Cache", self)
        clear_cache_action.triggered.connect(self._clear_cache)
        tools_menu.addAction(clear_cache_action)
        
        plugin_info_action = QAction("Plugin Information", self)
        plugin_info_action.triggered.connect(self._show_plugin_info)
        tools_menu.addAction(plugin_info_action)
        
        settings_action = QAction("Settings...", self)
        settings_action.setShortcut(QKeySequence.StandardKey.Preferences)
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("About OpenUP", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _setup_toolbar(self):
        """Setup toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Open file action
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file_dialog)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        # Refresh action
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_current_file)
        toolbar.addAction(refresh_action)
        
    def _setup_statusbar(self):
        """Setup status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.statusbar.addWidget(self.status_label, stretch=1)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.statusbar.addPermanentWidget(self.progress_bar)
        
        # Plugin count label
        self.plugin_count_label = QLabel("Plugins: 0")
        self.statusbar.addPermanentWidget(self.plugin_count_label)
        
    def _connect_signals(self):
        """Connect signals and slots."""
        self.file_browser.file_selected.connect(self.open_file)
        self.domain_filter.domain_changed.connect(self._on_domain_filter_changed)
        
    def _load_plugins(self):
        """Load all plugins."""
        self.set_status("Loading plugins...")
        self.plugin_manager.discover_and_load_plugins()
        
        # Update domain filter with available domains
        domains = self.plugin_manager.get_all_domains()
        self.domain_filter.set_domains(domains)
        
        # Update status
        plugin_count = len(self.plugin_manager._plugins)
        self.plugin_count_label.setText(f"Plugins: {plugin_count}")
        self.set_status(f"Loaded {plugin_count} plugins")
        
        self.logger.info(f"Loaded {plugin_count} plugins")
        
    def open_file_dialog(self):
        """Open file dialog to select file."""
        last_dir = self.config.get('last_directory', str(Path.home()))
        
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            last_dir,
            "All Files (*.*)"
        )
        
        if filepath:
            self.open_file(filepath)
            
    def open_file(self, filepath: str):
        """
        Open and preview file.
        
        Args:
            filepath: Absolute path to file
        """
        self.logger.info(f"Opening file: {filepath}")
        
        # Validate file exists
        if not Path(filepath).exists():
            QMessageBox.warning(
                self,
                "File Not Found",
                f"File does not exist:\n{filepath}"
            )
            return
            
        # Update current file
        self.current_file = filepath
        
        # Update last directory
        self.config.set('last_directory', str(Path(filepath).parent))
        
        # Add to recent files
        self.config.add_recent_file(filepath)
        self._update_recent_files_menu()
        
        # Update window title
        self.setWindowTitle(f"OpenUP - {Path(filepath).name}")
        
        # Load file in preview area
        self.preview_area.load_file(filepath)
        
        # Update status
        file_info = get_file_info(filepath)
        self.set_status(
            f"Loaded: {file_info['name']} ({file_info['size_human']})"
        )
        
        # Emit signal
        self.file_opened.emit(filepath)
        
    def refresh_current_file(self):
        """Refresh current file preview."""
        if self.current_file:
            self.logger.info("Refreshing current file")
            self.preview_area.load_file(self.current_file, force_refresh=True)
            
    def set_status(self, message: str, timeout: int = 5000):
        """
        Set status bar message.
        
        Args:
            message: Status message
            timeout: Message timeout in milliseconds (0 = permanent)
        """
        self.status_label.setText(message)
        if timeout > 0:
            QTimer.singleShot(timeout, lambda: self.status_label.setText("Ready"))
            
    def show_progress(self, value: int = 0, maximum: int = 100):
        """
        Show progress bar.
        
        Args:
            value: Current progress value
            maximum: Maximum progress value
        """
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
        self.progress_bar.setVisible(True)
        
    def hide_progress(self):
        """Hide progress bar."""
        self.progress_bar.setVisible(False)
        
    def _update_recent_files_menu(self):
        """Update recent files menu."""
        self.recent_files_menu.clear()
        
        recent_files = self.config.get_recent_files()
        
        if not recent_files:
            action = QAction("No recent files", self)
            action.setEnabled(False)
            self.recent_files_menu.addAction(action)
        else:
            for filepath in recent_files:
                if Path(filepath).exists():
                    action = QAction(Path(filepath).name, self)
                    action.setToolTip(filepath)
                    action.triggered.connect(
                        lambda checked, f=filepath: self.open_file(f)
                    )
                    self.recent_files_menu.addAction(action)
                    
            self.recent_files_menu.addSeparator()
            
            clear_action = QAction("Clear Recent Files", self)
            clear_action.triggered.connect(self._clear_recent_files)
            self.recent_files_menu.addAction(clear_action)
            
    def _clear_recent_files(self):
        """Clear recent files list."""
        self.config.clear_recent_files()
        self._update_recent_files_menu()
        
    def _on_domain_filter_changed(self, domain: str):
        """Handle domain filter change."""
        self.logger.debug(f"Domain filter changed: {domain}")
        # TODO: Filter file browser by domain
        
    def _toggle_file_browser(self):
        """Toggle file browser visibility."""
        left_pane = self.splitter.widget(0)
        left_pane.setVisible(not left_pane.isVisible())
        
    def _clear_cache(self):
        """Clear application cache."""
        reply = QMessageBox.question(
            self,
            "Clear Cache",
            "Are you sure you want to clear the cache?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            cache_size_before = self.cache_manager.get_cache_size()
            self.cache_manager.clear_cache()
            cache_size_after = self.cache_manager.get_cache_size()
            
            from src.utils.helpers import format_file_size
            QMessageBox.information(
                self,
                "Cache Cleared",
                f"Freed {format_file_size(cache_size_before - cache_size_after)}"
            )
            
    def _show_plugin_info(self):
        """Show plugin information dialog."""
        from src.ui.dialogs import PluginInfoDialog
        dialog = PluginInfoDialog(self.plugin_manager, self)
        dialog.exec()
        
    def _show_settings(self):
        """Show settings dialog."""
        from src.ui.dialogs import SettingsDialog
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            # Reload if settings changed
            pass
            
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About OpenUP",
            "<h2>OpenUP</h2>"
            "<p>Version 1.0.0</p>"
            "<p>Universal File Preview & Visualization</p>"
            "<p>Cross-platform desktop application for previewing files across multiple domains.</p>"
            "<p><b>Developed by:</b> Rajveer Singh</p>"
            "<p><b>License:</b> MIT</p>"
        )
        
    def _restore_window_state(self):
        """Restore window geometry and state."""
        geometry = self.config.get('window_geometry')
        if geometry:
            from PyQt6.QtCore import QByteArray
            self.restoreGeometry(QByteArray.fromHex(bytes.fromhex(geometry)))
            
        state = self.config.get('window_state')
        if state:
            from PyQt6.QtCore import QByteArray
            self.restoreState(QByteArray.fromHex(bytes.fromhex(state)))
            
        splitter_state = self.config.get('splitter_state')
        if splitter_state:
            from PyQt6.QtCore import QByteArray
            self.splitter.restoreState(QByteArray.fromHex(bytes.fromhex(splitter_state)))
            
    def _save_window_state(self):
        """Save window geometry and state."""
        self.config.set('window_geometry', self.saveGeometry().toHex().data().decode())
        self.config.set('window_state', self.saveState().toHex().data().decode())
        self.config.set('splitter_state', self.splitter.saveState().toHex().data().decode())
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        urls = event.mimeData().urls()
        if urls:
            filepath = urls[0].toLocalFile()
            if Path(filepath).is_file():
                self.open_file(filepath)
                
    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.info("Application closing...")
        
        # Save window state
        self._save_window_state()
        
        # Cleanup
        self.plugin_manager.cleanup_all()
        self.worker_pool.shutdown(wait=True)
        
        self.logger.info("Cleanup complete")
        event.accept()
