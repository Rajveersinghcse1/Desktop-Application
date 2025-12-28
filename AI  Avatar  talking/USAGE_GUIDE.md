# 🎬 AI Avatar Studio - Complete Usage Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Running the Application](#running-the-application)
4. [Using the GUI](#using-the-gui)
5. [CLI Commands](#cli-commands)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

---

## Quick Start

### With Docker (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd "AI  Avatar  talking"

# 2. Start the application
docker-compose up

# The GUI will open automatically
```

### Without Docker

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python main.py
```

---

## Installation

### Prerequisites

- **Python:** 3.8 - 3.11
- **FFmpeg:** 4.x or higher
- **Docker:** 20.10+ (optional but recommended)
- **GPU:** NVIDIA GPU with CUDA (optional, for faster processing)

### Option 1: Docker Installation (Recommended)

**Windows:**
```batch
# Run the setup script
scripts\docker_manage.bat setup

# Start the application
scripts\docker_manage.bat start
```

**Linux/Mac:**
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run the setup script
./scripts/docker_manage.sh setup

# Start the application
./scripts/docker_manage.sh start
```

### Option 2: Local Installation

**1. Install FFmpeg**

- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **Linux:** `sudo apt install ffmpeg`
- **Mac:** `brew install ffmpeg`

**2. Install Python Dependencies**

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**3. Configure Environment**

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
```

---

## Running the Application

### GUI Mode (Default)

```bash
# Docker
docker-compose up

# Local
python main.py
```

### CLI Mode (Testing)

```bash
# Docker
docker-compose run app python main.py --mode cli

# Local
python main.py --mode cli
```

### Options

```bash
python main.py [OPTIONS]

Options:
  --mode {gui|cli}     Run mode (default: gui)
  --log-level LEVEL    Logging level (default: INFO)
  --help              Show help message
```

---

## Using the GUI

### Main Window Overview

```
┌─────────────────────────────────────────────────────────┐
│  File   Tools   Help                                    │
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│   [Image     │         Script Text                      │
│    Preview]  │    ┌──────────────────────────┐         │
│              │    │ Enter your script here...│         │
│   Select     │    │                          │         │
│   Image      │    └──────────────────────────┘         │
│              │                                          │
│              │    Voice:  [Default ▼]                   │
│              │    Quality: [Balanced ▼]                 │
│              │    Resolution: [720p ▼]                  │
│              │    Speed: [───●───] 1.0x                 │
│              │                                          │
│              │    [🎬 Generate Avatar Video]            │
└──────────────┴──────────────────────────────────────────┘
```

### Step-by-Step Workflow

#### 1. Select Input Image

- Click **"Select Image"** button
- Choose an image file (JPG, PNG, BMP)
- **Requirements:**
  - Contains at least one face
  - Minimum resolution: 256x256
  - Maximum size: 10 MB
  - Face should be clearly visible

**Tips:**
- Use well-lit images
- Front-facing photos work best
- Avoid heavy makeup or accessories covering the mouth
- Higher resolution = better quality

#### 2. Enter Script Text

- Type or paste your script in the text area
- **Limits:**
  - Minimum: 1 character
  - Maximum: 5000 characters
  - Supports multiple languages

**Tips:**
- Use proper punctuation for natural pauses
- Break long scripts into sentences
- Avoid special characters that might confuse TTS

#### 3. Configure Settings

##### Voice Selection
- **Default:** System default voice
- **Male:** Male voice (if available)
- **Female:** Female voice (if available)

##### Quality Presets
- **Fast:** Quick processing, lower quality
  - CRF: 28
  - Processing time: ~1-2 minutes
  - File size: Smaller
  
- **Balanced:** Good quality, reasonable speed (Recommended)
  - CRF: 23
  - Processing time: ~2-4 minutes
  - File size: Medium
  
- **High:** Best quality, slower processing
  - CRF: 18
  - Processing time: ~4-8 minutes
  - File size: Larger

##### Resolution Options
- **480p (854×480):** Fast, small files
- **720p (1280×720):** Recommended for most uses
- **1080p (1920×1080):** Best quality, larger files

##### Speed Adjustment
- **Range:** 0.5x to 2.0x
- **Default:** 1.0x (normal speed)
- **Use cases:**
  - 0.5x: Slow, clear speech
  - 1.0x: Natural speed
  - 1.5x: Faster delivery
  - 2.0x: Very fast

#### 4. Generate Video

1. Click **"🎬 Generate Avatar Video"**
2. Wait for processing (button shows "Generating...")
3. Monitor progress in status messages
4. When complete, view result location

**Processing Stages:**
1. ✓ Validation
2. ✓ Face Detection
3. ✓ Audio Generation
4. ✓ Audio Processing
5. ✓ Lip Sync
6. ✓ Video Encoding
7. ✓ Thumbnail Generation
8. ✓ Finalization

#### 5. View Results

**Output Location:**
- Docker: `./docker_volumes/output/`
- Local: `./output/`

**Files Created:**
- `avatar_<id>.mp4` - Generated video
- `avatar_<id>.jpg` - Thumbnail

---

## CLI Commands

When running in CLI mode, you have access to:

### 1. System Check
```
Command: 1

Checks:
- Python version
- FFmpeg installation
- Disk space
- RAM availability
- GPU detection (if available)
```

### 2. View Statistics
```
Command: 2

Shows:
- Total projects
- Total generations
- Completed/failed counts
- Success rate
- Average processing time
```

### 3. List Projects
```
Command: 3

Displays:
- Project names
- Status (active/completed/failed)
- Creation dates
```

### 4. Clean Cache
```
Command: 4

Removes:
- Temporary files
- Old processing data
- Cached models (optional)
```

### 5. Exit
```
Command: 0

Cleanly exits the application
```

---

## Configuration

### Environment Variables

Edit `.env` file for configuration:

```bash
# Application
APP_VERSION=1.0.0
DEBUG=false

# Paths (Docker auto-detected)
DATA_DIR=/app/data
MODELS_DIR=/app/models
OUTPUT_DIR=/app/output

# Database
DATABASE_PATH=/app/data/database/projects.db
BACKUP_RETENTION_DAYS=30

# Processing
DEFAULT_QUALITY=balanced
DEFAULT_RESOLUTION=720p
DEFAULT_SPEED=1.0
MAX_TEXT_LENGTH=5000

# Models
ENABLE_GPU=true
MODEL_DOWNLOAD_TIMEOUT=600

# Logging
LOG_LEVEL=INFO
ENABLE_FILE_LOGGING=true
MAX_LOG_SIZE_MB=10
LOG_BACKUP_COUNT=5
```

### Quality Presets

Customize in `config/settings.py`:

```python
QUALITY_PRESETS = {
    'fast': {
        'video_crf': 28,
        'audio_bitrate': 128
    },
    'balanced': {
        'video_crf': 23,
        'audio_bitrate': 192
    },
    'high': {
        'video_crf': 18,
        'audio_bitrate': 256
    }
}
```

---

## Troubleshooting

### Common Issues

#### Issue: "No face detected"

**Solutions:**
- Ensure face is clearly visible
- Try a different image
- Check image is not corrupted
- Verify minimum resolution (256x256)

#### Issue: "FFmpeg not found"

**Solutions:**
- Install FFmpeg
- Add FFmpeg to system PATH
- Restart application/terminal

#### Issue: "Model download failed"

**Solutions:**
- Check internet connection
- Use Tools → Download Models
- Manually download from GitHub
- Check firewall settings

#### Issue: "Out of memory"

**Solutions:**
- Close other applications
- Reduce resolution
- Use "Fast" quality preset
- Increase Docker memory limit

#### Issue: "Generation takes too long"

**Solutions:**
- Use "Fast" quality preset
- Reduce resolution to 480p
- Check system resources
- Enable GPU if available

### Error Messages

#### "Invalid image format"
- Supported formats: JPG, PNG, BMP, WEBP
- Convert image to supported format

#### "Text too long"
- Maximum: 5000 characters
- Split into multiple generations

#### "Database locked"
- Close other instances
- Restart application
- Check file permissions

---

## Advanced Usage

### Batch Processing

Process multiple images/texts programmatically:

```python
from core.pipeline import GenerationPipeline
from utils import DatabaseManager, ModelManager
from config import settings, paths

# Initialize
db = DatabaseManager()
model_manager = ModelManager(str(paths.models_dir))
pipeline = GenerationPipeline(settings.to_dict(), db, model_manager)

# Batch data
items = [
    {
        'image': 'avatar1.jpg',
        'text': 'Hello, I am Avatar 1',
        'voice': 'female'
    },
    {
        'image': 'avatar2.jpg',
        'text': 'Hello, I am Avatar 2',
        'voice': 'male'
    }
]

# Process each
for i, item in enumerate(items):
    project_id = db.create_project(f"Batch_{i}")
    
    result = pipeline.generate(
        project_id=project_id,
        input_image=item['image'],
        text=item['text'],
        output_path=f"output_{i}.mp4",
        voice=item['voice']
    )
    
    print(f"✓ Generated: {result['output_path']}")
```

### Custom Voice Configuration

Add custom TTS voices in `config/settings.py`:

```python
TTS_VOICES = {
    'default': 'en-US',
    'male': 'en-US-GuyNeural',
    'female': 'en-US-JennyNeural',
    'child': 'en-US-AriaNeural'
}
```

### GPU Acceleration

Enable GPU for faster processing:

```bash
# Check GPU availability
nvidia-smi

# Set in .env
ENABLE_GPU=true
CUDA_VISIBLE_DEVICES=0
```

### Model Management

Download specific models:

```python
from utils import ModelManager

manager = ModelManager('./models')

# Download specific model
manager.download_model('wav2lip_96')

# Check downloaded models
status = manager.list_models()
print(status)

# Get model info
info = manager.get_models_info()
```

---

## Tips & Best Practices

### For Best Results

1. **Image Quality**
   - Use high-resolution images (1024x1024+)
   - Ensure good lighting
   - Face should occupy 30-50% of frame
   - Neutral expression works best

2. **Script Writing**
   - Use natural language
   - Include proper punctuation
   - Break long texts into paragraphs
   - Test with short scripts first

3. **Settings Selection**
   - Start with "Balanced" quality
   - Use 720p for most cases
   - Adjust speed for clarity
   - Test different voices

4. **Performance**
   - Close unnecessary applications
   - Use Docker for isolation
   - Enable GPU if available
   - Process during off-peak hours

### Workflow Optimization

1. **Test Pipeline**
   - Start with low-quality test
   - Verify face detection works
   - Check audio quality
   - Then generate full quality

2. **Organize Projects**
   - Use descriptive project names
   - Keep original images
   - Back up generated videos
   - Clean cache regularly

3. **Resource Management**
   - Monitor disk space
   - Clean old projects
   - Archive completed work
   - Schedule maintenance

---

## Support & Resources

### Documentation
- [README.md](README.md) - Project overview
- [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) - Quick Docker setup
- [BUILD_STATUS.md](BUILD_STATUS.md) - Development progress

### Logs
- Console output for real-time info
- Log files in `./logs/` directory
- Docker logs: `docker-compose logs`

### Database
- SQLite browser for inspection
- Backup: `./scripts/docker_manage.sh backup`
- Restore: `./scripts/docker_manage.sh restore`

---

## Keyboard Shortcuts

### Main Window
- `Ctrl+O` - Open image
- `Ctrl+S` - Save project
- `Ctrl+G` - Generate video
- `Ctrl+Q` - Quit application

### Text Input
- `Ctrl+A` - Select all
- `Ctrl+C` - Copy
- `Ctrl+V` - Paste
- `Ctrl+Z` - Undo

---

## Frequently Asked Questions

**Q: How long does generation take?**  
A: 2-8 minutes depending on quality and system specs.

**Q: Can I use my own AI models?**  
A: Yes, place models in `./models/` and update configuration.

**Q: What languages are supported?**  
A: TTS supports multiple languages. Check available voices.

**Q: Can I run headless (no GUI)?**  
A: Yes, use `--mode cli` or write custom scripts.

**Q: How do I update the application?**  
A: Pull latest changes and rebuild Docker container.

---

**Enjoy creating amazing AI avatars! 🎬✨**
