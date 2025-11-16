"""Dialog windows for OpenUP."""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QTabWidget,
    QTextEdit, QFormLayout, QSpinBox, QCheckBox,
    QComboBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt

from src.core.plugin_manager import PluginManager
from src.core.config import Config


class PluginInfoDialog(QDialog):
    """Dialog displaying information about loaded plugins."""
    
    def __init__(self, plugin_manager: PluginManager, parent=None):
        """Initialize dialog."""
        super().__init__(parent)
        
        self.plugin_manager = plugin_manager
        self.setWindowTitle("Plugin Information")
        self.setMinimumSize(700, 500)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        
        # Info label
        plugin_count = len(self.plugin_manager._plugins)
        info_label = QLabel(f"<b>{plugin_count} plugins loaded</b>")
        layout.addWidget(info_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Name", "Version", "Domain", "Extensions", "Description"
        ])
        
        plugins = self.plugin_manager.get_plugin_info()
        self.table.setRowCount(len(plugins))
        
        for row, plugin in enumerate(plugins):
            self.table.setItem(row, 0, QTableWidgetItem(plugin['name']))
            self.table.setItem(row, 1, QTableWidgetItem(plugin['version']))
            self.table.setItem(row, 2, QTableWidgetItem(plugin['domain']))
            self.table.setItem(row, 3, QTableWidgetItem(', '.join(plugin['extensions'])))
            self.table.setItem(row, 4, QTableWidgetItem(plugin['description']))
            
        self.table.resizeColumnsToContents()
        layout.addWidget(self.table)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class SettingsDialog(QDialog):
    """Settings dialog."""
    
    def __init__(self, config: Config, parent=None):
        """Initialize dialog."""
        super().__init__(parent)
        
        self.config = config
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        
        # Form layout
        form = QFormLayout()
        
        # Cache size
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(100, 5000)
        self.cache_size_spin.setValue(self.config.get('cache_size_mb', 500))
        self.cache_size_spin.setSuffix(" MB")
        form.addRow("Cache Size:", self.cache_size_spin)
        
        # Worker threads
        self.worker_threads_spin = QSpinBox()
        self.worker_threads_spin.setRange(1, 16)
        self.worker_threads_spin.setValue(self.config.get('worker_threads', 4))
        form.addRow("Worker Threads:", self.worker_threads_spin)
        
        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        current_theme = self.config.get('theme', 'dark')
        self.theme_combo.setCurrentText(current_theme.capitalize())
        form.addRow("Theme:", self.theme_combo)
        
        # Enable GPU
        self.gpu_checkbox = QCheckBox()
        self.gpu_checkbox.setChecked(self.config.get('enable_gpu', True))
        form.addRow("Enable GPU Acceleration:", self.gpu_checkbox)
        
        layout.addLayout(form)
        layout.addStretch()
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def _save_settings(self):
        """Save settings."""
        self.config.set('cache_size_mb', self.cache_size_spin.value())
        self.config.set('worker_threads', self.worker_threads_spin.value())
        self.config.set('theme', self.theme_combo.currentText().lower())
        self.config.set('enable_gpu', self.gpu_checkbox.isChecked())
        self.accept()
