"""
Simple Avatar Generation Example
Demonstrates basic usage of the generation pipeline
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

from core.pipeline import GenerationPipeline
from utils import DatabaseManager, ModelManager
from config import settings, paths


def main():
    """Generate a simple avatar video"""
    
    print("=" * 70)
    print("  Simple Avatar Generation Example")
    print("=" * 70)
    print()
    
    # Initialize components
    print("Initializing components...")
    db = DatabaseManager()
    model_manager = ModelManager(str(paths.models_dir))
    pipeline = GenerationPipeline(settings.to_dict(), db, model_manager)
    print("✓ Components initialized")
    print()
    
    # Create project
    project_id = db.create_project(
        name="Simple Example",
        description="Basic avatar generation example"
    )
    print(f"✓ Created project (ID: {project_id})")
    print()
    
    # Configuration
    input_image = "path/to/your/image.jpg"  # Replace with actual image
    script_text = "Hello! This is a test of the AI Avatar Studio."
    output_video = str(paths.output_dir / "example_avatar.mp4")
    
    print("Configuration:")
    print(f"  Input image: {input_image}")
    print(f"  Script: {script_text}")
    print(f"  Output: {output_video}")
    print()
    
    # Progress callback
    def show_progress(stage, progress, message):
        """Display progress"""
        print(f"[{stage}] {progress}% - {message}")
    
    # Generate avatar
    print("Starting generation...")
    print("=" * 70)
    
    result = pipeline.generate(
        project_id=project_id,
        input_image=input_image,
        text=script_text,
        output_path=output_video,
        voice='default',
        quality='balanced',
        resolution='720p',
        speed=1.0,
        progress_callback=show_progress
    )
    
    print("=" * 70)
    print()
    
    # Check result
    if result['success']:
        print("✓ Generation completed successfully!")
        print(f"  Video: {result['output_path']}")
        print(f"  Thumbnail: {result['thumbnail_path']}")
        print()
        
        # Get generation info
        generation = db.get_generation(result['generation_id'])
        print("Generation details:")
        print(f"  Status: {generation['status']}")
        print(f"  Created: {generation['created_at']}")
        print(f"  Completed: {generation['completed_at']}")
    else:
        print("✗ Generation failed!")
        print(f"  Error: {result['error']}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGeneration cancelled by user.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
