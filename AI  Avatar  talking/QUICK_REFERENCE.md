# 📋 AI Avatar Studio - Quick Reference

**One-page cheat sheet for common operations**

---

## 🚀 First Time Setup

```bash
# Automated setup (easiest)
python quick_start.py

# Or manual steps:
pip install -r requirements.txt
python setup_models.py --required
python main.py
```

---

## 🎬 Generate Avatar

### GUI Method
1. Launch: `python main.py`
2. Select image
3. Enter text
4. Click "Generate"

### Code Method
```python
from core.pipeline import GenerationPipeline

pipeline = GenerationPipeline()
result = pipeline.generate(
    image_path="photo.jpg",
    text="Hello world!",
    output_path="output.mp4"
)
```

---

## 🛠️ Maintenance Commands

```bash
# System health check
python maintenance.py diagnose

# Create backup
python maintenance.py backup

# Clean old files (30+ days)
python maintenance.py cleanup --days 30

# Preview cleanup (safe)
python maintenance.py cleanup --dry-run

# Optimize performance
python maintenance.py optimize

# System status
python maintenance.py status
```

---

## 📦 Model Management

```bash
# Check installed models
python setup_models.py --check

# List all available models
python setup_models.py --list

# Download required models
python setup_models.py --required

# Download all models
python setup_models.py --all

# Download specific model
python setup_models.py --model wav2lip
```

---

## 🎮 GPU Setup

```bash
# Check GPU status
python setup_gpu.py diagnose

# Install GPU PyTorch
python setup_gpu.py install

# Test GPU performance
python setup_gpu.py benchmark
```

---

## 🐳 Docker Commands

**Windows:**
```cmd
scripts\docker_manage.bat [command]
```

**Linux/Mac:**
```bash
./scripts/docker_manage.sh [command]
```

**Commands:**
- `setup` - First-time setup
- `start` - Start application
- `stop` - Stop application
- `restart` - Restart application
- `logs` - View logs
- `status` - Check status
- `backup` - Create backup
- `restore <file>` - Restore backup
- `clean` - Remove containers

---

## 📊 Database Operations

### Python API
```python
from utils.database_manager import DatabaseManager

db = DatabaseManager()

# Create project
project_id = db.create_project("My Project")

# Get statistics
stats = db.get_statistics()
print(stats)

# List recent projects
projects = db.get_recent_projects(limit=10)

# Search projects
results = db.search_projects("keyword")

# Delete project
db.delete_project(project_id)
```

### CLI
```bash
# Backup database
python -c "from utils.backup_manager import BackupManager; BackupManager().create_backup()"

# Get stats
python -c "from utils import DatabaseManager; print(DatabaseManager().get_statistics())"
```

---

## 🧹 Cleanup Operations

```bash
# Analyze disk usage
python utils/cleanup_manager.py analyze

# Clean old videos (30+ days)
python utils/cleanup_manager.py videos --days 30

# Clean failed generations
python utils/cleanup_manager.py failed

# Clean temp files
python utils/cleanup_manager.py temp

# Clean cache
python utils/cleanup_manager.py cache

# Clean all (preview)
python utils/cleanup_manager.py all --dry-run

# Find large files (>100 MB)
python utils/cleanup_manager.py large --min-size 100
```

---

## 💾 Backup & Restore

```bash
# Create backup (database + config + videos)
python utils/backup_manager.py create

# Create backup with models
python utils/backup_manager.py create --models

# List backups
python utils/backup_manager.py list

# Restore backup
python utils/backup_manager.py restore backups/avatar_backup_20251222_143000.zip

# Delete old backups (keep 5)
python utils/backup_manager.py cleanup --keep 5
```

---

## ✅ Testing & Verification

```bash
# Quick component test
python run_avatar_test.py

# Full system verification
python verify_setup.py

# Test specific module
python -c "from core.tts import TTSManager; TTSManager().synthesize('test')"
```

---

## 🎯 Common Use Cases

