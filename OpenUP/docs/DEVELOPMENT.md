# OpenUP - Development & Deployment Guide

## Project Structure

```
OpenUP/
├── main.py                 # Application entry point
├── setup.py               # Package configuration
├── requirements.txt       # Dependencies
├── openup.spec           # PyInstaller specification
├── LICENSE               # MIT License
├── README.md             # Project overview
├── .gitignore           # Git ignore rules
│
├── src/                  # Source code
│   ├── __init__.py
│   ├── core/            # Core components
│   │   ├── config.py         # Configuration management
│   │   ├── logger.py         # Logging setup
│   │   ├── plugin_base.py    # Plugin interface
│   │   ├── plugin_manager.py # Plugin loader
│   │   ├── worker_pool.py    # Background workers
│   │   └── cache_manager.py  # Cache system
│   │
│   ├── ui/              # User interface
│   │   ├── main_window.py    # Main application window
│   │   ├── file_browser.py   # File navigation widget
│   │   ├── domain_filter.py  # Domain filter widget
│   │   ├── preview_area.py   # Preview container
│   │   ├── dialogs.py        # Dialog windows
│   │   └── themes.py         # Dark/light themes
│   │
│   ├── plugins/         # File format plugins
│   │   ├── text_plugin.py    # Text files
│   │   ├── image_plugin.py   # Images
│   │   ├── data_plugin.py    # CSV/Excel
│   │   └── ... (more plugins)
│   │
│   └── utils/           # Utility functions
│       └── helpers.py        # Helper functions
│
├── tests/               # Unit tests
│   ├── test_core.py         # Core component tests
│   └── assets/              # Test files
│
├── docs/                # Documentation
│   ├── QUICK_START.md       # Quick start guide
│   ├── PLUGIN_DEVELOPMENT.md # Plugin development
│   └── ... (more docs)
│
├── resources/           # Application resources
│   └── icons/              # Icon files
│
├── cache/              # Runtime cache (gitignored)
└── logs/               # Application logs (gitignored)
```

## Development Setup

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

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

# Install in development mode
pip install -e .
```

### Running the Application

```bash
# From project root
python main.py

# Or with a file argument
python main.py path/to/file.txt
```

### Development Workflow

1. **Make changes** to source files in `src/`
2. **Test changes** by running the application
3. **Run tests** with `pytest`
4. **Commit changes** with descriptive messages

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run with verbose output
pytest -v
```

### Writing Tests

Create test files in `tests/` directory:

```python
# tests/test_my_feature.py
import pytest
from src.core.my_module import MyClass

def test_my_feature():
    obj = MyClass()
    assert obj.do_something() == expected_result
```

## Building Executables

### Using PyInstaller

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller openup.spec

# Output will be in dist/OpenUP/
```

### Platform-Specific Builds

**Windows:**
```powershell
# Build
pyinstaller openup.spec

# Create installer (optional, requires NSIS)
makensis installer.nsi
```

**macOS:**
```bash
# Build app bundle
pyinstaller openup.spec

# Sign app (optional)
codesign --deep --force --verify --verbose --sign "Developer ID" dist/OpenUP.app

# Create DMG (optional, requires create-dmg)
create-dmg dist/OpenUP.app
```

**Linux:**
```bash
# Build
pyinstaller openup.spec

# Create AppImage (optional, requires appimagetool)
appimagetool dist/OpenUP
```

## Deployment

### Version Control

```bash
# Stage changes
git add .

# Commit
git commit -m "Description of changes"

# Push to remote
git push origin main
```

### Creating Releases

1. **Update version** in `src/__init__.py` and `setup.py`
2. **Update CHANGELOG.md**
3. **Tag release**:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```
4. **Build executables** for all platforms
5. **Create GitHub Release** and upload executables

### CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/build.yml`:

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: pytest --cov=src
```

## Code Quality

### Linting

```bash
# Install linters
pip install flake8 black isort

# Format code
black src/
isort src/

# Check style
flake8 src/
```

### Type Checking

```bash
# Install mypy
pip install mypy

# Run type checker
mypy src/
```

## Performance Optimization

### Profiling

```python
# Profile application
python -m cProfile -o profile.stats main.py

# Analyze results
python -m pstats profile.stats
```

### Memory Profiling

```python
# Install memory_profiler
pip install memory_profiler

# Profile memory usage
python -m memory_profiler main.py
```

## Security

### Dependency Scanning

```bash
# Install safety
pip install safety

# Check for vulnerabilities
safety check

# Update dependencies
pip list --outdated
pip install --upgrade package_name
```

## Documentation

### Building Documentation

```bash
# Install Sphinx (if using)
pip install sphinx sphinx_rtd_theme

# Build HTML docs
cd docs/
make html

# View in browser
open _build/html/index.html
```

### API Documentation

Generate API docs from docstrings:

```bash
# Install pdoc
pip install pdoc3

# Generate docs
pdoc --html --output-dir docs/api src/
```

## Troubleshooting

### Common Issues

**Import errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**PyQt6 issues:**
- Windows: May need to install Visual C++ Redistributable
- Linux: Install Qt dependencies: `sudo apt-get install python3-pyqt6`

**Build failures:**
- Clear build cache: `rm -rf build/ dist/`
- Rebuild: `pyinstaller --clean openup.spec`

### Debug Mode

Enable debug logging:

```python
# In main.py
setup_logging(log_level='DEBUG')
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open Pull Request

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for all functions/classes
- Add unit tests for new features

## Support

- **Issues**: https://github.com/Rajveersinghcse1/Web-dev/issues
- **Discussions**: https://github.com/Rajveersinghcse1/Web-dev/discussions
- **Email**: support@openup.dev

## License

MIT License - see LICENSE file for details

---

**Happy Coding! 🚀**
