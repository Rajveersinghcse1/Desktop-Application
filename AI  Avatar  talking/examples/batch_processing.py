"""
Batch Processing Example
Generate multiple avatars from a list of images and texts
"""

import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))

from core.pipeline import GenerationPipeline
from utils import DatabaseManager, ModelManager
from config import settings, paths


def generate_single_avatar(pipeline, db, index, image_path, text, voice='default'):
    """Generate a single avatar"""
    
    print(f"\n[Avatar {index}] Starting generation...")
    
    # Create project
    project_id = db.create_project(
        name=f"Batch Avatar {index}",
        description=f"Batch processing example {index}"
    )
    
    # Output path
    output_path = str(paths.output_dir / f"batch_avatar_{index}.mp4")
    
    # Generate
    result = pipeline.generate(
        project_id=project_id,
        input_image=image_path,
        text=text,
        output_path=output_path,
        voice=voice,
        quality='fast',  # Use fast for batch processing
        resolution='720p',
        speed=1.0
    )
    
    if result['success']:
        print(f"[Avatar {index}] ✓ Completed: {result['output_path']}")
        return True, result['output_path']
    else:
        print(f"[Avatar {index}] ✗ Failed: {result['error']}")
        return False, result['error']


def main():
    """Batch process multiple avatars"""
    
    print("=" * 70)
    print("  Batch Avatar Generation Example")
    print("=" * 70)
    print()
    
    # Initialize components
    print("Initializing components...")
    db = DatabaseManager()
    model_manager = ModelManager(str(paths.models_dir))
    pipeline = GenerationPipeline(settings.to_dict(), db, model_manager)
    print("✓ Components initialized")
    print()
    
    # Batch data
    # Replace with your actual images and texts
    batch_items = [
        {
            'image': 'path/to/image1.jpg',
            'text': 'Hello, I am Avatar 1.',
            'voice': 'default'
        },
        {
            'image': 'path/to/image2.jpg',
            'text': 'Hello, I am Avatar 2.',
            'voice': 'female'
        },
        {
            'image': 'path/to/image3.jpg',
            'text': 'Hello, I am Avatar 3.',
            'voice': 'male'
        }
    ]
    
    print(f"Processing {len(batch_items)} avatars...")
    print()
    
    # Option 1: Sequential processing (safer, uses less memory)
    print("Method: Sequential Processing")
    print("=" * 70)
    
    results = []
    for i, item in enumerate(batch_items, 1):
        success, output = generate_single_avatar(
            pipeline, db, i,
            item['image'],
            item['text'],
            item['voice']
        )
        results.append((i, success, output))
    
    # Option 2: Parallel processing (faster, but uses more memory)
    # Uncomment to use parallel processing
    """
    print("Method: Parallel Processing")
    print("=" * 70)
    
    results = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(
                generate_single_avatar,
                pipeline, db, i,
                item['image'],
                item['text'],
                item['voice']
            ): i
            for i, item in enumerate(batch_items, 1)
        }
        
        for future in as_completed(futures):
            i = futures[future]
            success, output = future.result()
            results.append((i, success, output))
    """
    
    # Summary
    print()
    print("=" * 70)
    print("  Batch Processing Summary")
    print("=" * 70)
    print()
    
    successful = sum(1 for _, success, _ in results if success)
    failed = len(results) - successful
    
    print(f"Total: {len(results)} avatars")
    print(f"✓ Successful: {successful}")
    print(f"✗ Failed: {failed}")
    print()
    
    if successful > 0:
        print("Generated videos:")
        for i, success, output in results:
            if success:
                print(f"  {i}. {output}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBatch processing cancelled by user.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