### Batch Processing
```python
from examples.batch_processing import batch_generate

items = [
    {"image": "photo1.jpg", "text": "Hello"},
    {"image": "photo2.jpg", "text": "World"}
]

results = batch_generate(items, parallel=True)
```

### Custom Pipeline
```python
from core.face_detection import FaceDetectionManager
from core.tts import TTSManager
from core.lip_sync import Wav2LipEngine

# Detect face
face_mgr = FaceDetectionManager()
faces = face_mgr.detect("photo.jpg")

# Generate speech
tts = TTSManager()
audio = tts.synthesize("Hello world")

# Sync lips
wav2lip = Wav2LipEngine()
video = wav2lip.generate(image="photo.jpg", audio=audio)
```

### Progress Tracking
```python
def progress_callback(stage, percentage, message):
    print(f"{stage}: {percentage}% - {message}")

pipeline.generate(
    image_path="photo.jpg",
    text="Hello",
    progress_callback=progress_callback
)
```

---

## 📁 Directory Structure

```
AI Avatar Studio/
├── main.py                 # Launch application
├── quick_start.py          # Setup wizard
├── setup_models.py         # Model downloader
├── setup_gpu.py            # GPU helper
├── maintenance.py          # Maintenance tool
├── requirements.txt        # Dependencies
├── .env                    # Configuration
│
├── core/                   # Processing engines
├── gui/                    # User interface
├── utils/                  # Utilities
├── examples/               # Usage examples
├── docs/                   # Documentation
│
├── models/                 # AI models (~400 MB)
├── output/                 # Generated videos
├── logs/                   # Application logs
├── temp/                   # Temporary files
└── backups/                # Database backups
```

---

## ⚙️ Configuration (.env)

```bash
# Database
DATABASE_PATH=./data/database/projects.db

# GPU
USE_GPU=false
CUDA_VISIBLE_DEVICES=0

# Quality
DEFAULT_RESOLUTION=1080p
DEFAULT_QUALITY=high
DEFAULT_VIDEO_FORMAT=mp4

# TTS
DEFAULT_TTS_ENGINE=pyttsx3
DEFAULT_TTS_VOICE=default

# Processing
ENABLE_AUDIO_ENHANCEMENT=true
ENABLE_NOISE_REDUCTION=true
ENABLE_BACKGROUND_REMOVAL=false
```

---

## 🔧 Troubleshooting

### App won't start
```bash
python verify_setup.py
python maintenance.py diagnose
```

### Out of memory
```bash
# Use Fast quality
# Reduce resolution to 480p
# Close other apps
```

### Models not found
```bash
python setup_models.py --check
python setup_models.py --required
```

### FFmpeg error
```bash
# Windows: Add to PATH
# Linux: sudo apt install ffmpeg
# Mac: brew install ffmpeg
```

### Database error
```bash
# Backup and restore
python maintenance.py backup
python utils/backup_manager.py restore latest
```

---

## 📞 Quick Help

- **Logs:** `./logs/app.log`
- **Status:** `python maintenance.py status`
- **Test:** `python run_avatar_test.py`
- **Docs:** `README.md`, `USAGE_GUIDE.md`
- **Examples:** `examples/README.md`

---

## 🎓 Learning Resources

1. **Start Here:** [INSTALLATION.md](INSTALLATION.md)
2. **Basic Usage:** [USAGE_GUIDE.md](USAGE_GUIDE.md)
3. **Code Examples:** [examples/](examples/)
4. **API Docs:** [API_REFERENCE.md](API_REFERENCE.md)
5. **Maintenance:** [MAINTENANCE_GUIDE.md](MAINTENANCE_GUIDE.md)

---

## 💡 Pro Tips

- **Use --dry-run** before cleanup/delete operations
- **Create backups** before major changes
- **Run optimize** weekly for best performance
- **Check diagnose** monthly for system health
- **Use GPU** for 5-10x faster generation
- **Batch process** for efficiency
- **Monitor logs** to catch issues early

---

**Keep this file bookmarked for quick reference! 📌**
