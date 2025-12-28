# FAQ & Troubleshooting Guide

## Frequently Asked Questions

### General Questions

**Q: What is AI Avatar Studio?**  
A: AI Avatar Studio is a comprehensive application for creating talking avatar videos from photos and text/audio. It uses advanced AI models for lip-sync, face detection, and speech synthesis.

**Q: What platforms are supported?**  
A: Windows, Linux, and macOS. Docker deployment is available for all platforms.

**Q: Do I need a GPU?**  
A: No, but GPU acceleration significantly improves performance. The application works on CPU but will be slower.

**Q: How long does it take to generate a video?**  
A: Depends on hardware and settings:
- With GPU (high-end): 2-5 minutes
- With GPU (mid-range): 5-10 minutes
- CPU only: 15-30 minutes

### Installation Issues

**Q: Installation fails with "Python version not supported"**  
A: AI Avatar Studio requires Python 3.8-3.11. Check your version:
```bash
python --version
```
Install a compatible version from [python.org](https://python.org).

**Q: pip install fails with dependency errors**  
A: Try upgrading pip first:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Q: FFmpeg not found**  
A: Install FFmpeg:
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html), add to PATH
- **Linux**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`

Verify installation:
```bash
ffmpeg -version
```

**Q: PyTorch installation fails**  
A: Install PyTorch separately based on your system:

CPU only:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

CUDA 11.8:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

CUDA 12.1:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Model Download Issues

**Q: Model download fails or is very slow**  
A: 
1. Check your internet connection
2. Try using a VPN if download is blocked
3. Manually download models:
   - Download from [project releases page]
   - Place in `./models/` directory
4. Use the model downloader with retry:
```bash
python setup_models.py --force
```

**Q: "Model verification failed" error**  
A: The downloaded model file is corrupted. Delete it and re-download:
```bash
rm models/wav2lip.pth
python setup_models.py
```

### Runtime Errors

**Q: "CUDA out of memory" error**  
A: Your GPU doesn't have enough memory. Solutions:
1. Lower resolution: Use 480p or 720p instead of 1080p
2. Use CPU mode: Set `USE_GPU=false` in `.env`
3. Close other GPU-using applications
4. Reduce batch size if doing batch processing

**Q: "Face not detected" error**  
A: 
1. Ensure the input image has a clear, frontal face
2. Good lighting in the photo
3. Face size should be at least 100x100 pixels
4. Only one face should be in the image
5. Try different face detection backends:
```python
from core.face_detection import FaceDetectionManager
detector = FaceDetectionManager(preferred_backend='opencv')
```

**Q: Generated video has no audio**  
A: Check:
1. Input audio file is valid (if using audio input)
2. TTS engine is working (run `python run_avatar_test.py`)
3. FFmpeg is correctly installed
4. Check logs in `./logs/` for errors

**Q: Lip sync is poor quality**  
A: 
1. Ensure high-quality input image (min 480p)
2. Use clear audio without background noise
3. Try "high" quality setting
4. Use GPU mode for better processing
5. Ensure face is clearly visible and well-lit

**Q: "Database locked" error**  
A: 
1. Close other instances of the application
2. If using Docker, restart container:
```bash
docker-compose restart
```
3. Delete lock file if exists:
```bash
rm data/database/projects.db-journal
```

### Docker Issues

**Q: Docker container won't start**  
A: Check:
```bash
# View logs
docker-compose logs

# Rebuild container
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Q: "Permission denied" errors in Docker**  
A: Fix volume permissions:
```bash
# Linux/Mac
sudo chown -R $USER:$USER docker_volumes/

# Windows (run as Administrator)
icacls docker_volumes /grant Everyone:F /t
```

**Q: Changes not persisting in Docker**  
A: Ensure volumes are correctly mounted:
```bash
docker-compose down
docker volume ls  # Check volumes exist
docker-compose up -d
```

### Performance Issues

**Q: Application is very slow**  
A: 
1. Enable GPU acceleration (if available)
2. Lower quality/resolution settings
3. Close background applications
4. Check disk space (need 10GB+ free)
5. Run performance benchmark:
```bash
python benchmark.py --full
```

