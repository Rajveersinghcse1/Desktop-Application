"""
Custom Processing Example
Demonstrates how to use individual processing modules
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

from core.face_detection import FaceDetectionManager
from core.tts import TTSManager
from core.video import VideoProcessor
from core.audio import AudioProcessor
from core.image import ImageProcessor
from config import paths


def example_face_detection():
    """Example: Detect faces in an image"""
    
    print("\n" + "=" * 70)
    print("  Example 1: Face Detection")
    print("=" * 70)
    
    import cv2
    
    # Load image
    image_path = "path/to/image.jpg"  # Replace with actual image
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"✗ Could not load image: {image_path}")
        return
    
    # Detect faces
    detector = FaceDetectionManager()
    faces = detector.detect_faces(image)
    
    print(f"✓ Detected {len(faces)} face(s)")
    
    for i, face in enumerate(faces, 1):
        print(f"\nFace {i}:")
        print(f"  Confidence: {face['confidence']:.2f}")
        print(f"  Bounding box: {face['bbox']}")  # (x, y, width, height)
        print(f"  Area: {face['area']} pixels")


def example_text_to_speech():
    """Example: Generate speech from text"""
    
    print("\n" + "=" * 70)
    print("  Example 2: Text-to-Speech")
    print("=" * 70)
    
    # Create TTS manager
    tts = TTSManager()
    
    # Get available voices
    voices = tts.get_voices()
    print(f"✓ Available voices: {len(voices)}")
    
    # Generate speech
    text = "Hello! This is a test of the text-to-speech system."
    output_path = str(paths.cache_dir / "tts_test.wav")
    
    print(f"\nGenerating speech...")
    print(f"  Text: {text}")
    print(f"  Output: {output_path}")
    
    success = tts.text_to_speech(
        text=text,
        output_path=output_path,
        voice='default',
        speed=1.0
    )
    
    if success:
        print(f"✓ Speech generated: {output_path}")
    else:
        print("✗ Speech generation failed")


def example_audio_processing():
    """Example: Process and enhance audio"""
    
    print("\n" + "=" * 70)
    print("  Example 3: Audio Processing")
    print("=" * 70)
    
    processor = AudioProcessor()
    
    # Load audio
    input_path = "path/to/audio.wav"  # Replace with actual audio
    output_path = str(paths.cache_dir / "processed_audio.wav")
    
    try:
        audio, sr = processor.load_audio(input_path)
        print(f"✓ Loaded audio: {len(audio)} samples, {sr} Hz")
        
        # Normalize
        audio = processor.normalize_audio(audio, target_db=-20.0)
        print("✓ Normalized audio")
        
        # Reduce noise
        audio = processor.reduce_noise(audio, sr)
        print("✓ Reduced noise")
        
        # Enhance
        audio = processor.enhance_audio(audio, sr)
        print("✓ Enhanced audio")
        
        # Save
        processor.save_audio(output_path, audio, sr)
        print(f"✓ Saved processed audio: {output_path}")
        
    except Exception as e:
        print(f"✗ Audio processing failed: {e}")


def example_video_processing():
    """Example: Process video files"""
    
    print("\n" + "=" * 70)
    print("  Example 4: Video Processing")
    print("=" * 70)
    
    processor = VideoProcessor()
    
    # Example: Combine video and audio
    video_path = "path/to/video.mp4"
    audio_path = "path/to/audio.wav"
    output_path = str(paths.output_dir / "combined.mp4")
    
    print("\nCombining video and audio...")
    success = processor.combine_video_audio(
        video_path=video_path,
        audio_path=audio_path,
        output_path=output_path
    )
    
    if success:
        print(f"✓ Combined video: {output_path}")
    else:
        print("✗ Video combination failed")
    
    # Example: Create thumbnail
    thumbnail_path = str(paths.output_dir / "thumbnail.jpg")
    
    print("\nCreating thumbnail...")
    success = processor.create_thumbnail(
        video_path=output_path,
        output_path=thumbnail_path,
        timestamp=0.5  # At 50% of video
    )
    
    if success:
        print(f"✓ Thumbnail created: {thumbnail_path}")
    else:
        print("✗ Thumbnail creation failed")
    
    # Get video info
    print("\nGetting video information...")
    try:
        info = processor.get_video_info(output_path)
        print(f"✓ Video info:")
        print(f"  Duration: {info['duration']:.2f}s")
        print(f"  Size: {info['width']}x{info['height']}")
        print(f"  FPS: {info['fps']}")
        print(f"  Codec: {info['codec']}")
    except Exception as e:
        print(f"✗ Could not get video info: {e}")


def example_image_processing():
    """Example: Process and enhance images"""
    
    print("\n" + "=" * 70)
    print("  Example 5: Image Processing")
    print("=" * 70)
    
    processor = ImageProcessor()
    
    # Load image
    input_path = "path/to/image.jpg"  # Replace with actual image
    
    try:
        image = processor.load_image(input_path)
        print(f"✓ Loaded image: {image.shape}")
        
        # Validate
        valid, message = processor.validate_image(input_path)
        print(f"✓ Validation: {message}")
        
        # Resize
        image = processor.resize_image(image, width=1024, height=1024)
        print(f"✓ Resized to 1024x1024")
        
        # Enhance
        image = processor.enhance_image(image)
        print("✓ Enhanced image")
        
        # Save
        output_path = str(paths.output_dir / "processed_image.jpg")
        processor.save_image(output_path, image, quality=95)
        print(f"✓ Saved processed image: {output_path}")
        
    except Exception as e:
        print(f"✗ Image processing failed: {e}")


def main():
    """Run all examples"""
    
    print("=" * 70)
    print("  Custom Processing Examples")
    print("=" * 70)
    print()
    print("These examples demonstrate how to use individual modules")
    print("for custom processing workflows.")
    print()
    
    # Run examples
    example_face_detection()
    example_text_to_speech()
    example_audio_processing()
    example_video_processing()
    example_image_processing()
    
    print("\n" + "=" * 70)
    print("  Examples Complete")
    print("=" * 70)
    print()
    print("See the source code for implementation details.")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExamples cancelled by user.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
