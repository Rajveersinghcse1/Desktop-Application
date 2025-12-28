"""
Model Manager
Download, verify, and manage AI models
"""

import logging
import hashlib
from pathlib import Path
from typing import Optional, Dict
import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


class ModelManager:
    """Manage AI model downloads and verification"""
    
    def __init__(self, models_dir: str):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Model registry
        self.models = {
            'wav2lip_96': {
                'url': 'https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip.pth',
                'filename': 'wav2lip.pth',
                'size_mb': 148,
                'checksum': None,  # Optional MD5 checksum
                'description': 'Wav2Lip model for lip synchronization'
            },
            'wav2lip_gan': {
                'url': 'https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth',
                'filename': 'wav2lip_gan.pth',
                'size_mb': 148,
                'checksum': None,
                'description': 'Wav2Lip GAN model (higher quality)'
            },
            'face_detection': {
                'url': 'https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth',
                'filename': 's3fd.pth',
                'size_mb': 89,
                'checksum': None,
                'description': 'S3FD face detection model'
            }
        }
    
    def is_model_downloaded(self, model_name: str) -> bool:
        """Check if model is already downloaded"""
        if model_name not in self.models:
            return False
        
        model_info = self.models[model_name]
        model_path = self.models_dir / model_info['filename']
        
        return model_path.exists()
    
    def get_model_path(self, model_name: str) -> Optional[Path]:
        """Get path to model file"""
        if model_name not in self.models:
            logger.error(f"Unknown model: {model_name}")
            return None
        
        model_info = self.models[model_name]
        model_path = self.models_dir / model_info['filename']
        
        if not model_path.exists():
            logger.warning(f"Model not downloaded: {model_name}")
            return None
        
        return model_path
    
    def download_model(
        self,
        model_name: str,
        force: bool = False,
        progress_callback=None
    ) -> bool:
        """
        Download AI model
        
        Args:
            model_name: Model identifier
            force: Force re-download even if exists
            progress_callback: Callback function(current, total, percentage)
        
        Returns:
            True if successful
        """
        if model_name not in self.models:
            logger.error(f"Unknown model: {model_name}")
            return False
        
        model_info = self.models[model_name]
        model_path = self.models_dir / model_info['filename']
        
        # Check if already downloaded
        if model_path.exists() and not force:
            logger.info(f"Model already downloaded: {model_name}")
            return True
        
        logger.info(f"Downloading {model_name}...")
        logger.info(f"  URL: {model_info['url']}")
        logger.info(f"  Size: ~{model_info['size_mb']} MB")
        
        try:
            # Download with progress
            response = requests.get(model_info['url'], stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            # Create progress bar
            if total_size > 0:
                pbar = tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    desc=model_info['filename']
                )
            else:
                pbar = None
            
            # Download in chunks
            downloaded = 0
            with open(model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if pbar:
                            pbar.update(len(chunk))
                        
                        if progress_callback and total_size > 0:
                            percentage = (downloaded / total_size) * 100
                            progress_callback(downloaded, total_size, percentage)
            
            if pbar:
                pbar.close()
            
            logger.info(f"✓ Downloaded: {model_name} ({downloaded / (1024**2):.1f} MB)")
            
            # Verify checksum if available
            if model_info.get('checksum'):
                if self.verify_checksum(model_path, model_info['checksum']):
                    logger.info("✓ Checksum verified")
                else:
                    logger.error("✗ Checksum verification failed")
                    model_path.unlink()
                    return False
            
            return True
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Download failed: {e}")
            if model_path.exists():
                model_path.unlink()
            return False
        
        except Exception as e:
            logger.error(f"Error downloading model: {e}")
            if model_path.exists():
                model_path.unlink()
            return False
    
    def verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify file MD5 checksum"""
        try:
            md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    md5.update(chunk)
            
            actual_checksum = md5.hexdigest()
            return actual_checksum == expected_checksum
        
        except Exception as e:
            logger.error(f"Checksum verification error: {e}")
            return False
    
    def download_all_models(self, progress_callback=None) -> bool:
        """Download all required models"""
        logger.info("Downloading all models...")
        
        all_success = True
        for model_name in self.models.keys():
            success = self.download_model(model_name, progress_callback=progress_callback)
            if not success:
                all_success = False
                logger.error(f"Failed to download: {model_name}")
        
        if all_success:
            logger.info("✓ All models downloaded successfully")
        else:
            logger.warning("⚠ Some models failed to download")
        
        return all_success
    
    def list_models(self) -> Dict[str, bool]:
        """List all models and their download status"""
        status = {}
        for model_name in self.models.keys():
            status[model_name] = self.is_model_downloaded(model_name)
        return status
    
    def get_models_info(self) -> Dict:
        """Get information about all models"""
        info = {}
        for model_name, model_data in self.models.items():
            info[model_name] = {
                'description': model_data['description'],
                'size_mb': model_data['size_mb'],
                'downloaded': self.is_model_downloaded(model_name),
                'path': str(self.get_model_path(model_name)) if self.is_model_downloaded(model_name) else None
            }
        return info
    
    def delete_model(self, model_name: str) -> bool:
        """Delete a downloaded model"""
        if model_name not in self.models:
            return False
        
        model_path = self.get_model_path(model_name)
        if model_path and model_path.exists():
            try:
                model_path.unlink()
                logger.info(f"Deleted model: {model_name}")
                return True
            except Exception as e:
                logger.error(f"Error deleting model: {e}")
                return False
        
        return False
    
    def get_total_size(self) -> float:
        """Get total size of downloaded models in MB"""
        total = 0
        for model_name in self.models.keys():
            model_path = self.get_model_path(model_name)
            if model_path and model_path.exists():
                total += model_path.stat().st_size
        
        return total / (1024 ** 2)


if __name__ == '__main__':
    # Test model manager
    from config import paths
    
    manager = ModelManager(str(paths.models_dir))
    
    print("AI Avatar Studio - Model Manager")
    print("=" * 60)
    
    # List models
    models_info = manager.get_models_info()
    for name, info in models_info.items():
        status = "✓ Downloaded" if info['downloaded'] else "✗ Not downloaded"
        print(f"\n{name}:")
        print(f"  {info['description']}")
        print(f"  Size: ~{info['size_mb']} MB")
        print(f"  Status: {status}")
        if info['path']:
            print(f"  Path: {info['path']}")
    
    total_size = manager.get_total_size()
    print(f"\nTotal downloaded: {total_size:.1f} MB")
