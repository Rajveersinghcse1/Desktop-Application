# 🔧 AI Avatar Studio - Developer API Reference

## Table of Contents
1. [Core Modules](#core-modules)
2. [Pipeline API](#pipeline-api)
3. [Database API](#database-api)
4. [Model Management](#model-management)
5. [Processing Modules](#processing-modules)
6. [Configuration](#configuration)
7. [Examples](#examples)

---

## Core Modules

### Generation Pipeline

The main orchestrator for avatar generation workflow.

```python
from core.pipeline import GenerationPipeline
from utils import DatabaseManager, ModelManager
from config import settings, paths

# Initialize components
db = DatabaseManager()
model_manager = ModelManager(str(paths.models_dir))
pipeline = GenerationPipeline(settings.to_dict(), db, model_manager)

# Generate avatar
result = pipeline.generate(
    project_id=1,
    input_image='path/to/image.jpg',
    text='Hello world!',
    output_path='output.mp4',
    voice='default',
    quality='balanced',
    resolution='720p',
    speed=1.0,
    progress_callback=lambda stage, progress, msg: print(f"{stage}: {progress}%")
)

# Check result
if result['success']:
    print(f"Video: {result['output_path']}")
    print(f"Thumbnail: {result['thumbnail_path']}")
else:
    print(f"Error: {result['error']}")
```

**Parameters:**
- `project_id` (int): Database project ID
- `input_image` (str): Path to input image file
- `text` (str): Text to synthesize (max 5000 chars)
- `output_path` (str): Where to save output video
- `voice` (str): TTS voice name ('default', 'male', 'female')
- `quality` (str): Quality preset ('fast', 'balanced', 'high')
- `resolution` (str): Output resolution ('480p', '720p', '1080p')
- `speed` (float): Speech speed multiplier (0.5-2.0)
- `progress_callback` (callable): Progress callback function

**Returns:**
```python
{
    'success': bool,
    'generation_id': int,
    'output_path': str,
    'thumbnail_path': str,
    'error': str  # Only if success=False
}
```

---

## Pipeline API

### Pipeline Stages

The pipeline executes 8 stages sequentially:

1. **Validation**: Validate inputs (image format, text length)
2. **Face Detection**: Detect face in input image
3. **Audio Generation**: Generate speech from text
4. **Audio Processing**: Enhance audio quality
5. **Lip Sync**: Apply Wav2Lip synchronization
6. **Video Encoding**: Encode final video
7. **Thumbnail Generation**: Create video thumbnail
8. **Finalization**: Update database, cleanup

### Custom Pipeline

```python
from core.pipeline import GenerationPipeline

class CustomPipeline(GenerationPipeline):
    """Custom pipeline with additional processing"""
    
    def _process_audio(self, audio_path: str) -> str:
        """Override audio processing"""
        audio, sr = self.audio_processor.load_audio(audio_path)
        
        # Custom processing
        audio = self.apply_reverb(audio)
        audio = self.normalize(audio)
        
        # Save
        output_path = 'processed.wav'
        self.audio_processor.save_audio(output_path, audio, sr)
        return output_path
```

---

## Database API

### DatabaseManager

Complete database operations wrapper.

```python
from utils import DatabaseManager

db = DatabaseManager()

# Projects
project_id = db.create_project(
    name="My Project",
    description="Test project",
    settings={'quality': 'high'}
)

projects = db.get_all_projects(status='active')
project = db.get_project(project_id)

db.update_project(
    project_id,
    status='completed',
    metadata={'notes': 'Finished'}
)

# Generations
generation_id = db.create_generation(
    project_id=project_id,
    status='processing',
    input_image='image.jpg',
    output_video='output.mp4',
    settings={'voice': 'female'}
)

db.update_generation(
    generation_id,
    status='completed',
    metadata={'duration': 123.5}
)

# Statistics
stats = db.get_statistics()
print(f"Total projects: {stats['total_projects']}")
print(f"Success rate: {stats['success_rate']}%")

# Cleanup
deleted = db.cleanup_old_data(older_than_days=30)
print(f"Deleted {deleted} old records")
```

### Database Schema

```sql
-- Projects table
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settings JSON,
    metadata JSON
);

-- Generations table
CREATE TABLE generations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    input_image TEXT,
    output_video TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    settings JSON,
    metadata JSON,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

---

## Model Management

### ModelManager

Download and manage AI models.

```python
from utils import ModelManager

manager = ModelManager('./models')

# Check model status
if not manager.is_model_downloaded('wav2lip_96'):
    # Download model
    success = manager.download_model(
        'wav2lip_96',
        progress_callback=lambda cur, total, pct: print(f"{pct:.1f}%")
    )

# Get model path
model_path = manager.get_model_path('wav2lip_96')

# List all models
status = manager.list_models()
for name, downloaded in status.items():
    print(f"{name}: {'✓' if downloaded else '✗'}")

# Get detailed info
info = manager.get_models_info()
for name, data in info.items():
    print(f"{name}:")
    print(f"  Description: {data['description']}")
    print(f"  Size: {data['size_mb']} MB")
    print(f"  Downloaded: {data['downloaded']}")
```

### Available Models

| Model | Size | Description |
|-------|------|-------------|
| `wav2lip_96` | 148 MB | Wav2Lip standard model |
| `wav2lip_gan` | 148 MB | Wav2Lip GAN (higher quality) |
| `face_detection` | 89 MB | S3FD face detection |

---

## Processing Modules

### Face Detection

```python
from core.face_detection import FaceDetectionManager

detector = FaceDetectionManager()

# Detect faces
import cv2
image = cv2.imread('image.jpg')
faces = detector.detect_faces(image)

for face in faces:
    print(f"Confidence: {face['confidence']}")
    print(f"Bbox: {face['bbox']}")  # (x, y, w, h)
    print(f"Area: {face['area']}")
    
    # Get face image
    face_img = face['image']
```

### Text-to-Speech

```python
from core.tts import TTSManager

tts = TTSManager()

# Get available voices
voices = tts.get_voices()

# Generate speech
success = tts.text_to_speech(
    text="Hello, how are you?",
    output_path="speech.wav",
    voice="default",
    speed=1.0,
    pitch=1.0
)
```

### Video Processing

```python
from core.video import VideoProcessor

processor = VideoProcessor()

# Combine video and audio
processor.combine_video_audio(
    video_path='video.mp4',
    audio_path='audio.wav',
    output_path='output.mp4',
    video_codec='libx264',
    audio_codec='aac'
)

# Extract audio
processor.extract_audio('video.mp4', 'audio.wav')

# Resize video
processor.resize_video(
    'input.mp4',
    'output.mp4',
    width=1280,
    height=720
)

# Create thumbnail
processor.create_thumbnail(
    'video.mp4',
    'thumb.jpg',
    timestamp=0.5  # At 50% duration
)

# Get video info
info = processor.get_video_info('video.mp4')
print(f"Duration: {info['duration']}s")
print(f"Size: {info['width']}x{info['height']}")
print(f"FPS: {info['fps']}")
```

### Audio Processing

```python
from core.audio import AudioProcessor

processor = AudioProcessor()

# Load audio
audio, sr = processor.load_audio('input.wav')

# Normalize
audio = processor.normalize_audio(audio, target_db=-20.0)

# Reduce noise
audio = processor.reduce_noise(audio, sr)

# Enhance
audio = processor.enhance_audio(audio, sr)

# Adjust speed
audio = processor.adjust_speed(audio, sr, speed=1.5)

# Save
processor.save_audio('output.wav', audio, sr)
```

### Image Processing

```python
from core.image import ImageProcessor

processor = ImageProcessor()

# Load image
image = processor.load_image('input.jpg')

# Resize
image = processor.resize_image(image, width=1024, height=1024)

# Crop face
image = processor.crop_face(image, bbox=(100, 100, 300, 300))

# Enhance
image = processor.enhance_image(image)

# Validate
valid, message = processor.validate_image('test.jpg')

# Save
processor.save_image('output.jpg', image, quality=95)
```

### Lip Sync

```python
from core.lip_sync import Wav2LipEngine

engine = Wav2LipEngine(model_path='models/wav2lip.pth', device='cpu')

# Initialize
engine.initialize()

# Generate lip-synced video
success = engine.generate(
    face_video_path='face.mp4',
    audio_path='speech.wav',
    output_path='synced.mp4',
    fps=25,
    quality='balanced',
    progress_callback=lambda pct: print(f"{pct:.1f}%")
)
```

---

## Configuration

### Settings

```python
from config import settings

# Access settings
print(settings.APP_VERSION)
print(settings.DATABASE_PATH)
print(settings.MODELS_DIR)

# Quality presets
preset = settings.QUALITY_PRESETS['balanced']
print(preset['video_crf'])
print(preset['audio_bitrate'])

# Resolution mapping
res = settings.RESOLUTION_MAP['720p']
print(res['width'])  # 1280
print(res['height'])  # 720

# Convert to dict
config = settings.to_dict()
```

### Paths

```python
from config import paths

# Directory paths
print(paths.project_root)
print(paths.data_dir)
print(paths.models_dir)
print(paths.output_dir)
print(paths.cache_dir)
print(paths.logs_dir)

# Ensure directories exist
paths.ensure_all_directories()

# Disk usage
usage = paths.get_disk_usage()
print(f"Free: {usage['free_gb']} GB")

# Cleanup
paths.cleanup_temp_files(older_than_hours=24)
```

### Constants

```python
from config.constants import (
    ProcessingStage,
    GenerationStatus,
    QualityPreset,
    VideoFormat,
    ErrorCode
)

# Use enums
stage = ProcessingStage.LIP_SYNC
status = GenerationStatus.COMPLETED
quality = QualityPreset.HIGH
```

---

## Examples

### Example 1: Simple Generation

```python
from core.pipeline import GenerationPipeline
from utils import DatabaseManager, ModelManager
from config import settings, paths

# Setup
db = DatabaseManager()
model_manager = ModelManager(str(paths.models_dir))
pipeline = GenerationPipeline(settings.to_dict(), db, model_manager)

# Create project
project_id = db.create_project("Test Avatar")

# Generate
result = pipeline.generate(
    project_id=project_id,
    input_image='avatar.jpg',
    text='Welcome to AI Avatar Studio!',
    output_path='welcome.mp4'
)

print(f"Success: {result['success']}")
print(f"Output: {result['output_path']}")
```

### Example 2: Batch Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

def generate_avatar(image, text, index):
    """Generate single avatar"""
    project_id = db.create_project(f"Batch_{index}")
    
    result = pipeline.generate(
        project_id=project_id,
        input_image=image,
        text=text,
        output_path=f'output_{index}.mp4'
    )
    
    return result

# Batch data
items = [
    ('image1.jpg', 'Hello from avatar 1'),
    ('image2.jpg', 'Hello from avatar 2'),
    ('image3.jpg', 'Hello from avatar 3'),
]

# Process in parallel
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(generate_avatar, img, txt, i)
        for i, (img, txt) in enumerate(items)
    ]
    
    results = [f.result() for f in futures]

# Check results
for i, result in enumerate(results):
    print(f"Avatar {i}: {'✓' if result['success'] else '✗'}")
```

### Example 3: Custom Processing

```python
from core.audio import AudioProcessor
import numpy as np

class CustomAudioProcessor(AudioProcessor):
    """Custom audio processor with reverb"""
    
    def add_reverb(self, audio, sr, room_size=0.5):
        """Add reverb effect"""
        # Implement reverb
        delay_samples = int(0.05 * sr)
        reverb = np.zeros_like(audio)
        
        for i in range(len(audio)):
            if i >= delay_samples:
                reverb[i] = audio[i] + 0.3 * audio[i - delay_samples]
            else:
                reverb[i] = audio[i]
        
        return reverb
    
    def enhance_audio(self, audio, sr):
        """Enhanced audio processing with reverb"""
        # Base enhancement
        audio = super().enhance_audio(audio, sr)
        
        # Add reverb
        audio = self.add_reverb(audio, sr)
        
        return audio

# Use custom processor
processor = CustomAudioProcessor()
audio, sr = processor.load_audio('input.wav')
audio = processor.enhance_audio(audio, sr)
processor.save_audio('enhanced.wav', audio, sr)
```

### Example 4: Progress Monitoring

```python
def progress_callback(stage, progress, message):
    """Monitor generation progress"""
    print(f"[{stage}] {progress}% - {message}")
    
    # Log to database
    db.log_processing_stage(
        generation_id=gen_id,
        stage=stage,
        status='in_progress',
        progress=progress,
        message=message
    )

# Generate with progress monitoring
result = pipeline.generate(
    project_id=project_id,
    input_image='image.jpg',
    text='Test',
    output_path='output.mp4',
    progress_callback=progress_callback
)
```

---

## Error Handling

### Exception Types

```python
from config.constants import ErrorCode

try:
    result = pipeline.generate(...)
    
except FileNotFoundError as e:
    print(f"File not found: {e}")
    
except ValueError as e:
    print(f"Invalid input: {e}")
    
except RuntimeError as e:
    print(f"Processing error: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Logging

```python
from utils import get_logger

logger = get_logger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

---

## Testing

### Unit Tests

```python
import unittest
from core.face_detection import FaceDetectionManager

class TestFaceDetection(unittest.TestCase):
    def setUp(self):
        self.detector = FaceDetectionManager()
    
    def test_detect_faces(self):
        import cv2
        image = cv2.imread('test_image.jpg')
        faces = self.detector.detect_faces(image)
        
        self.assertGreater(len(faces), 0)
        self.assertIn('confidence', faces[0])
        self.assertIn('bbox', faces[0])

if __name__ == '__main__':
    unittest.main()
```

---

## Best Practices

1. **Always use context managers** for database operations
2. **Validate inputs** before processing
3. **Handle errors gracefully** with try-except blocks
4. **Log important events** for debugging
5. **Clean up temporary files** after processing
6. **Use progress callbacks** for long operations
7. **Test with small inputs** before full processing

---

**For more examples, see the `examples/` directory in the repository.**
