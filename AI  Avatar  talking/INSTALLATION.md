# 🚀 Complete Installation & Setup Guide

This guide will walk you through setting up AI Avatar Studio from scratch.

---

## 📋 Prerequisites

Before starting, ensure you have:

- **Operating System:** Windows 10/11, Ubuntu 20.04+, or macOS 11+
- **Internet Connection:** Required for downloading dependencies and models
- **Disk Space:** At least 10 GB free
- **RAM:** Minimum 8 GB (16 GB recommended)

---

## 🎯 Installation Methods

Choose the method that best suits your needs:

### Method 1: Docker (Recommended - Easiest)

**Advantages:**
- ✅ Simplest setup
- ✅ Everything configured automatically
- ✅ Isolated environment
- ✅ Consistent across all platforms

**Requirements:**
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- 10 GB free disk space

**Steps:**

#### Windows
1. **Install Docker Desktop**
   - Download from: https://www.docker.com/products/docker-desktop
   - Install and restart computer
   - Start Docker Desktop

2. **Navigate to Project**
   ```cmd
   cd "c:\Users\YourUsername\Desktop\AI  Avatar  talking"
   ```

3. **Start Application**
   ```cmd
   docker-compose up
   ```

4. **Wait for Setup**
   - First run downloads images (~2 GB)
   - Takes 5-10 minutes
   - Subsequent runs start instantly

5. **Done!**
   - GUI opens automatically
   - Ready to create avatars

#### Linux/Mac
1. **Install Docker**
   ```bash
   # Linux
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Mac (using Homebrew)
   brew install --cask docker
   ```

2. **Navigate to Project**
   ```bash
   cd ~/Desktop/"AI  Avatar  talking"
   ```

3. **Start Application**
   ```bash
   docker-compose up
   ```

4. **Done!**
   - GUI opens automatically
   - Ready to create avatars

---

### Method 2: Local Installation (Advanced)

**Advantages:**
- ✅ Full control over environment
- ✅ Easier debugging
- ✅ Can customize Python packages
- ✅ Potentially faster (no Docker overhead)

**Requirements:**
- Python 3.8-3.11
- FFmpeg
- 10 GB free disk space

#### Step 1: Install Python

**Windows:**
1. Download Python from: https://www.python.org/downloads/
2. During installation:
   - ✅ Check "Add Python to PATH"
   - Click "Install Now"
3. Verify:
   ```cmd
   python --version
   ```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

**Mac:**
```bash
brew install python@3.10
```

#### Step 2: Install FFmpeg

**Windows:**
1. Download from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add to PATH:
   - Search "Environment Variables"
   - Edit "Path" variable
   - Add `C:\ffmpeg\bin`
4. Restart Command Prompt
5. Verify:
   ```cmd
   ffmpeg -version
   ```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
ffmpeg -version
```

**Mac:**
```bash
brew install ffmpeg
ffmpeg -version
```

#### Step 3: Setup Python Environment

1. **Navigate to Project**
   ```bash
   cd "AI  Avatar  talking"
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   This will install:
   - CustomTkinter (GUI)
   - PyTorch (AI models)
   - OpenCV (image processing)
   - librosa (audio processing)
   - And 30+ other packages

   ⏱️ Installation takes 10-20 minutes

#### Step 4: Configure Environment

1. **Copy Environment Template**
   ```bash
   # Windows
   copy .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```

2. **Edit Configuration** (Optional)
   ```bash
   # Open .env in text editor
   notepad .env  # Windows
   nano .env     # Linux
   open .env     # Mac
   ```

#### Step 5: Verify Installation

```bash
python verify_setup.py
```

This checks:
- ✓ Python version
- ✓ Directory structure
- ✓ Core files
- ✓ Dependencies
- ✓ FFmpeg
- ✓ Disk space

#### Step 6: Run Application

```bash
python main.py
```

---

## 📦 First-Time Setup

### Download AI Models

On first run, the application needs to download AI models (~400 MB).

**Option 1: Automatic (During First Use)**
- Start application
- Click "Generate"
- Models download automatically

**Option 2: Manual (Recommended)**
1. Start application
2. Go to: **Tools → Download Models**
3. Click **Yes** to download
4. Wait 5-10 minutes

Models downloaded:
- `wav2lip_96.pth` (148 MB) - Lip sync
- `wav2lip_gan.pth` (148 MB) - Higher quality
- `s3fd.pth` (89 MB) - Face detection

Models saved to:
- Docker: `./docker_volumes/models/`
- Local: `./models/`

---

## 🧪 Testing the Installation

### Quick Test

Run the test script:
```bash
python run_avatar_test.py
```

This tests:
- ✓ All imports
- ✓ Database operations
- ✓ Configuration
- ✓ System requirements
- ✓ Processors

### Full Test (Generate Avatar)

1. **Prepare Test Files**
   - Get a clear face photo (JPG/PNG)
   - Minimum 256x256 pixels
   - Face clearly visible

