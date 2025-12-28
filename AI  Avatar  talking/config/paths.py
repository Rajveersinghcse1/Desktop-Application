"""
Path Management for AI Avatar Studio
"""

from pathlib import Path
import os


class PathManager:
    """Centralized path management"""
    
    def __init__(self, root_dir: str = None):
        """
        Initialize path manager
        
        Args:
            root_dir: Root directory of the project. If None, uses current directory
        """
        if root_dir is None:
            self.root = Path.cwd()
        else:
            self.root = Path(root_dir).resolve()
        
        # Check if running in Docker
        self.is_docker = self._check_docker()
        
        # Initialize paths
        self._init_paths()
    
    def _check_docker(self) -> bool:
        """Check if running inside Docker container"""
        return (
            os.path.exists('/.dockerenv') or
            os.getenv('DOCKER_CONTAINER', 'false') == 'true' or
            str(self.root).startswith('/app')
        )
    
    def _init_paths(self):
        """Initialize all paths"""
        # Core directories
        if self.is_docker:
            self.data_dir = Path('/app/data')
            self.models_dir = Path('/app/models')
            self.output_dir = Path('/app/output')
            self.cache_dir = Path('/app/data/cache')
            self.logs_dir = Path('/app/data/logs')
        else:
            self.data_dir = self.root / 'data'
            self.models_dir = self.root / 'models'
            self.output_dir = self.root / 'output'
            self.cache_dir = self.data_dir / 'cache'
            self.logs_dir = self.data_dir / 'logs'
        
        # Database
        self.database_dir = self.data_dir / 'database'
        self.database_file = self.database_dir / 'projects.db'
        
        # Models subdirectories
        self.models_tts_dir = self.models_dir / 'tts'
        self.models_wav2lip_dir = self.models_dir / 'wav2lip'
        self.models_face_detection_dir = self.models_dir / 'face_detection'
        self.models_background_dir = self.models_dir / 'background_removal'
        
        # Output subdirectories
        self.output_videos_dir = self.output_dir / 'videos'
        self.output_thumbnails_dir = self.output_dir / 'thumbnails'
        self.output_exports_dir = self.output_dir / 'exports'
        
        # Config
        self.config_dir = self.root / 'config'
        
        # Temp directories
        self.temp_dir = self.cache_dir / 'temp'
        self.temp_audio_dir = self.temp_dir / 'audio'
        self.temp_video_dir = self.temp_dir / 'video'
        self.temp_images_dir = self.temp_dir / 'images'
        
        # GUI assets
        self.gui_dir = self.root / 'gui'
        self.assets_dir = self.gui_dir / 'assets'
        self.icons_dir = self.assets_dir / 'icons'
        self.images_dir = self.assets_dir / 'images'
        self.fonts_dir = self.assets_dir / 'fonts'
        self.sounds_dir = self.assets_dir / 'sounds'
        
        # Backups
        self.backups_dir = self.root / 'backups'
    
    def ensure_all_directories(self):
        """Create all necessary directories"""
        directories = [
            self.data_dir,
            self.models_dir,
            self.output_dir,
            self.cache_dir,
            self.logs_dir,
            self.database_dir,
            self.models_tts_dir,
            self.models_wav2lip_dir,
            self.models_face_detection_dir,
            self.models_background_dir,
            self.output_videos_dir,
            self.output_thumbnails_dir,
            self.output_exports_dir,
            self.temp_dir,
            self.temp_audio_dir,
            self.temp_video_dir,
            self.temp_images_dir,
            self.backups_dir,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_video_path(self, filename: str) -> Path:
        """Get full path for video file"""
        return self.output_videos_dir / filename
    
    def get_thumbnail_path(self, filename: str) -> Path:
        """Get full path for thumbnail file"""
        return self.output_thumbnails_dir / filename
    
    def get_temp_audio_path(self, filename: str) -> Path:
        """Get temporary audio file path"""
        return self.temp_audio_dir / filename
    
    def get_temp_video_path(self, filename: str) -> Path:
        """Get temporary video file path"""
        return self.temp_video_dir / filename
    
    def get_temp_image_path(self, filename: str) -> Path:
        """Get temporary image file path"""
        return self.temp_images_dir / filename
    
    def get_log_path(self, filename: str) -> Path:
        """Get log file path"""
        return self.logs_dir / filename
    
    def get_model_path(self, model_type: str, filename: str) -> Path:
        """Get model file path"""
        model_dirs = {
            'tts': self.models_tts_dir,
            'wav2lip': self.models_wav2lip_dir,
            'face_detection': self.models_face_detection_dir,
            'background_removal': self.models_background_dir,
        }
        return model_dirs.get(model_type, self.models_dir) / filename
    
    def get_backup_path(self, filename: str) -> Path:
        """Get backup file path"""
        return self.backups_dir / filename
    
    def cleanup_temp_files(self, older_than_hours: int = 24):
        """Clean up old temporary files"""
        import time
        current_time = time.time()
        cutoff_time = current_time - (older_than_hours * 3600)
        
        temp_dirs = [self.temp_audio_dir, self.temp_video_dir, self.temp_images_dir]
        
        for temp_dir in temp_dirs:
            if not temp_dir.exists():
                continue
            
            for file in temp_dir.iterdir():
                if file.is_file():
                    file_time = file.stat().st_mtime
                    if file_time < cutoff_time:
                        try:
                            file.unlink()
                        except Exception:
                            pass  # Ignore errors
    
    def get_disk_usage(self) -> dict:
        """Get disk usage statistics"""
        import shutil
        
        stats = {}
        
        for name, directory in [
            ('models', self.models_dir),
            ('output', self.output_dir),
            ('cache', self.cache_dir),
            ('logs', self.logs_dir),
        ]:
            if directory.exists():
                total_size = sum(
                    f.stat().st_size
                    for f in directory.rglob('*')
                    if f.is_file()
                )
                stats[name] = total_size
            else:
                stats[name] = 0
        
        # Get free space
        try:
            disk_usage = shutil.disk_usage(str(self.root))
            stats['free_space'] = disk_usage.free
            stats['total_space'] = disk_usage.total
        except Exception:
            stats['free_space'] = 0
            stats['total_space'] = 0
        
        return stats
    
    def __str__(self) -> str:
        """String representation"""
        return f"PathManager(root={self.root}, docker={self.is_docker})"


# Global path manager instance
paths = PathManager()


if __name__ == '__main__':
    # Test path manager
    print("AI Avatar Studio - Path Manager")
    print("=" * 50)
    print(f"Root Directory: {paths.root}")
    print(f"Running in Docker: {paths.is_docker}")
    print(f"Database: {paths.database_file}")
    print(f"Models: {paths.models_dir}")
    print(f"Output: {paths.output_dir}")
    print(f"Cache: {paths.cache_dir}")
    print(f"Logs: {paths.logs_dir}")
    print("=" * 50)
    
    # Ensure directories exist
    paths.ensure_all_directories()
    print("✓ All directories created/verified")
    
    # Show disk usage
    usage = paths.get_disk_usage()
    print("\nDisk Usage:")
    for key, value in usage.items():
        if key in ['free_space', 'total_space']:
            print(f"  {key}: {value / (1024**3):.2f} GB")
        else:
            print(f"  {key}: {value / (1024**2):.2f} MB")