**Q: High memory usage**  
A: 
1. Reduce resolution setting
2. Close other applications
3. Process videos one at a time
4. Restart application periodically
5. Clear temp files:
```bash
python maintenance.py cleanup --temp
```

**Q: Disk space filling up**  
A: Use cleanup manager:
```bash
# View disk usage
python maintenance.py status

# Clean old files (keeps last 30 days)
python cleanup_manager.py --clean --days 30

# Clean temp files only
python cleanup_manager.py --clean-temp
```

### GUI Issues

**Q: GUI doesn't start**  
A: 
1. Check if CustomTkinter is installed:
```bash
pip install customtkinter
```
2. Try Tkinter fallback (should be automatic)
3. Use CLI mode instead:
```bash
python generate_video.py -i photo.jpg -t "Hello world"
```

**Q: GUI is unresponsive during generation**  
A: This is normal - video generation takes time. Check:
1. Progress bar should be updating
2. Check logs: `tail -f logs/app.log`
3. Monitor from another terminal:
```bash
python monitor_generation.py --watch
```

### Audio Issues

**Q: TTS voice sounds robotic**  
A: Try different TTS engines:
1. pyttsx3 (fastest, basic quality)
2. gTTS (internet required, better quality)
3. Coqui TTS (best quality, slower)

Set in `.env`:
```
DEFAULT_TTS_ENGINE=gtts
```

**Q: "No audio devices found"**  
A: This is a pyttsx3 issue. Solutions:
1. Use gTTS or Coqui instead
2. Install audio drivers
3. Or provide pre-generated audio:
```bash
python generate_video.py -i photo.jpg -a speech.mp3
```

### Database Issues

**Q: "Projects not loading" or database errors**  
A: Reset database:
```bash
# Backup first
python maintenance.py backup

# Reinitialize
python health_check.py --fix
```

**Q: Lost project data**  
A: Restore from backup:
```bash
# List backups
python backup_manager.py --list

# Restore
python backup_manager.py --restore backups/backup_20250122.zip
```

### Common Error Messages

**"ModuleNotFoundError: No module named 'X'"**  
Install missing module:
```bash
pip install X
```
Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

**"RuntimeError: Attempting to deserialize object on a CUDA device"**  
Model was saved with GPU but you're loading on CPU. Solution:
```python
# In settings or code
USE_GPU = False
```

**"FileNotFoundError: models/wav2lip.pth"**  
Download models:
```bash
python setup_models.py
```

**"cv2.error: Face detection model not found"**  
Reinstall OpenCV and download cascade file:
```bash
pip install opencv-contrib-python
```

## Getting Help

If your issue isn't covered here:

1. **Check logs**: `./logs/app.log`
2. **Run health check**: `python health_check.py --detailed`
3. **Run diagnostics**: `python maintenance.py diagnose`
4. **Check documentation**: `USAGE_GUIDE.md`, `API_REFERENCE.md`
5. **Create an issue**: Include:
   - Error message
   - System info (OS, Python version)
   - Steps to reproduce
   - Relevant log entries

## Quick Fixes Checklist

```bash
# 1. Verify installation
python verify_setup.py

# 2. Check system health
python health_check.py --detailed

# 3. Download models if missing
python setup_models.py

# 4. Run component tests
python run_avatar_test.py

# 5. Check GPU setup
python setup_gpu.py

# 6. Clean up temp files
python maintenance.py cleanup --temp

# 7. Run benchmark
python benchmark.py
```

## Best Practices

1. **Regular maintenance**: Run cleanup weekly
2. **Backup projects**: Use backup manager before major operations
3. **Monitor disk space**: Keep 10GB+ free
4. **Update regularly**: Check for updates monthly
5. **Use appropriate quality**: Don't use 4K unless necessary
6. **GPU vs CPU**: Use GPU when available for 5-10x speedup

## Performance Tips

1. **Optimize images**: Resize to target resolution before processing
2. **Batch processing**: Process multiple videos together
3. **Caching**: Enable caching in settings
4. **Close other apps**: Free up system resources
5. **Use SSD**: Store output on SSD for faster I/O

## Security Notes

1. **Input validation**: Application validates all inputs
2. **No internet required**: Works offline (except gTTS)
3. **Local processing**: All data stays on your machine
4. **No telemetry**: No data collection
5. **Open source**: All code is auditable