2. **Run Application**
   ```bash
   python main.py
   ```

3. **Generate Test Avatar**
   - Click "Select Image" → Choose your photo
   - Enter text: "Hello, this is a test."
   - Click "Generate Avatar Video"
   - Wait 2-5 minutes

4. **Check Results**
   - Video saved to `./output/`
   - Thumbnail also created

---

## 🔧 Troubleshooting

### Common Issues

#### Python Version Issues

**Problem:** "Python 3.12 not supported"

**Solution:**
- Install Python 3.10 or 3.11
- Use pyenv to manage versions:
  ```bash
  pyenv install 3.10.0
  pyenv local 3.10.0
  ```

#### FFmpeg Issues

**Problem:** "FFmpeg not found"

**Solution 1 - Add to PATH:**
```bash
# Windows (run as Administrator)
setx PATH "%PATH%;C:\ffmpeg\bin"

# Linux/Mac (add to ~/.bashrc or ~/.zshrc)
export PATH="/usr/local/bin:$PATH"
```

**Solution 2 - Reinstall:**
```bash
# Linux
sudo apt remove ffmpeg
sudo apt install ffmpeg

# Mac
brew reinstall ffmpeg
```

#### Package Installation Fails

**Problem:** pip install errors

**Solution 1 - Update pip:**
```bash
python -m pip install --upgrade pip setuptools wheel
```

**Solution 2 - Install with no cache:**
```bash
pip install -r requirements.txt --no-cache-dir
```

**Solution 3 - Install one by one:**
```bash
pip install numpy
pip install opencv-python
pip install torch torchvision
# ... continue with others
```

#### PyTorch Installation Issues

**Problem:** PyTorch won't install

**Solution - Install from official site:**
```bash
# CPU-only (smaller, faster download)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# GPU (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Docker Issues

**Problem:** "Docker daemon not running"

**Solution:**
1. Start Docker Desktop
2. Wait for it to fully start (whale icon in taskbar)
3. Try again

**Problem:** "Port already in use"

**Solution:**
```bash
# Stop existing containers
docker-compose down

# Or use different port
# Edit docker-compose.yml, change "8080:8080" to "8081:8080"
```

#### Permission Issues (Linux)

**Problem:** Permission denied errors

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh
```

#### Memory Issues

**Problem:** "Out of memory" during generation

**Solution:**
1. Close other applications
2. Use "Fast" quality preset
3. Reduce resolution to 480p
4. Increase Docker memory:
   - Docker Desktop → Settings → Resources
   - Increase memory to 8 GB+

---

## 🎓 Next Steps

### 1. Read Documentation

- [README.md](README.md) - Overview and features
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - How to use
- [API_REFERENCE.md](API_REFERENCE.md) - Developer docs

### 2. Try Examples

```bash
# Simple generation
python examples/simple_generation.py

# Batch processing
python examples/batch_processing.py

# Custom processing
python examples/custom_processing.py
```

### 3. Explore Features

- Different voices (male/female)
- Quality presets (fast/balanced/high)
- Resolution options (480p/720p/1080p)
- Speed adjustment (0.5x to 2.0x)

### 4. Check Statistics

- View generation history
- Track success rates
- Monitor processing times

---

## 📊 System Optimization

### For Best Performance

**Hardware:**
- GPU: NVIDIA GPU with CUDA support
- RAM: 16 GB or more
- SSD: For faster file I/O

**Settings:**
- Use "Fast" quality for testing
- Use "High" quality for final output
- Enable GPU acceleration in settings

**Docker Optimization:**
- Increase memory allocation
- Use volumes on SSD
- Enable BuildKit for faster builds

---

## 🔄 Updating

### Update Code

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Or rebuild Docker image
docker-compose build --no-cache
```

### Update Models

Delete old models and redownload:
```bash
# Delete models
rm -rf models/*  # Linux/Mac
del /Q models\*  # Windows

# Redownload
python main.py
# Tools → Download Models
```

---

## 🗑️ Uninstallation

### Docker

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove images
docker rmi ai-avatar-studio_app
```

### Local

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows

# Remove generated files
rm -rf output/ logs/ models/
```

---

## 📞 Support

- **Documentation:** See docs in project directory
- **Logs:** Check `./logs/` for errors
- **Issues:** Review error messages carefully
- **Testing:** Run `python verify_setup.py`

---

## ✅ Installation Checklist

Use this checklist to ensure everything is set up:

- [ ] Python 3.8-3.11 installed
- [ ] FFmpeg installed and in PATH
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Environment file configured (`.env`)
- [ ] Verification script passed (`python verify_setup.py`)
- [ ] Application starts (`python main.py`)
- [ ] Models downloaded (Tools → Download Models)
- [ ] Test generation successful

---

**Installation complete! Ready to create amazing avatars! 🎬✨**
