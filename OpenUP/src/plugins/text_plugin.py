"""Text file preview plugin."""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QTableWidget,
    QTableWidgetItem, QLabel, QHBoxLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from src.core.plugin_base import PreviewPlugin


class TextPlugin(PreviewPlugin):
    """Plugin for previewing text files."""
    
    extensions = ['.txt', '.log', '.md', '.csv', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini']
    domain = "Documents"
    name = "Text File Viewer"
    version = "1.0.0"
    description = "Preview plain text and structured text files"
    author = "OpenUP Team"
    max_file_size_mb = 100
    supports_caching = True
    
    def get_metadata(self, filepath: str) -> dict:
        """Extract metadata from text file."""
        path = Path(filepath)
        
        try:
            # Try UTF-8 first
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                encoding = 'utf-8'
        except UnicodeDecodeError:
            # Fallback to latin-1
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    content = f.read()
                    encoding = 'latin-1'
            except Exception as e:
                self.logger.error(f"Failed to read file: {e}")
                content = ""
                encoding = 'unknown'
                
        lines = content.splitlines()
        
        metadata = {
            'file_name': path.name,
            'file_size': path.stat().st_size,
            'file_type': 'Text File',
            'encoding': encoding,
            'line_count': len(lines),
            'character_count': len(content),
            'word_count': len(content.split()),
            'summary': f"{len(lines)} lines, {len(content.split())} words",
            'preview': '\n'.join(lines[:50])  # First 50 lines
        }
        
        return metadata
        
    def create_metadata_widget(self, metadata: dict, parent: QWidget = None) -> QWidget:
        """Create metadata display widget."""
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        
        # Summary cards
        summary_layout = QHBoxLayout()
        
        cards = [
            ("Lines", str(metadata.get('line_count', 0))),
            ("Words", str(metadata.get('word_count', 0))),
            ("Characters", str(metadata.get('character_count', 0))),
            ("Encoding", metadata.get('encoding', 'unknown'))
        ]
        
        for title, value in cards:
            card = QLabel(f"<b>{title}</b><br><font size='+1'>{value}</font>")
            card.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card.setStyleSheet("padding: 10px; border: 1px solid #555;")
            summary_layout.addWidget(card)
            
        layout.addLayout(summary_layout)
        
        # Preview
        preview_label = QLabel("<b>Preview (first 50 lines):</b>")
        layout.addWidget(preview_label)
        
        preview_text = QTextEdit()
        preview_text.setPlainText(metadata.get('preview', ''))
        preview_text.setReadOnly(True)
        preview_text.setFont(QFont("Courier New", 9))
        layout.addWidget(preview_text, stretch=1)
        
        return widget
        
    def create_visual_widget(self, filepath: str, parent: QWidget = None) -> QWidget:
        """Create visual preview widget."""
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        
        # Full text display
        text_edit = QTextEdit()
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception as e:
                content = f"Error reading file: {e}"
                
        text_edit.setPlainText(content)
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Courier New", 10))
        
        # Enable line wrap toggle
        text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        layout.addWidget(text_edit)
        
        return widget
