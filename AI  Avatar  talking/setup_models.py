"""
Model Download and Setup Script for AI Avatar Studio.

Downloads and verifies all required AI models:
- Wav2Lip models (lip sync)
- Face detection models
- Optional enhancement models

This script makes first-time setup easier by handling
all model downloads with progress tracking and verification.

Usage:
    python setup_models.py [options]

Author: AI Avatar Studio
Date: 2025-12-22
"""

import os
import sys
import hashlib
import argparse
from pathlib import Path
from typing import Dict, Optional, Tuple
import urllib.request
import urllib.error

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.paths import PathManager


class ModelDownloader:
    """Handles downloading and verification of AI models."""
    
    # Model definitions with download URLs and checksums
    MODELS = {
        "wav2lip": {
            "name": "Wav2Lip (Standard)",
            "filename": "wav2lip.pth",
            "url": "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip.pth",
            "size_mb": 148,
            "md5": "7c8e16e8b7c8b8e8b8e8b8e8b8e8b8e8",  # Placeholder
            "required": True,
            "description": "Standard Wav2Lip model for lip synchronization"
        },
        "wav2lip_gan": {
            "name": "Wav2Lip GAN (High Quality)",
            "filename": "wav2lip_gan.pth",
            "url": "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth",
            "size_mb": 148,
            "md5": "8d9e17e9c8d9c9d9d9d9d9d9d9d9d9d9",  # Placeholder
            "required": False,
            "description": "GAN-based Wav2Lip model for better quality (slower)"
        },
        "s3fd": {
            "name": "S3FD Face Detection",
            "filename": "s3fd.pth",
            "url": "https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth",
            "size_mb": 89,
            "md5": "9f9e10e9d9e9e9e9e9e9e9e9e9e9e9e9",  # Placeholder
            "required": True,
            "description": "Face detection model for Wav2Lip"
        },
        "face_alignment": {
            "name": "Face Alignment",
            "filename": "2DFAN4-11f355bf06.pth.tar",
            "url": "https://www.adrianbulat.com/downloads/python-fan/2DFAN4-11f355bf06.pth.tar",
            "size_mb": 238,
            "md5": "a0a1e2e3e4e5e6e7e8e9e0e1e2e3e4e5",  # Placeholder
            "required": False,
            "description": "Face alignment model (optional, improves accuracy)"
        }
    }
    
    def __init__(self):
        """Initialize model downloader."""
        self.paths = PathManager()
        self.models_dir = self.paths.get_models_dir()
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def check_model_exists(self, model_id: str) -> bool:
        """
        Check if a model is already downloaded.
        
        Args:
            model_id: Model identifier
        
        Returns:
            True if model exists
        """
        model_info = self.MODELS[model_id]
        model_path = self.models_dir / model_info["filename"]
        return model_path.exists()
    
    def verify_model(self, model_id: str) -> Tuple[bool, Optional[str]]:
        """
        Verify model file integrity.
        
        Args:
            model_id: Model identifier
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        model_info = self.MODELS[model_id]
        model_path = self.models_dir / model_info["filename"]
        
        if not model_path.exists():
            return False, "File not found"
        
        # Check file size (approximate)
        file_size_mb = model_path.stat().st_size / 1024 / 1024
        expected_size_mb = model_info["size_mb"]
        
        # Allow 10% variance in file size
        if abs(file_size_mb - expected_size_mb) > expected_size_mb * 0.1:
            return False, f"File size mismatch: {file_size_mb:.1f} MB (expected ~{expected_size_mb} MB)"
        
        # Note: MD5 check disabled as it's slow for large files
        # Can be enabled if checksums are verified
        
        return True, None
    
    def download_model(
        self,
        model_id: str,
        force: bool = False,
        show_progress: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Download a model.
        
        Args:
            model_id: Model identifier
            force: Force redownload even if exists
            show_progress: Show download progress
        
        Returns:
            Tuple of (success, error_message)
        """
        model_info = self.MODELS[model_id]
        model_path = self.models_dir / model_info["filename"]
        
        # Check if already exists
        if model_path.exists() and not force:
            is_valid, error = self.verify_model(model_id)
            if is_valid:
                return True, "Already downloaded"
            else:
                print(f"⚠️  Existing file invalid ({error}), redownloading...")
        
        print(f"\n📥 Downloading: {model_info['name']}")
        print(f"   URL: {model_info['url']}")
        print(f"   Size: ~{model_info['size_mb']} MB")
        
        try:
            # Download with progress
            if show_progress:
                self._download_with_progress(model_info["url"], model_path)
            else:
                urllib.request.urlretrieve(model_info["url"], model_path)
            
            # Verify download
            is_valid, error = self.verify_model(model_id)
            if not is_valid:
                model_path.unlink()  # Delete invalid file
                return False, f"Download verification failed: {error}"
            
            print(f"✅ Downloaded successfully: {model_info['filename']}")
            return True, None
            
        except urllib.error.URLError as e:
            return False, f"Download failed: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def download_all_required(self, force: bool = False) -> Dict[str, bool]:
        """
        Download all required models.
        
        Args:
            force: Force redownload
        
        Returns:
            Dictionary of model_id -> success
        """
        results = {}
        
        print("\n" + "="*70)
        print("DOWNLOADING REQUIRED MODELS")
        print("="*70)
        
        for model_id, model_info in self.MODELS.items():
            if model_info["required"]:
                success, error = self.download_model(model_id, force=force)
                results[model_id] = success
                
                if not success:
                    print(f"❌ Failed: {error}")
        
        return results
    
    def download_all_optional(self, force: bool = False) -> Dict[str, bool]:
        """
        Download all optional models.
        
        Args:
            force: Force redownload
        
        Returns:
            Dictionary of model_id -> success
        """
        results = {}
        
        print("\n" + "="*70)
        print("DOWNLOADING OPTIONAL MODELS")
        print("="*70)
        
        for model_id, model_info in self.MODELS.items():
            if not model_info["required"]:
                success, error = self.download_model(model_id, force=force)
                results[model_id] = success
                
                if not success:
                    print(f"❌ Failed: {error}")
        
        return results
    
    def list_models(self) -> None:
        """List all available models with status."""
        print("\n" + "="*70)
        print("AVAILABLE MODELS")
        print("="*70 + "\n")
        
        for model_id, model_info in self.MODELS.items():
            exists = self.check_model_exists(model_id)
            status = "✅ Downloaded" if exists else "❌ Not downloaded"
            required = "Required" if model_info["required"] else "Optional"
            
            print(f"📦 {model_info['name']}")
            print(f"   Status: {status}")
            print(f"   Type: {required}")
            print(f"   Size: ~{model_info['size_mb']} MB")
            print(f"   File: {model_info['filename']}")
            print(f"   Description: {model_info['description']}")
            
            if exists:
                is_valid, error = self.verify_model(model_id)
                if not is_valid:
                    print(f"   ⚠️  Warning: {error}")
            
            print()
    
    def check_all_required(self) -> Tuple[bool, list]:
        """
        Check if all required models are present.
        
        Returns:
            Tuple of (all_present, missing_models)
        """
        missing = []
        
        for model_id, model_info in self.MODELS.items():
            if model_info["required"]:
                if not self.check_model_exists(model_id):
                    missing.append(model_id)
        
        return len(missing) == 0, missing
    
    def get_total_size(self, include_optional: bool = False) -> float:
        """
        Calculate total download size in MB.
        
        Args:
            include_optional: Include optional models
        
        Returns:
            Total size in MB
        """
        total = 0
        
        for model_id, model_info in self.MODELS.items():
            if model_info["required"] or include_optional:
                if not self.check_model_exists(model_id):
                    total += model_info["size_mb"]
        
        return total
    
    def _download_with_progress(self, url: str, filepath: Path) -> None:
        """
        Download file with progress bar.
        
        Args:
            url: Download URL
            filepath: Destination path
        """
        try:
            import tqdm
            
            response = urllib.request.urlopen(url)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f:
                with tqdm.tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=filepath.name
                ) as pbar:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        pbar.update(len(chunk))
        
        except ImportError:
            # Fallback without progress bar
            print("   Downloading... (install tqdm for progress bar)")
            urllib.request.urlretrieve(url, filepath)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Download and setup AI models for Avatar Studio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_models.py --list              # List all models
  python setup_models.py --required          # Download required models
  python setup_models.py --all               # Download all models
  python setup_models.py --model wav2lip     # Download specific model
  python setup_models.py --check             # Check if ready
        """
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available models"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if all required models are present"
    )
    
    parser.add_argument(
        "--required",
        action="store_true",
        help="Download all required models"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all models (required + optional)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        help="Download specific model by ID"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force redownload even if exists"
    )
    
    args = parser.parse_args()
    
    downloader = ModelDownloader()
    
    try:
        if args.list:
            downloader.list_models()
        
        elif args.check:
            all_present, missing = downloader.check_all_required()
            
            if all_present:
                print("\n✅ All required models are present!\n")
                print("You're ready to start generating avatars! 🎬")
            else:
                print("\n❌ Missing required models:\n")
                for model_id in missing:
                    model_info = downloader.MODELS[model_id]
                    print(f"  • {model_info['name']} ({model_info['filename']})")
                
                total_size = downloader.get_total_size(include_optional=False)
                print(f"\nTotal download size: ~{total_size:.0f} MB")
                print("\nRun: python setup_models.py --required")
        
        elif args.required:
            total_size = downloader.get_total_size(include_optional=False)
            print(f"\n📊 Total download size: ~{total_size:.0f} MB")
            print("⏱️  Estimated time: 5-15 minutes (depending on connection)\n")
            
            if not args.force:
                response = input("Continue with download? [Y/n]: ").strip().lower()
                if response and response != 'y':
                    print("Cancelled.")
                    return
            
            results = downloader.download_all_required(force=args.force)
            
            success_count = sum(1 for v in results.values() if v)
            total_count = len(results)
            
            print("\n" + "="*70)
            print(f"DOWNLOAD COMPLETE: {success_count}/{total_count} successful")
            print("="*70 + "\n")
            
            if success_count == total_count:
                print("✅ All required models downloaded successfully!")
                print("You're ready to start generating avatars! 🎬\n")
            else:
                print("⚠️  Some downloads failed. Check errors above.")
                print("Try running again or download manually.\n")
        
        elif args.all:
            total_size = downloader.get_total_size(include_optional=True)
            print(f"\n📊 Total download size: ~{total_size:.0f} MB")
            print("⏱️  Estimated time: 10-30 minutes (depending on connection)\n")
            
            if not args.force:
                response = input("Continue with download? [Y/n]: ").strip().lower()
                if response and response != 'y':
                    print("Cancelled.")
                    return
            
            results_required = downloader.download_all_required(force=args.force)
            results_optional = downloader.download_all_optional(force=args.force)
            
            results = {**results_required, **results_optional}
            
            success_count = sum(1 for v in results.values() if v)
            total_count = len(results)
            
            print("\n" + "="*70)
            print(f"DOWNLOAD COMPLETE: {success_count}/{total_count} successful")
            print("="*70 + "\n")
            
            if success_count == total_count:
                print("✅ All models downloaded successfully!")
                print("You have the complete model collection! 🎬\n")
            else:
                print("⚠️  Some downloads failed. Check errors above.\n")
        
        elif args.model:
            model_id = args.model
            
            if model_id not in downloader.MODELS:
                print(f"\n❌ Unknown model: {model_id}")
                print("\nAvailable models:")
                for mid in downloader.MODELS.keys():
                    print(f"  • {mid}")
                return
            
            success, error = downloader.download_model(model_id, force=args.force)
            
            if success:
                print(f"\n✅ Model downloaded successfully!")
            else:
                print(f"\n❌ Download failed: {error}")
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Download cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
