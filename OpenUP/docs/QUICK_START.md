# OpenUP Quick Start Guide

Get up and running with OpenUP in 5 minutes!

## Installation

### Option 1: From Source

```bash
# Clone repository
git clone https://github.com/Rajveersinghcse1/Web-dev.git
cd "Formate Viewer/OpenUP"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Option 2: Binary Download (Coming Soon)

Download pre-built executables from GitHub Releases.

## First Steps

### 1. Launch OpenUP

```bash
python main.py
```

### 2. Open a File

**Method A: File Browser**
- Use the left panel to browse your files
- Double-click any supported file

**Method B: Drag & Drop**
- Drag any file from your file explorer
- Drop it onto the OpenUP window

**Method C: File Menu**
- Click File > Open File...
- Select your file

### 3. View File Preview

Once opened, you'll see two tabs:

- **📊 Metadata / Table**: File information, statistics, and tabular data
- **👁 Visualization**: Visual preview (image, text editor, 3D view, etc.)

## Supported File Types

OpenUP currently supports:

| Domain | Extensions |
|--------|-----------|
| **Documents** | `.txt`, `.md`, `.log` |
| **Images** | `.png`, `.jpg`, `.jpeg`, `.bmp`, `.gif`, `.tiff`, `.webp` |
| **Data** | `.csv`, `.tsv`, `.xlsx`, `.xls` |

More formats coming soon!

## Key Features

### Filtering by Domain

Use the domain filter in the left panel to show only files from specific domains (Documents, Images, Data, etc.)

### Recent Files

Access recently opened files via File > Recent Files

### Cache Management

OpenUP caches metadata to speed up re-opening files. To clear cache:
- Tools > Clear Cache

### Settings

Customize OpenUP via Tools > Settings:
- **Theme**: Dark or Light mode
- **Cache Size**: Maximum cache size in MB
- **Worker Threads**: Number of background workers
- **GPU Acceleration**: Enable/disable GPU for 3D rendering

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open file |
| `Ctrl+R` | Refresh current file |
| `Ctrl+B` | Toggle file browser |
| `Ctrl+Q` | Quit |
| `F11` | Fullscreen (coming soon) |

## Tips & Tricks

### Large Files

OpenUP intelligently handles large files:
- Streams data instead of loading everything into memory
- Downsamples point clouds and images for display
- Shows first N rows for CSV files

### Custom Plugins

You can create custom plugins to support new file formats! See the Plugin Development Guide.

### Command Line

Open files directly from command line:

```bash
python main.py path/to/your/file.txt
```

## Troubleshooting

### "No plugin available" error

This means OpenUP doesn't have a plugin for that file type yet. Check the roadmap for upcoming format support.

### Application won't start

1. Ensure Python 3.11+ is installed
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Check logs in `~/.openup/logs/`

### Slow performance

1. Reduce cache size in Settings
2. Decrease worker threads in Settings
3. Disable GPU acceleration if causing issues

## Getting Help

- **Documentation**: See `docs/` folder
- **Issues**: https://github.com/Rajveersinghcse1/Web-dev/issues
- **Discussions**: https://github.com/Rajveersinghcse1/Web-dev/discussions

## Next Steps

- Read the [User Guide](docs/USER_GUIDE.md) for detailed information
- Learn about [Plugin Development](docs/PLUGIN_DEVELOPMENT.md)
- Check the [Architecture](docs/ARCHITECTURE.md) document

Enjoy using OpenUP! 🚀
