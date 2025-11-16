# Plugin Development Guide

Learn how to create custom plugins for OpenUP to support new file formats.

## Overview

OpenUP uses a plugin architecture where each file format is handled by a dedicated plugin. Plugins implement a standard interface and are automatically discovered at startup.

## Plugin Structure

Every plugin must:
1. Inherit from `PreviewPlugin` base class
2. Define supported file extensions
3. Implement metadata extraction
4. Provide metadata display widget
5. Provide visual preview widget

## Minimal Plugin Example

```python
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from src.core.plugin_base import PreviewPlugin


class MyFormatPlugin(PreviewPlugin):
    """Plugin for .myformat files."""
    
    # Plugin metadata
    extensions = ['.myformat', '.mf']
    domain = "Custom"
    name = "My Format Viewer"
    version = "1.0.0"
    description = "Preview custom .myformat files"
    author = "Your Name"
    
    # Performance hints
    max_file_size_mb = 100
    supports_caching = True
    
    def get_metadata(self, filepath: str) -> dict:
        """Extract metadata from file."""
        path = Path(filepath)
        
        # Read and parse your file
        # ... your parsing logic here ...
        
        return {
            'file_name': path.name,
            'file_size': path.stat().st_size,
            'file_type': 'My Custom Format',
            'summary': 'File summary here',
            # Add your custom metadata
            'custom_field': 'value',
        }
        
    def create_metadata_widget(self, metadata: dict, parent: QWidget = None) -> QWidget:
        """Create widget to display metadata."""
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        
        # Display metadata
        for key, value in metadata.items():
            label = QLabel(f"<b>{key}:</b> {value}")
            layout.addWidget(label)
            
        return widget
        
    def create_visual_widget(self, filepath: str, parent: QWidget = None) -> QWidget:
        """Create widget to display visual preview."""
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        
        # Create your visualization
        preview = QLabel("Your custom visualization here")
        layout.addWidget(preview)
        
        return widget
```

## Step-by-Step Guide

### 1. Create Plugin File

Create a new Python file in `src/plugins/`:

```bash
src/plugins/my_format_plugin.py
```

### 2. Import Required Modules

```python
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from src.core.plugin_base import PreviewPlugin
```

### 3. Define Plugin Class

```python
class MyFormatPlugin(PreviewPlugin):
    extensions = ['.myformat']
    domain = "Custom"
    name = "My Format Viewer"
    # ... metadata ...
```

### 4. Implement `get_metadata()`

This method extracts metadata from the file. It should return a dictionary with at least:

```python
def get_metadata(self, filepath: str) -> dict:
    # Parse file
    data = self._parse_file(filepath)
    
    return {
        'file_name': Path(filepath).name,
        'file_size': Path(filepath).stat().st_size,
        'file_type': 'My Format',
        'summary': 'Brief summary',
        # Your custom metadata
        'record_count': len(data),
        'version': data.version,
    }
```

### 5. Implement `create_metadata_widget()`

Create a PyQt widget to display metadata:

```python
def create_metadata_widget(self, metadata: dict, parent: QWidget = None) -> QWidget:
    widget = QWidget(parent)
    layout = QVBoxLayout(widget)
    
    # Summary cards
    summary = QLabel(f"<h3>{metadata['summary']}</h3>")
    layout.addWidget(summary)
    
    # Detailed table
    from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
    table = QTableWidget()
    table.setColumnCount(2)
    table.setHorizontalHeaderLabels(["Property", "Value"])
    
    # Add rows
    for key, value in metadata.items():
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(str(key)))
        table.setItem(row, 1, QTableWidgetItem(str(value)))
    
    layout.addWidget(table)
    return widget
```

### 6. Implement `create_visual_widget()`

Create a widget for visual preview:

