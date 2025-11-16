"""LAS/LAZ file viewer plugin for OpenUP."""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QTextEdit, QHeaderView, QTabWidget
)
from PyQt6.QtCore import Qt
from src.core.plugin_base import PreviewPlugin

logger = logging.getLogger(__name__)


class LASPlugin(PreviewPlugin):
    """
    Plugin for viewing LAS/LAZ point cloud files.
    Displays point data in table format.
    """
    
    name = "LAS Point Cloud Viewer"
    version = "1.0.0"
    extensions = ['.las', '.laz']
    domain = "Geospatial"
    
    def probe(self, filepath: str) -> bool:
        """Check if file is a valid LAS/LAZ file."""
        try:
            path = Path(filepath)
            if not path.exists():
                return False
            
            # Check file signature (LAS files start with "LASF")
            with open(filepath, 'rb') as f:
                signature = f.read(4)
                return signature == b'LASF'
        except Exception as e:
            logger.error(f"Error probing LAS file: {e}")
            return False
    
    def get_metadata(self, filepath: str) -> dict:
        """Extract metadata from LAS file."""
        try:
            metadata = {
                'file_name': Path(filepath).name,
                'file_size': Path(filepath).stat().st_size,
                'file_format': 'LAS Point Cloud',
            }
            
            # Try to read LAS header
            try:
                import laspy
                with laspy.open(filepath) as las_file:
                    header = las_file.header
                    metadata.update({
                        'point_count': header.point_count,
                        'version': f"{header.version.major}.{header.version.minor}",
                        'point_format': header.point_format.id,
                        'x_min': header.x_min,
                        'x_max': header.x_max,
                        'y_min': header.y_min,
                        'y_max': header.y_max,
                        'z_min': header.z_min,
                        'z_max': header.z_max,
                        'x_scale': header.x_scale,
                        'y_scale': header.y_scale,
                        'z_scale': header.z_scale,
                    })
                    
                    # Get available dimensions
                    points = las_file.read()
                    metadata['dimensions'] = list(points.point_format.dimension_names)
                    
            except ImportError:
                # Fallback: Read basic header without laspy
                with open(filepath, 'rb') as f:
                    f.seek(0)
                    signature = f.read(4).decode('ascii')
                    metadata['signature'] = signature
                    
                    # Read version (bytes 24-25)
                    f.seek(24)
                    major = int.from_bytes(f.read(1), 'little')
                    minor = int.from_bytes(f.read(1), 'little')
                    metadata['version'] = f"{major}.{minor}"
                    
                    # Read point count (varies by version, try offset 107)
                    f.seek(107)
                    point_count = int.from_bytes(f.read(4), 'little')
                    metadata['point_count'] = point_count
                    
                    metadata['note'] = 'Install laspy for full LAS support: pip install laspy'
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting LAS metadata: {e}")
            return {
                'error': str(e),
                'file_name': Path(filepath).name,
                'note': 'Could not read LAS file. Install laspy: pip install laspy'
            }
    
    def create_metadata_widget(self, metadata: dict, parent=None) -> QWidget:
        """Create widget to display LAS metadata."""
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        
        # Create text widget for metadata
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # Format metadata
        content = "📊 LAS Point Cloud Metadata\n\n"
        
        for key, value in metadata.items():
            if key == 'dimensions' and isinstance(value, list):
                content += f"📐 Available Dimensions:\n"
                for dim in value:
                    content += f"   • {dim}\n"
            else:
                content += f"{key.replace('_', ' ').title()}: {value}\n"
        
        text_edit.setText(content)
        layout.addWidget(text_edit)
        
        return widget
    
    def create_visual_widget(self, filepath: str, parent=None) -> QWidget:
        """Create widget to display LAS point data in table format."""
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        
        try:
            # Try to use laspy
            try:
                import laspy
                
                with laspy.open(filepath) as las_file:
                    points = las_file.read()
                    
                    # Get available dimensions
                    dimensions = list(points.point_format.dimension_names)
                    
                    # Limit to first 1000 points for preview
                    max_points = min(1000, len(points))
                    
                    # Create info label
                    info_label = QLabel(
                        f"📍 Displaying first {max_points:,} of {len(points):,} points"
                    )
                    layout.addWidget(info_label)
                    
                    # Create table
                    table = QTableWidget()
                    table.setRowCount(max_points)
                    table.setColumnCount(len(dimensions))
                    table.setHorizontalHeaderLabels(dimensions)
                    
                    # Populate table
                    for row in range(max_points):
                        for col, dim in enumerate(dimensions):
                            try:
                                value = getattr(points, dim)[row]
                                item = QTableWidgetItem(str(value))
                                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                                table.setItem(row, col, item)
                            except Exception as e:
                                logger.warning(f"Error reading dimension {dim}: {e}")
                    
                    # Auto-resize columns
                    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
                    table.setAlternatingRowColors(True)
                    
                    layout.addWidget(table)
                    
            except ImportError:
                # Show installation instructions
                label = QLabel(
                    "⚠️ LAS Support Not Available\n\n"
                    "To view LAS/LAZ point cloud data in table format,\n"
                    "install the required library:\n\n"
                    "pip install laspy\n\n"
                    "Then restart the application."
                )
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("font-size: 14px; padding: 40px;")
                layout.addWidget(label)
                
        except Exception as e:
            error_label = QLabel(f"❌ Error loading LAS file:\n{str(e)}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: red; padding: 20px;")
            layout.addWidget(error_label)
        
        return widget
