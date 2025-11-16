"""CSV and Excel file preview plugin."""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QHBoxLayout
)
from PyQt6.QtCore import Qt
import pandas as pd
import humanize

from src.core.plugin_base import PreviewPlugin


class DataPlugin(PreviewPlugin):
    """Plugin for previewing CSV and Excel files."""
    
    extensions = ['.csv', '.tsv', '.xlsx', '.xls']
    domain = "Data"
    name = "Data Table Viewer"
    version = "1.0.0"
    description = "Preview CSV and Excel files with statistics"
    author = "OpenUP Team"
    max_file_size_mb = 200
    supports_caching = True
    supports_streaming = True
    
    def get_metadata(self, filepath: str) -> dict:
        """Extract metadata from data file."""
        path = Path(filepath)
        ext = path.suffix.lower()
        
        try:
            # Read file
            if ext == '.csv':
                df = pd.read_csv(filepath, nrows=1000)  # Limit rows for preview
            elif ext == '.tsv':
                df = pd.read_csv(filepath, sep='\t', nrows=1000)
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(filepath, nrows=1000)
            else:
                raise ValueError(f"Unsupported extension: {ext}")
                
            # Calculate statistics
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            stats = {}
            if len(numeric_cols) > 0:
                stats = {
                    col: {
                        'mean': float(df[col].mean()),
                        'std': float(df[col].std()),
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                    }
                    for col in numeric_cols
                }
                
            metadata = {
                'file_name': path.name,
                'file_size': path.stat().st_size,
                'file_type': f'Data Table ({ext[1:].upper()})',
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'summary': f"{len(df)} rows × {len(df.columns)} columns",
                'stats': stats,
                'preview_rows': df.head(100).to_dict('records'),  # First 100 rows
                'memory_usage': df.memory_usage(deep=True).sum()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to read data file: {e}")
            metadata = {
                'file_name': path.name,
                'file_size': path.stat().st_size,
                'file_type': 'Data Table',
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
                ("Rows", str(metadata.get('row_count', 0))),
                ("Columns", str(metadata.get('column_count', 0))),
                ("Memory", humanize.naturalsize(metadata.get('memory_usage', 0))),
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
        
        if 'error' in metadata:
            return widget
            
        # Column information table
        layout.addWidget(QLabel("<b>Column Information:</b>"))
        
        col_table = QTableWidget()
        col_table.setColumnCount(2)
        col_table.setHorizontalHeaderLabels(["Column", "Type"])
        
        columns = metadata.get('columns', [])
        dtypes = metadata.get('dtypes', {})
        
        col_table.setRowCount(len(columns))
        for row, col in enumerate(columns):
            col_table.setItem(row, 0, QTableWidgetItem(col))
            col_table.setItem(row, 1, QTableWidgetItem(dtypes.get(col, 'unknown')))
            
        col_table.resizeColumnsToContents()
        layout.addWidget(col_table, stretch=1)
        
        return widget
        
    def create_visual_widget(self, filepath: str, parent: QWidget = None) -> QWidget:
        """Create visual preview widget."""
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        
        path = Path(filepath)
        ext = path.suffix.lower()
        
        try:
            # Read file
            if ext == '.csv':
                df = pd.read_csv(filepath, nrows=1000)
            elif ext == '.tsv':
                df = pd.read_csv(filepath, sep='\t', nrows=1000)
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(filepath, nrows=1000)
            else:
                raise ValueError(f"Unsupported extension: {ext}")
                
            # Create table
            table = QTableWidget()
            table.setRowCount(len(df))
            table.setColumnCount(len(df.columns))
            table.setHorizontalHeaderLabels([str(col) for col in df.columns])
            
            # Populate table
            for row_idx, row in df.iterrows():
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    table.setItem(row_idx, col_idx, item)
                    
            table.resizeColumnsToContents()
            
            # Add info label
            info_label = QLabel(
                f"<i>Showing first {len(df)} rows. "
                f"File may contain more data.</i>"
            )
            layout.addWidget(info_label)
            
            layout.addWidget(table, stretch=1)
            
        except Exception as e:
            error_label = QLabel(f"Error loading data:\n{e}")
            error_label.setStyleSheet("color: red; padding: 20px;")
            layout.addWidget(error_label)
            
        return widget
