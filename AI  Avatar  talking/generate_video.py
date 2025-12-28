#!/usr/bin/env python3
"""
Command-line video generation script for AI Avatar Studio.

Quick generation without launching the GUI.

Usage:
    python generate_video.py --image photo.jpg --text "Hello world"
    python generate_video.py --image photo.jpg --audio speech.mp3
    python generate_video.py --config generation_config.json

Examples:
    # Basic generation
    python generate_video.py -i face.jpg -t "Welcome to my channel!"
    
    # With custom output
    python generate_video.py -i face.jpg -t "Hello" -o output.mp4
    
    # High quality 1080p
    python generate_video.py -i face.jpg -t "Hello" --quality high --resolution 1080p
    
    # Using audio file
    python generate_video.py -i face.jpg -a speech.mp3
    
    # Batch from JSON
    python generate_video.py --batch batch_config.json

Author: AI Avatar Studio
Date: 2025-12-22
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Optional, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.paths import PathManager
from core.pipeline import GenerationPipeline
from utils.database_manager import DatabaseManager


class CLIGenerator:
    """Command-line video generator."""
    
    def __init__(self):
        """Initialize CLI generator."""
        self.paths = PathManager()
        self.pipeline = GenerationPipeline()
        self.db = DatabaseManager()
    
    def generate_single(
        self,
        image_path: str,
        text: Optional[str] = None,
        audio_path: Optional[str] = None,
        output_path: Optional[str] = None,
        quality: str = "balanced",
        resolution: str = "720p",
        voice: str = "default",
        speed: float = 1.0,
        project_name: Optional[str] = None,
        verbose: bool = True
    ) -> Dict:
        """
        Generate a single video.
        
        Args:
            image_path: Path to input image
            text: Text to speak (or None if audio_path provided)
            audio_path: Path to audio file (or None if text provided)
            output_path: Output video path (auto-generated if None)
            quality: Quality preset (fast, balanced, high)
            resolution: Video resolution (480p, 720p, 1080p)
            voice: TTS voice
            speed: Speech speed
            project_name: Project name for database
            verbose: Print progress
        
        Returns:
            Generation result dictionary
        """
        # Validate inputs
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        if text is None and audio_path is None:
            raise ValueError("Either text or audio_path must be provided")
        
        if audio_path and not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio not found: {audio_path}")
        
        # Create project
        if project_name is None:
            project_name = f"CLI_{Path(image_path).stem}"
        
        project_id = self.db.create_project(project_name)
        
        # Generate output path if not provided
        if output_path is None:
            output_dir = self.paths.get_output_dir()
            output_path = output_dir / f"{project_name}.mp4"
        
        # Progress callback
        def progress_callback(stage: str, percentage: float, message: str):
            if verbose:
                print(f"[{stage}] {percentage:3.0f}% - {message}")
        
        if verbose:
            print(f"\n🎬 Generating Avatar Video")
            print(f"   Image: {image_path}")
            if text:
                print(f"   Text: {text[:50]}{'...' if len(text) > 50 else ''}")
            if audio_path:
                print(f"   Audio: {audio_path}")
            print(f"   Output: {output_path}")
            print(f"   Quality: {quality}, Resolution: {resolution}\n")
        
        try:
            # Generate
            result = self.pipeline.generate(
                image_path=image_path,
                text=text,
                audio_path=audio_path,
                output_path=str(output_path),
                quality=quality,
                resolution=resolution,
                voice=voice,
                speed=speed,
                project_id=project_id,
                progress_callback=progress_callback
            )
            
            if verbose:
                print(f"\n✅ Generation Complete!")
                print(f"   Video: {result['output_path']}")
                print(f"   Duration: {result.get('duration_seconds', 0):.1f}s")
                print(f"   Size: {result.get('file_size_mb', 0):.1f} MB")
                print(f"   Time: {result.get('processing_time_seconds', 0):.1f}s\n")
            
            return result
        
        except Exception as e:
            if verbose:
                print(f"\n❌ Generation Failed: {str(e)}\n")
            raise
    
    def generate_batch(
        self,
        batch_config: List[Dict],
        parallel: bool = False,
        verbose: bool = True
    ) -> List[Dict]:
        """
        Generate multiple videos from configuration.
        
        Args:
            batch_config: List of generation configs
            parallel: Use parallel processing
            verbose: Print progress
        
        Returns:
            List of generation results
        """
        results = []
        total = len(batch_config)
        
        if verbose:
            print(f"\n🎬 Batch Generation: {total} video(s)\n")
        
        for idx, config in enumerate(batch_config, 1):
            if verbose:
                print(f"[{idx}/{total}] Processing: {config.get('project_name', 'Untitled')}")
            
            try:
                result = self.generate_single(
                    image_path=config['image_path'],
                    text=config.get('text'),
                    audio_path=config.get('audio_path'),
                    output_path=config.get('output_path'),
                    quality=config.get('quality', 'balanced'),
                    resolution=config.get('resolution', '720p'),
                    voice=config.get('voice', 'default'),
                    speed=config.get('speed', 1.0),
                    project_name=config.get('project_name'),
                    verbose=False
                )
                results.append(result)
                
                if verbose:
                    print(f"   ✅ Success: {result['output_path']}\n")
            
            except Exception as e:
                if verbose:
                    print(f"   ❌ Failed: {str(e)}\n")
                results.append({"error": str(e)})
        
        # Summary
        if verbose:
            success_count = sum(1 for r in results if 'error' not in r)
            print(f"Batch Complete: {success_count}/{total} successful\n")
        
        return results
    
    def load_batch_config(self, config_path: str) -> List[Dict]:
        """
        Load batch configuration from JSON file.
        
        Args:
            config_path: Path to JSON config file
        
        Returns:
            List of generation configs
        """
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Support both list and dict format
        if isinstance(config, list):
            return config
        elif isinstance(config, dict) and 'batch' in config:
            return config['batch']
        else:
            raise ValueError("Invalid batch config format")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate talking avatar videos from command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic generation
  python generate_video.py -i photo.jpg -t "Hello world!"
  
  # With audio file
  python generate_video.py -i photo.jpg -a speech.mp3
  
  # High quality 1080p
  python generate_video.py -i photo.jpg -t "Welcome!" --quality high --resolution 1080p
  
  # Custom output location
  python generate_video.py -i photo.jpg -t "Hello" -o output/video.mp4
  
  # Batch processing
  python generate_video.py --batch batch_config.json
  
Batch Config Format (JSON):
  [
    {
      "image_path": "photo1.jpg",
      "text": "Hello from photo 1",
      "project_name": "Video 1",
      "quality": "high"
    },
    {
      "image_path": "photo2.jpg",
      "audio_path": "speech.mp3",
      "project_name": "Video 2"
    }
  ]
        """
    )
    
    # Input options
    parser.add_argument(
        "-i", "--image",
        type=str,
        help="Path to input image file"
    )
    
    parser.add_argument(
        "-t", "--text",
        type=str,
        help="Text to speak"
    )
    
    parser.add_argument(
        "-a", "--audio",
        type=str,
        help="Path to audio file (instead of text)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output video path (auto-generated if not specified)"
    )
    
    # Quality options
    parser.add_argument(
        "--quality",
        type=str,
        choices=["fast", "balanced", "high"],
        default="balanced",
        help="Quality preset (default: balanced)"
    )
    
    parser.add_argument(
        "--resolution",
        type=str,
        choices=["480p", "720p", "1080p", "4k"],
        default="720p",
        help="Video resolution (default: 720p)"
    )
    
    parser.add_argument(
        "--voice",
        type=str,
        default="default",
        help="TTS voice (default: default)"
    )
    
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speech speed multiplier (default: 1.0)"
    )
    
    # Project options
    parser.add_argument(
        "--name",
        type=str,
        help="Project name for database tracking"
    )
    
    # Batch options
    parser.add_argument(
        "--batch",
        type=str,
        help="Path to batch config JSON file"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Use parallel processing for batch"
    )
    
    # Output options
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    generator = CLIGenerator()
    
    try:
        # Batch mode
        if args.batch:
            batch_config = generator.load_batch_config(args.batch)
            results = generator.generate_batch(
                batch_config=batch_config,
                parallel=args.parallel,
                verbose=not args.quiet
            )
            
            if args.json:
                print(json.dumps(results, indent=2))
        
        # Single mode
        elif args.image:
            if not args.text and not args.audio:
                print("Error: Either --text or --audio is required")
                parser.print_help()
                sys.exit(1)
            
            result = generator.generate_single(
                image_path=args.image,
                text=args.text,
                audio_path=args.audio,
                output_path=args.output,
                quality=args.quality,
                resolution=args.resolution,
                voice=args.voice,
                speed=args.speed,
                project_name=args.name,
                verbose=not args.quiet
            )
            
            if args.json:
                print(json.dumps(result, indent=2))
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nGeneration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
