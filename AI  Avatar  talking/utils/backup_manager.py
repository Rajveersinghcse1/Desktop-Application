"""
Backup and restore utility for AI Avatar Studio.

Manages backups of:
- Database
- Configuration files
- Generated projects
- Models (optional)

Author: AI Avatar Studio
Date: 2025-12-22
"""

import os
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

from config.paths import PathManager
from utils.database_manager import DatabaseManager


class BackupManager:
    """Manages backup and restore operations."""
    
    def __init__(self, backup_dir: Optional[str] = None):
        """
        Initialize backup manager.
        
        Args:
            backup_dir: Directory to store backups (default: ./backups)
        """
        self.paths = PathManager()
        self.db = DatabaseManager()
        self.logger = logging.getLogger(__name__)
        
        # Setup backup directory
        if backup_dir:
            self.backup_dir = Path(backup_dir)
        else:
            self.backup_dir = self.paths.get_base_dir() / "backups"
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(
        self,
        include_models: bool = False,
        include_output: bool = True,
        compression: str = "zip"
    ) -> Dict[str, any]:
        """
        Create a complete backup.
        
        Args:
            include_models: Include AI models in backup (large)
            include_output: Include generated videos
            compression: Compression format ("zip", "tar", "none")
        
        Returns:
            Dictionary with backup information
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"avatar_backup_{timestamp}"
        
        try:
            # Create temporary backup directory
            temp_dir = self.backup_dir / f"temp_{backup_name}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            backup_info = {
                "name": backup_name,
                "timestamp": timestamp,
                "datetime": datetime.now().isoformat(),
                "size_bytes": 0,
                "items": []
            }
            
            # 1. Backup database
            self.logger.info("Backing up database...")
            db_backup = self._backup_database(temp_dir)
            backup_info["items"].append(db_backup)
            backup_info["size_bytes"] += db_backup["size"]
            
            # 2. Backup configuration
            self.logger.info("Backing up configuration...")
            config_backup = self._backup_config(temp_dir)
            backup_info["items"].append(config_backup)
            backup_info["size_bytes"] += config_backup["size"]
            
            # 3. Backup output (if requested)
            if include_output:
                self.logger.info("Backing up generated videos...")
                output_backup = self._backup_output(temp_dir)
                if output_backup:
                    backup_info["items"].append(output_backup)
                    backup_info["size_bytes"] += output_backup["size"]
            
            # 4. Backup models (if requested)
            if include_models:
                self.logger.info("Backing up AI models...")
                models_backup = self._backup_models(temp_dir)
                if models_backup:
                    backup_info["items"].append(models_backup)
                    backup_info["size_bytes"] += models_backup["size"]
            
            # 5. Save backup metadata
            metadata_path = temp_dir / "backup_info.json"
            with open(metadata_path, "w") as f:
                json.dump(backup_info, f, indent=2)
            
            # 6. Compress backup
            if compression == "zip":
                backup_file = self._compress_zip(temp_dir, backup_name)
            elif compression == "tar":
                backup_file = self._compress_tar(temp_dir, backup_name)
            else:
                # No compression, just rename
                backup_file = self.backup_dir / backup_name
                temp_dir.rename(backup_file)
            
            # Clean up temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            
            backup_info["file"] = str(backup_file)
            backup_info["compressed"] = compression != "none"
            
            self.logger.info(f"Backup created: {backup_file}")
            self.logger.info(f"Total size: {backup_info['size_bytes'] / 1024 / 1024:.2f} MB")
            
            return backup_info
            
        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}")
            # Clean up on failure
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            raise
    
    def restore_backup(
        self,
        backup_path: str,
        restore_database: bool = True,
        restore_config: bool = True,
        restore_output: bool = True,
        restore_models: bool = False
    ) -> Dict[str, any]:
        """
        Restore from a backup.
        
        Args:
            backup_path: Path to backup file/directory
            restore_database: Restore database
            restore_config: Restore configuration
            restore_output: Restore generated videos
            restore_models: Restore AI models
        
        Returns:
            Dictionary with restore information
        """
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        try:
            # Extract if compressed
            if backup_path.is_file():
                self.logger.info("Extracting backup...")
                temp_dir = self.backup_dir / f"temp_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                temp_dir.mkdir(parents=True, exist_ok=True)
                
                if backup_path.suffix == ".zip":
                    with zipfile.ZipFile(backup_path, "r") as zf:
                        zf.extractall(temp_dir)
                else:
                    raise ValueError(f"Unsupported backup format: {backup_path.suffix}")
                
                restore_dir = temp_dir
            else:
                restore_dir = backup_path
            
            # Load backup metadata
            metadata_path = restore_dir / "backup_info.json"
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    backup_info = json.load(f)
            else:
                backup_info = {"items": []}
            
            restore_info = {
                "timestamp": datetime.now().isoformat(),
                "source": str(backup_path),
                "restored": []
            }
            
            # Restore database
            if restore_database:
                self.logger.info("Restoring database...")
                db_result = self._restore_database(restore_dir)
                restore_info["restored"].append(db_result)
            
            # Restore configuration
            if restore_config:
                self.logger.info("Restoring configuration...")
                config_result = self._restore_config(restore_dir)
                restore_info["restored"].append(config_result)
            
            # Restore output
            if restore_output:
                self.logger.info("Restoring generated videos...")
                output_result = self._restore_output(restore_dir)
                if output_result:
                    restore_info["restored"].append(output_result)
            
            # Restore models
            if restore_models:
                self.logger.info("Restoring AI models...")
                models_result = self._restore_models(restore_dir)
                if models_result:
                    restore_info["restored"].append(models_result)
            
            # Clean up temp directory
            if backup_path.is_file() and restore_dir.exists():
                shutil.rmtree(restore_dir)
            
            self.logger.info("Restore completed successfully")
            
            return restore_info
            
        except Exception as e:
            self.logger.error(f"Restore failed: {str(e)}")
            raise
    
    def list_backups(self) -> List[Dict[str, any]]:
        """
        List all available backups.
        
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        for item in self.backup_dir.iterdir():
            if item.is_file() and item.suffix == ".zip":
                # Compressed backup
                size = item.stat().st_size
                backups.append({
                    "name": item.stem,
                    "path": str(item),
                    "size_bytes": size,
                    "size_mb": size / 1024 / 1024,
                    "created": datetime.fromtimestamp(item.stat().st_ctime).isoformat(),
                    "compressed": True
                })
            elif item.is_dir() and item.name.startswith("avatar_backup_"):
                # Uncompressed backup
                size = self._get_dir_size(item)
                backups.append({
                    "name": item.name,
                    "path": str(item),
                    "size_bytes": size,
                    "size_mb": size / 1024 / 1024,
                    "created": datetime.fromtimestamp(item.stat().st_ctime).isoformat(),
                    "compressed": False
                })
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        return backups
    
    def delete_backup(self, backup_name: str) -> bool:
        """
        Delete a backup.
        
        Args:
            backup_name: Name of backup to delete
        
        Returns:
            True if deleted successfully
        """
        # Try as compressed file
        backup_path = self.backup_dir / f"{backup_name}.zip"
        if backup_path.exists():
            backup_path.unlink()
            self.logger.info(f"Deleted backup: {backup_name}.zip")
            return True
        
        # Try as directory
        backup_path = self.backup_dir / backup_name
        if backup_path.exists() and backup_path.is_dir():
            shutil.rmtree(backup_path)
            self.logger.info(f"Deleted backup: {backup_name}")
            return True
        
        return False
    
    def cleanup_old_backups(self, keep_count: int = 5) -> List[str]:
        """
        Delete old backups, keeping only the most recent ones.
        
        Args:
            keep_count: Number of backups to keep
        
        Returns:
            List of deleted backup names
        """
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return []
        
        deleted = []
        for backup in backups[keep_count:]:
            if self.delete_backup(backup["name"]):
                deleted.append(backup["name"])
        
        return deleted
    
    # Private helper methods
    
    def _backup_database(self, backup_dir: Path) -> Dict[str, any]:
        """Backup database file."""
        db_dir = backup_dir / "database"
        db_dir.mkdir(exist_ok=True)
        
        source = self.paths.get_database_path()
        dest = db_dir / "projects.db"
        
        shutil.copy2(source, dest)
        
        return {
            "type": "database",
            "files": ["projects.db"],
            "size": dest.stat().st_size
        }
    
    def _backup_config(self, backup_dir: Path) -> Dict[str, any]:
        """Backup configuration files."""
        config_dir = backup_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        files = []
        total_size = 0
        
        # Backup .env file
        env_file = self.paths.get_base_dir() / ".env"
        if env_file.exists():
            dest = config_dir / ".env"
            shutil.copy2(env_file, dest)
            files.append(".env")
            total_size += dest.stat().st_size
        
        return {
            "type": "config",
            "files": files,
            "size": total_size
        }
    
    def _backup_output(self, backup_dir: Path) -> Optional[Dict[str, any]]:
        """Backup generated videos."""
        output_src = self.paths.get_output_dir()
        
        if not output_src.exists() or not any(output_src.iterdir()):
            return None
        
        output_dir = backup_dir / "output"
        shutil.copytree(output_src, output_dir)
        
        size = self._get_dir_size(output_dir)
        file_count = sum(1 for _ in output_dir.rglob("*") if _.is_file())
        
        return {
            "type": "output",
            "files": f"{file_count} files",
            "size": size
        }
    
    def _backup_models(self, backup_dir: Path) -> Optional[Dict[str, any]]:
        """Backup AI models."""
        models_src = self.paths.get_models_dir()
        
        if not models_src.exists() or not any(models_src.iterdir()):
            return None
        
        models_dir = backup_dir / "models"
        shutil.copytree(models_src, models_dir)
        
        size = self._get_dir_size(models_dir)
        file_count = sum(1 for _ in models_dir.rglob("*.pth"))
        
        return {
            "type": "models",
            "files": f"{file_count} model files",
            "size": size
        }
    
    def _restore_database(self, restore_dir: Path) -> Dict[str, any]:
        """Restore database file."""
        source = restore_dir / "database" / "projects.db"
        dest = self.paths.get_database_path()
        
        # Backup current database
        if dest.exists():
            backup_dest = dest.parent / f"projects.db.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(dest, backup_dest)
        
        shutil.copy2(source, dest)
        
        return {
            "type": "database",
            "status": "restored",
            "files": ["projects.db"]
        }
    
    def _restore_config(self, restore_dir: Path) -> Dict[str, any]:
        """Restore configuration files."""
        config_dir = restore_dir / "config"
        files = []
        
        # Restore .env file
        env_source = config_dir / ".env"
        if env_source.exists():
            env_dest = self.paths.get_base_dir() / ".env"
            
            # Backup current .env
            if env_dest.exists():
                backup_dest = env_dest.parent / f".env.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(env_dest, backup_dest)
            
            shutil.copy2(env_source, env_dest)
            files.append(".env")
        
        return {
            "type": "config",
            "status": "restored",
            "files": files
        }
    
    def _restore_output(self, restore_dir: Path) -> Optional[Dict[str, any]]:
        """Restore generated videos."""
        output_source = restore_dir / "output"
        
        if not output_source.exists():
            return None
        
        output_dest = self.paths.get_output_dir()
        
        # Backup current output
        if output_dest.exists() and any(output_dest.iterdir()):
            backup_dest = output_dest.parent / f"output_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copytree(output_dest, backup_dest)
            shutil.rmtree(output_dest)
        
        shutil.copytree(output_source, output_dest)
        
        file_count = sum(1 for _ in output_dest.rglob("*") if _.is_file())
        
        return {
            "type": "output",
            "status": "restored",
            "files": f"{file_count} files"
        }
    
    def _restore_models(self, restore_dir: Path) -> Optional[Dict[str, any]]:
        """Restore AI models."""
        models_source = restore_dir / "models"
        
        if not models_source.exists():
            return None
        
        models_dest = self.paths.get_models_dir()
        
        # Backup current models
        if models_dest.exists() and any(models_dest.iterdir()):
            backup_dest = models_dest.parent / f"models_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copytree(models_dest, backup_dest)
            shutil.rmtree(models_dest)
        
        shutil.copytree(models_source, models_dest)
        
        file_count = sum(1 for _ in models_dest.rglob("*.pth"))
        
        return {
            "type": "models",
            "status": "restored",
            "files": f"{file_count} model files"
        }
    
    def _compress_zip(self, source_dir: Path, backup_name: str) -> Path:
        """Compress backup directory to ZIP."""
        zip_path = self.backup_dir / f"{backup_name}.zip"
        
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zf.write(file_path, arcname)
        
        return zip_path
    
    def _compress_tar(self, source_dir: Path, backup_name: str) -> Path:
        """Compress backup directory to TAR.GZ."""
        import tarfile
        
        tar_path = self.backup_dir / f"{backup_name}.tar.gz"
        
        with tarfile.open(tar_path, "w:gz") as tf:
            tf.add(source_dir, arcname=backup_name)
        
        return tar_path
    
    def _get_dir_size(self, directory: Path) -> int:
        """Calculate total size of directory."""
        total = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total += file_path.stat().st_size
        return total


