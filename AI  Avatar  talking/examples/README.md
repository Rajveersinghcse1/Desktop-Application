# AI Avatar Studio - Examples

This directory contains example scripts demonstrating various ways to use the AI Avatar Studio.

## Examples

### 1. Simple Generation (`simple_generation.py`)

Basic example showing how to generate a single avatar video.

```bash
python examples/simple_generation.py
```

**What it demonstrates:**
- Initialize the generation pipeline
- Create a project
- Generate an avatar with custom settings
- Handle progress callbacks
- Check generation results

### 2. Batch Processing (`batch_processing.py`)

Generate multiple avatars from a list of images and texts.

```bash
python examples/batch_processing.py
```

**What it demonstrates:**
- Process multiple avatars sequentially
- Optional parallel processing
- Progress tracking for batches
- Summary statistics

**Use cases:**
- Bulk avatar creation
- Testing multiple configurations
- Creating avatar series

### 3. Custom Processing (`custom_processing.py`)

Use individual processing modules for custom workflows.

```bash
python examples/custom_processing.py
```

**What it demonstrates:**
- Face detection
- Text-to-speech generation
- Audio processing and enhancement
- Video manipulation
- Image processing

**Use cases:**
- Custom pipelines
- Testing individual modules
- Advanced processing workflows

## Quick Start

1. **Update paths in examples:**
   ```python
   input_image = "path/to/your/image.jpg"  # Replace this
   ```

2. **Run an example:**
   ```bash
   python examples/simple_generation.py
   ```

3. **Check output:**
   - Videos: `./output/`
   - Logs: `./logs/`

## Customization

### Change Quality Settings

```python
result = pipeline.generate(
    # ... other parameters
    quality='high',        # 'fast', 'balanced', or 'high'
    resolution='1080p',    # '480p', '720p', or '1080p'
    speed=1.2             # 0.5 to 2.0
)
```

### Change Voice

```python
result = pipeline.generate(
    # ... other parameters
    voice='female'  # 'default', 'male', or 'female'
)
```

### Add Progress Tracking

```python
def progress_callback(stage, progress, message):
    print(f"[{stage}] {progress}% - {message}")

result = pipeline.generate(
    # ... other parameters
    progress_callback=progress_callback
)
```

## API Usage

### Direct Module Usage

```python
# Face Detection
from core.face_detection import FaceDetectionManager
detector = FaceDetectionManager()
faces = detector.detect_faces(image)

# TTS
from core.tts import TTSManager
tts = TTSManager()
tts.text_to_speech(text, output_path, voice='default')

# Video Processing
from core.video import VideoProcessor
processor = VideoProcessor()
processor.combine_video_audio(video, audio, output)
```

## Common Issues

### "File not found"
- Update the image/audio paths in the example
- Use absolute paths or ensure files exist

### "Model not downloaded"
- Run: `python main.py` → Tools → Download Models
- Or download manually using ModelManager

### "FFmpeg not found"
- Install FFmpeg
- Add to system PATH
- Restart terminal

## Next Steps

1. **Modify examples** to use your own images and texts
2. **Create custom workflows** based on these examples
3. **Integrate** into your own applications
4. **Build advanced features** using the API

## Support

- See [API_REFERENCE.md](../API_REFERENCE.md) for detailed API docs
- See [USAGE_GUIDE.md](../USAGE_GUIDE.md) for comprehensive guide
- Check logs in `./logs/` for debugging

---

**Happy avatar creating! 🎬**
