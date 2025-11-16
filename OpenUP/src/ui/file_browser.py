"""File browser widget for OpenUP."""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QTreeView, QVBoxLayout, QWidget,
    QLineEdit, QHBoxLayout
)
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import pyqtSignal, Qt, QDir


class FileBrowser(QWidget):
    """
    File browser widget with search capability.
    
    Displays directory tree and emits signal when file is selected.
    """
    
    file_selected = pyqtSignal(str)  # Emitted when file is double-clicked
    
    def __init__(self, start_path: str = None, parent=None):
        """
        Initialize file browser.
        
        Args:
            start_path: Initial directory path
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        
        if start_path is None:
            start_path = str(Path.home())
            
        self._setup_ui(start_path)
        
    def _setup_ui(self, start_path: str):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Search box
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search files...")
        self.search_box.textChanged.connect(self._on_search_text_changed)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # File system model
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)
        
        # Tree view
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(start_path))
        
        # Hide unnecessary columns
        self.tree_view.setColumnWidth(0, 250)
        for i in range(1, 4):
            self.tree_view.hideColumn(i)
            
        # Enable sorting
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
        # Connect signals
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)
        
        layout.addWidget(self.tree_view, stretch=1)
        
    def _on_item_double_clicked(self, index):
        """Handle item double-click."""
        filepath = self.model.filePath(index)
        
        if Path(filepath).is_file():
            self.logger.debug(f"File selected: {filepath}")
            self.file_selected.emit(filepath)
        else:
            # Expand directory
            if self.tree_view.isExpanded(index):
                self.tree_view.collapse(index)
            else:
                self.tree_view.expand(index)
                
    def _on_search_text_changed(self, text: str):
        """Handle search text change."""
        # Apply name filter
        if text:
            self.model.setNameFilters([f"*{text}*"])
            self.model.setNameFilterDisables(False)
        else:
            self.model.setNameFilters([])
            
    def set_root_path(self, path: str):
        """Set root path for browser."""
        self.tree_view.setRootIndex(self.model.index(path))