def main():
    """Command-line interface for backup management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Avatar Studio Backup Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create backup
    create_parser = subparsers.add_parser("create", help="Create a new backup")
    create_parser.add_argument("--models", action="store_true", help="Include AI models")
    create_parser.add_argument("--no-output", action="store_true", help="Exclude generated videos")
    create_parser.add_argument("--compression", choices=["zip", "tar", "none"], default="zip")
    
    # Restore backup
    restore_parser = subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument("backup", help="Backup file/directory to restore")
    restore_parser.add_argument("--no-database", action="store_true", help="Don't restore database")
    restore_parser.add_argument("--no-config", action="store_true", help="Don't restore config")
    restore_parser.add_argument("--no-output", action="store_true", help="Don't restore videos")
    restore_parser.add_argument("--models", action="store_true", help="Restore AI models")
    
    # List backups
    list_parser = subparsers.add_parser("list", help="List available backups")
    
    # Delete backup
    delete_parser = subparsers.add_parser("delete", help="Delete a backup")
    delete_parser.add_argument("backup", help="Backup name to delete")
    
    # Cleanup old backups
    cleanup_parser = subparsers.add_parser("cleanup", help="Delete old backups")
    cleanup_parser.add_argument("--keep", type=int, default=5, help="Number of backups to keep")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    manager = BackupManager()
    
    if args.command == "create":
        print("\n🔄 Creating backup...\n")
        info = manager.create_backup(
            include_models=args.models,
            include_output=not args.no_output,
            compression=args.compression
        )
        print(f"\n✅ Backup created successfully!")
        print(f"📁 File: {info['file']}")
        print(f"📊 Size: {info['size_bytes'] / 1024 / 1024:.2f} MB")
        print(f"📦 Items: {len(info['items'])}")
        
    elif args.command == "restore":
        print(f"\n🔄 Restoring from: {args.backup}\n")
        info = manager.restore_backup(
            backup_path=args.backup,
            restore_database=not args.no_database,
            restore_config=not args.no_config,
            restore_output=not args.no_output,
            restore_models=args.models
        )
        print(f"\n✅ Restore completed successfully!")
        print(f"📦 Restored: {len(info['restored'])} items")
        
    elif args.command == "list":
        backups = manager.list_backups()
        if not backups:
            print("📭 No backups found")
        else:
            print(f"\n📦 Found {len(backups)} backup(s):\n")
            for backup in backups:
                print(f"  • {backup['name']}")
                print(f"    Size: {backup['size_mb']:.2f} MB")
                print(f"    Created: {backup['created']}")
                print(f"    Compressed: {'Yes' if backup['compressed'] else 'No'}")
                print()
        
    elif args.command == "delete":
        if manager.delete_backup(args.backup):
            print(f"✅ Deleted backup: {args.backup}")
        else:
            print(f"❌ Backup not found: {args.backup}")
        
    elif args.command == "cleanup":
        deleted = manager.cleanup_old_backups(keep_count=args.keep)
        if deleted:
            print(f"✅ Deleted {len(deleted)} old backup(s):")
            for name in deleted:
                print(f"  • {name}")
        else:
            print(f"📦 No backups to delete (keeping {args.keep} most recent)")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
