"""Image file preview plugin."""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QHBoxLayout, QTableWidget, QTableWidgetItem
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from PIL import Image
import humanize

from src.core.plugin_base import PreviewPlugin


class ImagePlugin(PreviewPlugin):
    """Plugin for previewing image files."""
    
    extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif', '.webp']
    domain = "Images"
    name = "Image Viewer"
    version = "1.0.0"
    description = "Preview raster images with metadata"
    author = "OpenUP Team"
    max_file_size_mb = 500
    supports_caching = True
    
    def get_metadata(self, filepath: str) -> dict:
        """Extract metadata from image file."""
        path = Path(filepath)
        
        try:
            img = Image.open(filepath)
            
            metadata = {
                'file_name': path.name,
                'file_size': path.stat().st_size,
                'file_type': f'Image ({img.format})',
                'width': img.width,
                'height': img.height,
                'mode': img.mode,
                'format': img.format,
                'summary': f"{img.width}x{img.height} {img.mode}",
                'dpi': img.info.get('dpi', 'N/A'),
                'has_transparency': img.mode in ('RGBA', 'LA', 'P'),
            }
            
            # EXIF data if available
            if hasattr(img, '_getexif') and img._getexif():
                metadata['has_exif'] = True
            else:
                metadata['has_exif'] = False
                
            img.close()
            
        except Exception as e:
            self.logger.error(f"Failed to read image: {e}")
            metadata = {
                'file_name': path.name,
                'file_size': path.stat().st_size,
                'file_type': 'Image',
                'error': str(e)
            }
            
        return metadata
        
    def create_metadata_widget(self, metadata: dict, parent: QWidget = None) -> QWidget:
        """Create metadata display widget."""
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        
        # Summary cards
        summary_layout = QHBoxLayout()
        
        if 'error' not in metadata:
            cards = [
                ("Dimensions", f"{metadata.get('width', 0)}x{metadata.get('height', 0)}"),
                ("Format", metadata.get('format', 'Unknown')),
                ("Mode", metadata.get('mode', 'Unknown')),
                ("Size", humanize.naturalsize(metadata.get('file_size', 0)))
            ]
        else:
            cards = [("Error", metadata['error'])]
            
        for title, value in cards:
            card = QLabel(f"<b>{title}</b><br><font size='+1'>{value}</font>")
            card.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card.setStyleSheet("padding: 10px; border: 1px solid #555;")
            summary_layout.addWidget(card)
            
        layout.addLayout(summary_layout)
        
        # Detailed table
        if 'error' not in metadata:
            table = QTableWidget()
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["Property", "Value"])
            
            properties = [
                ("File Name", metadata.get('file_name', '')),
                ("Format", metadata.get('format', '')),
                ("Width", str(metadata.get('width', 0))),
                ("Height", str(metadata.get('height', 0))),
                ("Mode", metadata.get('mode', '')),
                ("DPI", str(metadata.get('dpi', 'N/A'))),
                ("Has Transparency", str(metadata.get('has_transparency', False))),
                ("Has EXIF", str(metadata.get('has_exif', False))),
            ]
            
            table.setRowCount(len(properties))
            for row, (prop, value) in enumerate(properties):
                table.setItem(row, 0, QTableWidgetItem(prop))
                table.setItem(row, 1, QTableWidgetItem(value))
                
            table.resizeColumnsToContents()
            layout.addWidget(table, stretch=1)
        
        return widget
        
    def create_visual_widget(self, filepath: str, parent: QWidget = None) -> QWidget:
        """Create visual preview widget."""
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        
        # Scroll area for image
        scroll = QScrollArea()
        scroll.setWidgetResizable(False)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Image label
        image_label = QLabel()
        
        try:
            pixmap = QPixmap(filepath)
            
            # Scale down if too large (max 1920x1080 for display)
            if pixmap.width() > 1920 or pixmap.height() > 1080:
                pixmap = pixmap.scaled(
                    1920, 1080,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
            image_label.setPixmap(pixmap)
            
        except Exception as e:
            image_label.setText(f"Error loading image:\n{e}")
            image_label.setStyleSheet("color: red; padding: 20px;")
            
        scroll.setWidget(image_label)
        layout.addWidget(scroll)
        
        return widget
