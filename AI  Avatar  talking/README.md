# 🎬 AI Avatar Studio

**Transform static images into lifelike talking avatars with perfect lip synchronization**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Free](https://img.shields.io/badge/price-FREE-green.svg)](https://github.com)

## ✨ Features

- 🎭 **Professional Avatar Generation** - Studio-quality talking avatars
- 🗣️ **Multiple TTS Voices** - Choose from various voice options
- 🎬 **Perfect Lip Sync** - AI-powered Wav2Lip technology
- 🎨 **Background Removal** - Optional green screen or blur
- 📝 **Subtitle Support** - Automatic caption overlay
- 🔄 **Batch Processing** - Generate multiple avatars at once
- 💾 **Project History** - Track all your generations
- 🔒 **100% Private** - All processing happens offline
- 💯 **Completely Free** - No subscriptions, no limits

## 🚀 Quick Start

### Easiest Way - Automated Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-avatar-studio.git
cd ai-avatar-studio

# Run the quick start wizard
python quick_start.py
```

The wizard will:
- ✅ Check system requirements
- ✅ Install dependencies
- ✅ Download AI models
- ✅ Setup configuration
- ✅ Launch the application

### Docker Setup (Recommended for Production)

**Windows:**
```cmd
git clone https://github.com/yourusername/ai-avatar-studio.git
cd ai-avatar-studio
scripts\docker_manage.bat setup
```

**Linux/Mac:**
```bash
git clone https://github.com/yourusername/ai-avatar-studio.git
cd ai-avatar-studio
chmod +x scripts/docker_manage.sh
./scripts/docker_manage.sh setup
```

Docker setup includes:
- ✅ Persistent storage for database and models
- ✅ Automatic dependency management
- ✅ Isolated environment
- ✅ Easy updates and rollbacks

## 📋 Requirements

### Docker Setup (Recommended)
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose
- 10GB free disk space
- 8GB RAM minimum (16GB recommended)

### Manual Setup
- Python 3.8-3.11
- FFmpeg
- 10GB free disk space
- 8GB RAM minimum
- Optional: NVIDIA GPU with CUDA support

## 🐳 Docker Database Architecture

The application uses **SQLite** stored in **Docker volumes** for data persistence:

```
docker_volumes/
├── data/
│   └── database/
│       └── projects.db    ← Your database (persists across restarts)
├── models/                 ← AI models (~3-5GB, downloaded once)
└── output/                 ← Generated videos
```

**Key Benefits:**
- ✅ Data survives container restarts
- ✅ Easy backup and restore
- ✅ No external database server needed
- ✅ Simple migration between systems

See [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) for details.

## 🎯 Usage

### Basic Workflow

1. **Upload Image** - Drag & drop or browse for your image
2. **Enter Text** - Type the script or upload audio file
3. **Configure Settings** - Choose voice, quality, resolution
4. **Preview** - Check face detection and hear audio preview
5. **Generate** - Click "Generate Avatar" and wait
6. **Download** - Save your video in multiple formats

### Setup Utilities

The project includes powerful setup and maintenance tools:

```bash
# Quick start wizard (recommended for first-time setup)
python quick_start.py

# Download AI models
python setup_models.py --required       # Required models only
python setup_models.py --all            # All models including optional
python setup_models.py --check          # Check what's installed

# GPU setup and diagnostics
python setup_gpu.py diagnose            # Check GPU availability
python setup_gpu.py install             # Install GPU-enabled PyTorch
python setup_gpu.py benchmark           # Test GPU performance

# System maintenance
python maintenance.py diagnose          # Check system health
python maintenance.py backup            # Create backup
python maintenance.py cleanup           # Clean old files
python maintenance.py optimize          # Optimize performance
python maintenance.py status            # Show system status

# Test installation
python run_avatar_test.py               # Test all components
python verify_setup.py                  # Verify complete setup
```

### Common Docker Commands

| Action | Windows | Linux/Mac |
|--------|---------|-----------|
| Start | `scripts\docker_manage.bat start` | `./scripts/docker_manage.sh start` |
| Stop | `scripts\docker_manage.bat stop` | `./scripts/docker_manage.sh stop` |
| Logs | `scripts\docker_manage.bat logs` | `./scripts/docker_manage.sh logs` |
| Status | `scripts\docker_manage.bat status` | `./scripts/docker_manage.sh status` |
| Backup | `scripts\docker_manage.bat backup` | `./scripts/docker_manage.sh backup` |

## 📊 Database Operations

### Backup Database

```cmd
# Windows
scripts\docker_manage.bat backup

# Creates: backups/projects_backup_20231222_143052.db
```

```bash
# Linux/Mac
./scripts/docker_manage.sh backup
```

### Restore Database

```cmd
# Windows
scripts\docker_manage.bat restore backups\projects_backup_YYYYMMDD_HHMMSS.db
```

```bash
# Linux/Mac
./scripts/docker_manage.sh restore backups/projects_backup_YYYYMMDD_HHMMSS.db
```

### View Statistics

```python
from utils.database import DatabaseManager

db = DatabaseManager()
stats = db.get_statistics()
print(stats)
# Output: {'total_projects': 5, 'total_generations': 12, 'success_rate': 91.67, ...}
```

## 🏗️ Architecture

### Technology Stack

| Component | Technology | License |
|-----------|-----------|---------|
| **Language** | Python 3.10 | PSF |
| **GUI** | CustomTkinter | MIT |
| **TTS** | Coqui TTS / pyttsx3 | MPL 2.0 |
| **Lip Sync** | Wav2Lip | Custom (Research) |
| **Face Detection** | MediaPipe / OpenCV | Apache 2.0 / BSD |
| **Video Processing** | FFmpeg / OpenCV | LGPL / BSD |
| **Audio Processing** | pydub / librosa | MIT |
| **Background Removal** | rembg | MIT |
| **Database** | SQLite | Public Domain |
| **Container** | Docker | Apache 2.0 |

### Project Structure

```
ai-avatar-studio/
├── core/                   # Core processing engines
│   ├── tts/               # Text-to-speech
│   ├── face_detection/    # Face detection
│   ├── lip_sync/          # Lip synchronization
│   ├── video/             # Video processing
│   ├── audio/             # Audio processing
│   └── pipeline/          # Processing orchestration
├── gui/                    # User interface
│   ├── windows/           # Application windows
│   ├── components/        # Reusable widgets
│   └── themes/            # UI themes
├── utils/                  # Utilities
│   ├── database.py        # Database manager
│   ├── model_manager.py   # Model downloader
│   └── system_checker.py  # Dependency validator
├── models/                 # AI models (downloaded)
├── data/                   # Application data
│   └── database/          # SQLite database
├── output/                 # Generated videos
└── docker_volumes/         # Docker persistent storage
```

## 🎨 Features in Detail

### Text-to-Speech

- **Multiple Engines**: Coqui TTS (high quality), pyttsx3 (offline), gTTS (internet)
- **Voice Options**: 5+ voices including male/female variants
- **Customization**: Adjust speed (0.5x - 2.0x) and pitch
- **Audio Upload**: Use your own audio file instead of TTS

### Lip Synchronization

- **Wav2Lip Engine**: State-of-the-art lip sync technology
- **Quality Presets**: Fast, Balanced, High Quality modes
- **Face Detection**: Pre-validation ensures face is detected
- **Frame-by-frame**: Accurate lip movements for every phoneme

### Video Processing

- **Multiple Resolutions**: 480p, 720p, 1080p
- **Multiple Formats**: MP4, AVI, WebM, GIF
- **Quality Control**: Low, Medium, High encoding options
- **Effects**: Background removal, blur, subtitles

### Batch Processing

- **Queue System**: Process multiple images/texts in sequence
- **Priority Support**: Set processing order
- **Progress Tracking**: Monitor all generations
- **Auto-retry**: Failed generations can be retried

### Project Management

- **History**: View all previous generations
- **Thumbnails**: Visual preview of outputs
- **Statistics**: Track success rates and processing times
- **Search**: Find projects by name or date

## 🔧 Configuration

### Getting Started
- [🚀 Quick Start Guide](quick_start.py) - Automated setup wizard
- [📦 Installation Guide](INSTALLATION.md) - Complete installation instructions
- [🐳 Docker Quick Start](DOCKER_QUICKSTART.md) - Docker setup guide

### User Guides
- [📖 Usage Guide](USAGE_GUIDE.md) - How to use the application
- [🔧 API Reference](API_REFERENCE.md) - Developer documentation
- [💡 Examples](examples/README.md) - Code examples and tutorials

### Maintenance & Operations
- [🛠️ Maintenance Guide](MAINTENANCE_GUIDE.md) - Backup, cleanup, and optimization
- [⚙️ Model Setup](setup_models.py) - Download and manage AI models
- [🎮 GPU Setup](setup_gpu.py) - GPU detection and configuration

### Troubleshooting
- [🐛 Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [✅ Verification](verify_setup.py) - Verify your installation
- [🧪 Testing](run_avatar_test.py) - Test all component
# Database
DATABASE_PATH=/app/data/database/projects.db

# Processing
USE_GPU=false
DEFAULT_RESOLUTION=1080p
DEFAULT_VIDEO_FORMAT=mp4

# TTS
DEFAULT_TTS_ENGINE=coqui
DEFAULT_TTS_VOICE=jenny

# Audio
ENABLE_AUDIO_ENHANCEMENT=true
ENABLE_NOISE_REDUCTION=true

# Video
ENABLE_BACKGROUND_REMOVAL=false
ENABLE_SUBTITLES=false
```

See [.env.example](.env.example) for all options.

## 📚 Documentation

- [📖 Docker Database Architecture](docs/DOCKER_DATABASE_ARCHITECTURE.md) - Complete guide to the database setup
- [🚀 Docker Quick Start](DOCKER_QUICKSTART.md) - Fast setup guide
- [🔧 User Guide](docs/USER_GUIDE.md) - Detailed usage instructions
- [👨‍💻 Developer Guide](docs/DEVELOPER_GUIDE.md) - For contributors
- [🐛 Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

### Third-Party Licenses

- **Wav2Lip**: Custom license for research/education. Verify for commercial use.
- **Coqui TTS**: MPL 2.0
- **FFmpeg**: LGPL/GPL
- All other dependencies: MIT/Apache 2.0/BSD

## ⚠️ Disclaimer

This tool is for **educational and personal use**. Please respect:
- Portrait rights and privacy
- Copyright laws
- Terms of service for any content you use

## 🙏 Acknowledgments

- [Wav2Lip](https://github.com/Rudrabha/Wav2Lip) - Lip synchronization technology
- [Coqui TTS](https://github.com/coqui-ai/TTS) - Text-to-speech engine
- [MediaPipe](https://github.com/google/mediapipe) - Face detection
- [FFmpeg](https://ffmpeg.org/) - Video processing

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-avatar-studio/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-avatar-studio/discussions)
- **Email**: support@example.com

## 🗺️ Roadmap

- [ ] Web interface
- [ ] Real-time preview
- [ ] Multiple language support
- [ ] Cloud deployment option
- [ ] API for programmatic access
- [ ] Mobile app

## 📈 Statistics

```python
# View your statistics
from utils.database import DatabaseManager

db = DatabaseManager()
stats = db.get_statistics()
print(f"Success Rate: {stats['success_rate']:.2f}%")
print(f"Total Generations: {stats['total_generations']}")
print(f"Avg Processing Time: {stats['average_processing_time_seconds']:.2f}s")
```

---

**Made with ❤️ for the AI community**

⭐ Star this repo if you find it helpful!
