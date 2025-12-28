# Development Guide

Complete guide for developers working on AI Avatar Studio.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Development Setup](#development-setup)
3. [Architecture Overview](#architecture-overview)
4. [Adding New Features](#adding-new-features)
5. [Testing](#testing)
6. [Code Style](#code-style)
7. [Contributing](#contributing)

## Project Structure

```
AI Avatar Studio/
├── main.py                      # Application entry point
├── config/                      # Configuration
│   ├── settings.py             # Main settings
│   ├── constants.py            # Constants
│   └── paths.py                # Path management
├── core/                        # Core AI modules
│   ├── face_detection/         # Face detection
│   ├── tts/                    # Text-to-speech
│   ├── lip_sync/               # Wav2Lip integration
│   ├── video/                  # Video processing
│   ├── audio/                  # Audio processing
│   ├── image/                  # Image processing
│   └── pipeline/               # Generation pipeline
├── gui/                         # User interface
│   ├── splash_screen.py        # Splash screen
│   └── main_window.py          # Main window
├── utils/                       # Utilities
│   ├── database_manager.py     # Database operations
│   ├── logger.py               # Logging
│   ├── system_checker.py       # System checks
│   ├── model_manager.py        # Model management
│   ├── file_manager.py         # File operations
│   ├── backup_manager.py       # Backup system
│   └── cleanup_manager.py      # Cleanup utilities
├── examples/                    # Usage examples
├── scripts/                     # Helper scripts
├── docs/                        # Documentation
└── tests/                       # Test suite (if added)
```

## Development Setup

### Prerequisites

- Python 3.8-3.11
- Git
- FFmpeg
- CUDA Toolkit (optional, for GPU)

### Initial Setup

1. **Clone repository**:
```bash
git clone <repository-url>
cd "AI  Avatar  talking"
```

2. **Create virtual environment**:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**:
```bash
# Install base requirements
pip install -r requirements.txt

# Install development tools
pip install pytest pytest-cov black flake8 mypy
```

4. **Configure environment**:
```bash
# Copy example config
cp .env.example .env

# Edit configuration
notepad .env  # Windows
nano .env     # Linux/Mac
```

5. **Download models**:
```bash
python setup_models.py
```

6. **Verify setup**:
```bash
python verify_setup.py
python health_check.py --detailed
```

## Architecture Overview

### Core Components

#### 1. Face Detection System

Uses abstract base class pattern with multiple backends:

```python
# core/face_detection/base.py
class FaceDetector(ABC):
    @abstractmethod
    def detect_from_image(self, image: Image) -> Dict:
        pass

# core/face_detection/manager.py
class FaceDetectionManager:
    def __init__(self, preferred_backend='mediapipe'):
        self.backends = [
            MediaPipeDetector(),
            OpenCVDetector()
        ]
```

**Adding a new face detector**:

1. Create new file: `core/face_detection/my_detector.py`
2. Inherit from `FaceDetector` base class
3. Implement required methods
4. Register in `FaceDetectionManager`

Example:
```python
from core.face_detection.base import FaceDetector

class MyDetector(FaceDetector):
    def __init__(self):
        self.name = "my_detector"
    
    def detect_from_image(self, image: Image) -> Dict:
        # Your implementation
        return {
            'success': True,
            'face_count': 1,
            'landmarks': landmarks
        }
```

#### 2. TTS System

Similar architecture with multiple engines:

```python
# core/tts/base.py
class TTSEngine(ABC):
    @abstractmethod
    def synthesize(self, text: str, output_path: str) -> bool:
        pass

# core/tts/manager.py
class TTSManager:
    def __init__(self, preferred_engine='pyttsx3'):
        self.engines = [
            Pyttsx3Engine(),
            GTTSEngine(),
            CoquiEngine()
        ]
```

**Adding a new TTS engine**:

1. Create: `core/tts/my_engine.py`
2. Inherit from `TTSEngine`
3. Implement `synthesize()` method
4. Register in `TTSManager`

#### 3. Generation Pipeline

8-stage processing pipeline with progress callbacks:

```python
# core/pipeline/generation_pipeline.py
class GenerationPipeline:
    STAGES = [
        'validate',
        'face_detect',
        'tts',
        'audio_process',
        'lip_sync',
        'video_process',
        'enhance',
        'finalize'
    ]
    
    def generate(self, progress_callback=None):
        for stage in self.STAGES:
            self._run_stage(stage, progress_callback)
```

**Adding a new pipeline stage**:

1. Add stage name to `STAGES` list
2. Create `_stage_<name>()` method
3. Update progress callback handling
4. Update tests

#### 4. Database Layer

SQLite with 7 tables:

```python
# utils/database_manager.py
class DatabaseManager:
    TABLES = [
        'projects',
        'generations',
        'settings',
        'processing_logs',
        'model_versions',
        'user_preferences',
        'batch_queue'
    ]
```

**Adding a new table**:

1. Update `_create_tables()` method
2. Add CRUD methods for new table
3. Update database version
4. Create migration script

Example:
```python
def _create_my_table(self):
    cursor = self.conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS my_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    self.conn.commit()

def add_my_record(self, name: str) -> int:
    cursor = self.conn.cursor()
    cursor.execute(
        "INSERT INTO my_table (name) VALUES (?)",
        (name,)
    )
    self.conn.commit()
    return cursor.lastrowid
```

## Adding New Features

### 1. Adding Video Effects

Create new effect in `core/video/effects/`:

```python
# core/video/effects/my_effect.py
class MyEffect:
    def apply(self, frame: np.ndarray) -> np.ndarray:
        # Apply your effect
        return processed_frame

# Register in VideoProcessor
from core.video.effects.my_effect import MyEffect

class VideoProcessor:
    def __init__(self):
        self.effects = {
            'my_effect': MyEffect()
        }
```

### 2. Adding Audio Filters

Create filter in `core/audio/filters/`:

```python
# core/audio/filters/my_filter.py
class MyFilter:
    def apply(self, audio: np.ndarray, sr: int) -> np.ndarray:
        # Apply your filter
        return filtered_audio

# Register in AudioProcessor
from core.audio.filters.my_filter import MyFilter

class AudioProcessor:
    def __init__(self):
        self.filters = {
            'my_filter': MyFilter()
        }
```

### 3. Adding GUI Components

Create widget in `gui/widgets/`:

```python
# gui/widgets/my_widget.py
import customtkinter as ctk

class MyWidget(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._setup_ui()
    
    def _setup_ui(self):
        # Create your UI elements
        pass

# Add to main window
from gui.widgets.my_widget import MyWidget

class MainWindow:
    def __init__(self):
        self.my_widget = MyWidget(self)
```

### 4. Adding CLI Commands

Create command in root directory:

```python
# my_command.py
import argparse

class MyCommand:
    def run(self, args):
        # Your command logic
        pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--option', help='Description')
    args = parser.parse_args()
    
    cmd = MyCommand()
    cmd.run(args)

if __name__ == "__main__":
    main()
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=utils

# Run specific test
pytest tests/test_face_detection.py

# Run component tests
python run_avatar_test.py
```

### Writing Tests

Create test file in `tests/`:

```python
# tests/test_my_feature.py
import pytest
from core.my_feature import MyFeature

class TestMyFeature:
    def setup_method(self):
        self.feature = MyFeature()
    
    def test_basic_functionality(self):
        result = self.feature.process()
        assert result is not None
    
    def test_error_handling(self):
        with pytest.raises(ValueError):
            self.feature.process(invalid_input)
```

### Integration Tests

```python
# tests/integration/test_pipeline.py
def test_full_pipeline():
    from core.pipeline import GenerationPipeline
    
    pipeline = GenerationPipeline()
    result = pipeline.generate(
        image_path='test.jpg',
        text='Test'
    )
    
    assert result['success'] is True
    assert os.path.exists(result['output_path'])
```

## Code Style

### Python Style Guide

Follow PEP 8 with these specifics:

- **Line length**: 100 characters
- **Indentation**: 4 spaces
- **Quotes**: Single quotes for strings
- **Imports**: Grouped (stdlib, third-party, local)

### Formatting Tools

```bash
# Format code
black --line-length 100 .

# Check style
flake8 --max-line-length 100

# Type checking
mypy core/ utils/
```

### Docstrings

Use Google-style docstrings:

```python
def my_function(arg1: str, arg2: int) -> bool:
    """
    Short description.
    
    Longer description explaining the function.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When invalid input
    
    Example:
        >>> my_function('test', 42)
        True
    """
    pass
```

### Naming Conventions

- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`
- **Modules**: `lowercase` or `snake_case`

## Contributing

### Workflow

1. **Create branch**:
```bash
git checkout -b feature/my-feature
```

2. **Make changes**:
```bash
# Edit files
git add .
git commit -m "Add: my feature description"
```

3. **Test changes**:
```bash
python run_avatar_test.py
pytest
python health_check.py
```

4. **Update documentation**:
- Update relevant .md files
- Add docstrings
- Update CHANGELOG.md

5. **Submit pull request**:
```bash
git push origin feature/my-feature
# Create PR on GitHub
```

### Commit Messages

Follow conventional commits:

```
Add: New feature
Fix: Bug fix
Update: Existing feature update
Refactor: Code refactoring
Docs: Documentation changes
Test: Test additions/changes
Style: Code style changes
Perf: Performance improvements
```

Examples:
```
Add: Support for custom voice models
Fix: Memory leak in video processing
Update: Improve face detection accuracy
Docs: Add development guide
```

### Code Review Checklist

Before submitting:

- [ ] Code follows style guide
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Performance impact considered
- [ ] Error handling implemented
- [ ] Logging added where appropriate

## Debugging

### Logging

Enable debug logging:

```python
# In .env
LOG_LEVEL=DEBUG

# Or programmatically
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

### Common Issues

**Import errors**:
```bash
# Verify PYTHONPATH
echo $PYTHONPATH

# Add to path
export PYTHONPATH="${PYTHONPATH}:/path/to/project"
```

**CUDA errors**:
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Set CPU mode
# In .env: USE_GPU=false
```

**Database locked**:
```bash
# Close all connections
# Or delete lock file
rm data/database/projects.db-journal
```

### Profiling

```python
# Time profiling
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumtime')
stats.print_stats(20)

# Memory profiling
from memory_profiler import profile

@profile
def my_function():
    # Your code
    pass
```

### Debugging Tools

```bash
# Python debugger
python -m pdb main.py

# IPython debugger (better)
pip install ipdb
# Add to code: import ipdb; ipdb.set_trace()

# VS Code debugging
# Use launch.json configuration
```

## Performance Optimization

### Guidelines

1. **Use GPU when available**
2. **Cache expensive operations**
3. **Process in batches**
4. **Use generators for large datasets**
5. **Profile before optimizing**

### Example Optimizations

```python
# Cache decorator
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(arg):
    # Cached result
    return result

# Generator for memory efficiency
def process_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield process_frame(frame)
    cap.release()

# Batch processing
def process_batch(items, batch_size=32):
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        yield process(batch)
```

## Deployment

### Building Distribution

```bash
# Create distribution
python setup.py sdist bdist_wheel

# Install locally
pip install dist/ai_avatar_studio-*.whl
```

### Docker Deployment

```bash
# Build image
docker build -t ai-avatar-studio .

# Run container
docker-compose up -d

# Check logs
docker-compose logs -f
```

### System Service

**Linux (systemd)**:
```ini
# /etc/systemd/system/ai-avatar.service
[Unit]
Description=AI Avatar Studio
After=network.target

[Service]
Type=simple
User=avatar
WorkingDirectory=/opt/ai-avatar-studio
ExecStart=/opt/ai-avatar-studio/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Windows (Service)**:
```bash
# Use NSSM
nssm install AIAvatarStudio "C:\Python\python.exe" "C:\AI Avatar Studio\main.py"
```

## Resources

- **Python Docs**: https://docs.python.org/3/
- **PyTorch**: https://pytorch.org/docs/
- **OpenCV**: https://docs.opencv.org/
- **FFmpeg**: https://ffmpeg.org/documentation.html
- **CustomTkinter**: https://github.com/TomSchimansky/CustomTkinter

## Support

- **Issues**: Create issue on GitHub
- **Discussions**: Use GitHub Discussions
- **Email**: support@example.com (update with actual)

## License

See LICENSE file for details.