```python
def create_visual_widget(self, filepath: str, parent: QWidget = None) -> QWidget:
    widget = QWidget(parent)
    layout = QVBoxLayout(widget)
    
    # Your visualization logic
    # For images:
    from PyQt6.QtWidgets import QLabel
    from PyQt6.QtGui import QPixmap
    image_label = QLabel()
    image_label.setPixmap(QPixmap(filepath))
    layout.addWidget(image_label)
    
    # For text:
    from PyQt6.QtWidgets import QTextEdit
    text_edit = QTextEdit()
    text_edit.setPlainText(open(filepath).read())
    text_edit.setReadOnly(True)
    layout.addWidget(text_edit)
    
    # For 3D (with Open3D):
    # ... Open3D canvas setup ...
    
    return widget
```

### 7. Test Your Plugin

```python
# Create test file
# Run OpenUP
python main.py
# Open a .myformat file
```

## Advanced Features

### File Size Limits

```python
class MyPlugin(PreviewPlugin):
    max_file_size_mb = 50  # Reject files > 50 MB
```

### Custom Probe Logic

Override `probe()` for advanced file detection:

```python
def probe(self, filepath: str) -> bool:
    """Check if file is really our format."""
    # Check file signature/magic bytes
    with open(filepath, 'rb') as f:
        header = f.read(4)
        return header == b'MYFM'  # Your format signature
```

### Streaming for Large Files

```python
class MyPlugin(PreviewPlugin):
    supports_streaming = True
    
    def get_metadata(self, filepath: str) -> dict:
        # Read file in chunks
        chunk_size = 1024 * 1024  # 1 MB
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                # Process chunk
```

### Background Processing

Use WorkerPool for heavy operations:

```python
def create_visual_widget(self, filepath: str, parent: QWidget = None) -> QWidget:
    widget = QWidget(parent)
    
    # Submit heavy work to worker pool
    from src.core.worker_pool import WorkerPool
    pool = WorkerPool()
    
    signals = pool.submit_task(
        f"process:{filepath}",
        self._heavy_processing,
        filepath
    )
    
    signals.finished.connect(
        lambda result: self._update_widget(widget, result)
    )
    
    return widget
```

### Caching

Enable caching for faster re-opening:

```python
class MyPlugin(PreviewPlugin):
    supports_caching = True  # Enable caching
    
    def get_metadata(self, filepath: str) -> dict:
        # Metadata will be automatically cached
        # and retrieved on next open
        pass
```

## Testing

Create unit tests for your plugin:

```python
# tests/test_my_plugin.py
import pytest
from src.plugins.my_format_plugin import MyFormatPlugin

def test_metadata_extraction(tmp_path):
    # Create test file
    test_file = tmp_path / "test.myformat"
    test_file.write_text("test data")
    
    # Test plugin
    plugin = MyFormatPlugin()
    metadata = plugin.get_metadata(str(test_file))
    
    assert metadata['file_name'] == 'test.myformat'
    assert 'summary' in metadata
```

## Best Practices

1. **Error Handling**: Always wrap file operations in try/except
2. **Memory Efficiency**: Don't load entire file into memory for large files
3. **User Feedback**: Show progress for long operations
4. **Cleanup**: Release resources in `cleanup()` method
5. **Documentation**: Add docstrings and comments
6. **Testing**: Write unit tests for your plugin

## Plugin Distribution

### Share Your Plugin

1. Create GitHub repository for your plugin
2. Add installation instructions
3. Submit pull request to add plugin to OpenUP

### Plugin Package Structure

```
my-plugin/
├── README.md
├── requirements.txt
├── my_format_plugin.py
└── tests/
    └── test_my_plugin.py
```

## Examples

See existing plugins for reference:
- `src/plugins/text_plugin.py` - Simple text file viewer
- `src/plugins/image_plugin.py` - Image viewer with metadata
- `src/plugins/data_plugin.py` - CSV/Excel viewer with statistics

## Need Help?

- Check existing plugins in `src/plugins/`
- Read the [API Documentation](API.md)
- Ask in [GitHub Discussions](https://github.com/Rajveersinghcse1/Web-dev/discussions)

Happy plugin development! 🔌
