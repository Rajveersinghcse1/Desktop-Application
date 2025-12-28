"""
Cleanup and disk space management utility for AI Avatar Studio.

Helps manage disk space by:
- Removing old generated videos
- Cleaning temporary files
- Removing failed generations
- Clearing cache files
- Analyzing disk usage

Author: AI Avatar Studio
Date: 2025-12-22
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

from config.paths import PathManager
from utils.database_manager import DatabaseManager


class CleanupManager:
    """Manages cleanup operations and disk space."""
    
    def __init__(self):
        """Initialize cleanup manager."""
        self.paths = PathManager()
        self.db = DatabaseManager()
        self.logger = logging.getLogger(__name__)
    
    def analyze_disk_usage(self) -> Dict[str, any]:
        """
        Analyze disk space usage.
        
        Returns:
            Dictionary with disk usage information
        """
        analysis = {
            "total_size_bytes": 0,
            "total_size_mb": 0,
            "categories": {}
        }
        
        # Analyze output directory
        output_dir = self.paths.get_output_dir()
        if output_dir.exists():
            output_size = self._get_dir_size(output_dir)
            file_count = sum(1 for _ in output_dir.rglob("*") if _.is_file())
            video_count = sum(1 for _ in output_dir.rglob("*.mp4"))
            
            analysis["categories"]["output"] = {
                "path": str(output_dir),
                "size_bytes": output_size,
                "size_mb": output_size / 1024 / 1024,
                "file_count": file_count,
                "video_count": video_count
            }
            analysis["total_size_bytes"] += output_size
        
        # Analyze models directory
        models_dir = self.paths.get_models_dir()
        if models_dir.exists():
            models_size = self._get_dir_size(models_dir)
            model_count = sum(1 for _ in models_dir.rglob("*.pth"))
            
            analysis["categories"]["models"] = {
                "path": str(models_dir),
                "size_bytes": models_size,
                "size_mb": models_size / 1024 / 1024,
                "model_count": model_count
            }
            analysis["total_size_bytes"] += models_size
        
        # Analyze temp directory
        temp_dir = self.paths.get_temp_dir()
        if temp_dir.exists():
            temp_size = self._get_dir_size(temp_dir)
            file_count = sum(1 for _ in temp_dir.rglob("*") if _.is_file())
            
            analysis["categories"]["temp"] = {
                "path": str(temp_dir),
                "size_bytes": temp_size,
                "size_mb": temp_size / 1024 / 1024,
                "file_count": file_count
            }
            analysis["total_size_bytes"] += temp_size
        
        # Analyze cache directory
        cache_dir = self.paths.get_cache_dir()
        if cache_dir.exists():
            cache_size = self._get_dir_size(cache_dir)
            file_count = sum(1 for _ in cache_dir.rglob("*") if _.is_file())
            
            analysis["categories"]["cache"] = {
                "path": str(cache_dir),
                "size_bytes": cache_size,
                "size_mb": cache_size / 1024 / 1024,
                "file_count": file_count
            }
            analysis["total_size_bytes"] += cache_size
        
        # Analyze logs directory
        logs_dir = self.paths.get_logs_dir()
        if logs_dir.exists():
            logs_size = self._get_dir_size(logs_dir)
            file_count = sum(1 for _ in logs_dir.rglob("*.log"))
            
            analysis["categories"]["logs"] = {
                "path": str(logs_dir),
                "size_bytes": logs_size,
                "size_mb": logs_size / 1024 / 1024,
                "log_count": file_count
            }
            analysis["total_size_bytes"] += logs_size
        
        # Analyze database
        db_path = self.paths.get_database_path()
        if db_path.exists():
            db_size = db_path.stat().st_size
            
            analysis["categories"]["database"] = {
                "path": str(db_path),
                "size_bytes": db_size,
                "size_mb": db_size / 1024 / 1024
            }
            analysis["total_size_bytes"] += db_size
        
        analysis["total_size_mb"] = analysis["total_size_bytes"] / 1024 / 1024
        
        return analysis
    
    def cleanup_old_videos(
        self,
        days_old: int = 30,
        dry_run: bool = False
    ) -> Dict[str, any]:
        """
        Remove videos older than specified days.
        
        Args:
            days_old: Remove videos older than this many days
            dry_run: If True, only report what would be deleted
        
        Returns:
            Dictionary with cleanup results
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        output_dir = self.paths.get_output_dir()
        
        result = {
            "deleted_count": 0,
            "deleted_size_bytes": 0,
            "deleted_files": [],
            "dry_run": dry_run
        }
        
        if not output_dir.exists():
            return result
        
        for video_file in output_dir.rglob("*.mp4"):
            modified_time = datetime.fromtimestamp(video_file.stat().st_mtime)
            
            if modified_time < cutoff_date:
                file_size = video_file.stat().st_size
                
                if not dry_run:
                    # Also delete associated files (thumbnail, etc.)
                    base_name = video_file.stem
                    for related_file in video_file.parent.glob(f"{base_name}.*"):
                        related_file.unlink()
                    
                    self.logger.info(f"Deleted old video: {video_file.name}")
                
                result["deleted_count"] += 1
                result["deleted_size_bytes"] += file_size
                result["deleted_files"].append({
                    "name": video_file.name,
                    "size_bytes": file_size,
                    "modified": modified_time.isoformat()
                })
        
        result["deleted_size_mb"] = result["deleted_size_bytes"] / 1024 / 1024
        
        return result
    
    def cleanup_failed_generations(self, dry_run: bool = False) -> Dict[str, any]:
        """
        Remove files from failed generations.
        
        Args:
            dry_run: If True, only report what would be deleted
        
        Returns:
            Dictionary with cleanup results
        """
        result = {
            "deleted_count": 0,
            "deleted_size_bytes": 0,
            "deleted_projects": [],
            "dry_run": dry_run
        }
        
        # Get failed generations from database
        failed_projects = self.db.get_projects_by_status("failed")
        
        for project in failed_projects:
            project_id = project["id"]
            project_name = project["name"]
            
            # Find and delete project files
            output_dir = self.paths.get_output_dir() / str(project_id)
            
            if output_dir.exists():
                dir_size = self._get_dir_size(output_dir)
                
                if not dry_run:
                    shutil.rmtree(output_dir)
                    self.logger.info(f"Deleted failed project: {project_name}")
                
                result["deleted_count"] += 1
                result["deleted_size_bytes"] += dir_size
                result["deleted_projects"].append({
                    "id": project_id,
                    "name": project_name,
                    "size_bytes": dir_size
                })
        
        result["deleted_size_mb"] = result["deleted_size_bytes"] / 1024 / 1024
        
        return result
    
    def cleanup_temp_files(self, dry_run: bool = False) -> Dict[str, any]:
        """
        Remove temporary files.
        
        Args:
            dry_run: If True, only report what would be deleted
        
        Returns:
            Dictionary with cleanup results
        """
        temp_dir = self.paths.get_temp_dir()
        
        result = {
            "deleted_count": 0,
            "deleted_size_bytes": 0,
            "dry_run": dry_run
        }
        
        if not temp_dir.exists():
            return result
        
        for temp_file in temp_dir.rglob("*"):
            if temp_file.is_file():
                file_size = temp_file.stat().st_size
                
                if not dry_run:
                    temp_file.unlink()
                
                result["deleted_count"] += 1
                result["deleted_size_bytes"] += file_size
        
        result["deleted_size_mb"] = result["deleted_size_bytes"] / 1024 / 1024
        
        if not dry_run and result["deleted_count"] > 0:
            self.logger.info(f"Cleaned {result['deleted_count']} temp files")
        
        return result
    
    def cleanup_cache_files(self, dry_run: bool = False) -> Dict[str, any]:
        """
        Remove cache files.
        
        Args:
            dry_run: If True, only report what would be deleted
        
        Returns:
            Dictionary with cleanup results
        """
        cache_dir = self.paths.get_cache_dir()
        
        result = {
            "deleted_count": 0,
            "deleted_size_bytes": 0,
            "dry_run": dry_run
        }
        
        if not cache_dir.exists():
            return result
        
        for cache_file in cache_dir.rglob("*"):
            if cache_file.is_file():
                file_size = cache_file.stat().st_size
                
                if not dry_run:
                    cache_file.unlink()
                
                result["deleted_count"] += 1
                result["deleted_size_bytes"] += file_size
        
        result["deleted_size_mb"] = result["deleted_size_bytes"] / 1024 / 1024
        
        if not dry_run and result["deleted_count"] > 0:
            self.logger.info(f"Cleaned {result['deleted_count']} cache files")
        
        return result
    
    def cleanup_old_logs(
        self,
        days_old: int = 30,
        dry_run: bool = False
    ) -> Dict[str, any]:
        """
        Remove log files older than specified days.
        
        Args:
            days_old: Remove logs older than this many days
            dry_run: If True, only report what would be deleted
        
        Returns:
            Dictionary with cleanup results
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        logs_dir = self.paths.get_logs_dir()
        
        result = {
            "deleted_count": 0,
            "deleted_size_bytes": 0,
            "deleted_files": [],
            "dry_run": dry_run
        }
        
        if not logs_dir.exists():
            return result
        
        for log_file in logs_dir.rglob("*.log"):
            modified_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            if modified_time < cutoff_date:
                file_size = log_file.stat().st_size
                
                if not dry_run:
                    log_file.unlink()
                
                result["deleted_count"] += 1
                result["deleted_size_bytes"] += file_size
                result["deleted_files"].append(log_file.name)
        
        result["deleted_size_mb"] = result["deleted_size_bytes"] / 1024 / 1024
        
        if not dry_run and result["deleted_count"] > 0:
            self.logger.info(f"Cleaned {result['deleted_count']} old logs")
        
        return result
    
    def cleanup_all(
        self,
        days_old: int = 30,
        keep_models: bool = True,
        dry_run: bool = False
    ) -> Dict[str, any]:
        """
        Perform all cleanup operations.
        
        Args:
            days_old: Remove files older than this many days
            keep_models: Don't delete AI models
            dry_run: If True, only report what would be deleted
        
        Returns:
            Dictionary with cleanup results
        """
        self.logger.info("Starting comprehensive cleanup...")
        
        results = {
            "dry_run": dry_run,
            "operations": {}
        }
        
        # Cleanup old videos
        self.logger.info("Cleaning old videos...")
        results["operations"]["videos"] = self.cleanup_old_videos(
            days_old=days_old,
            dry_run=dry_run
        )
        
        # Cleanup failed generations
        self.logger.info("Cleaning failed generations...")
        results["operations"]["failed"] = self.cleanup_failed_generations(
            dry_run=dry_run
        )
        
        # Cleanup temp files
        self.logger.info("Cleaning temp files...")
        results["operations"]["temp"] = self.cleanup_temp_files(
            dry_run=dry_run
        )
        
        # Cleanup cache
        self.logger.info("Cleaning cache...")
        results["operations"]["cache"] = self.cleanup_cache_files(
            dry_run=dry_run
        )
        
        # Cleanup old logs
        self.logger.info("Cleaning old logs...")
        results["operations"]["logs"] = self.cleanup_old_logs(
            days_old=days_old,
            dry_run=dry_run
        )
        
        # Calculate totals
        total_freed = sum(
            op["deleted_size_bytes"]
            for op in results["operations"].values()
        )
        
        results["total_freed_bytes"] = total_freed
        results["total_freed_mb"] = total_freed / 1024 / 1024
        
        self.logger.info(f"Cleanup complete. Freed: {results['total_freed_mb']:.2f} MB")
        
        return results
    
    def find_large_files(
        self,
        min_size_mb: int = 100,
        exclude_models: bool = True
    ) -> List[Dict[str, any]]:
        """
        Find large files in the workspace.
        
        Args:
            min_size_mb: Minimum file size in MB
            exclude_models: Don't include model files
        
        Returns:
            List of large file information
        """
        min_size_bytes = min_size_mb * 1024 * 1024
        large_files = []
        
        base_dir = self.paths.get_base_dir()
        exclude_dirs = {"venv", "__pycache__", ".git"}
        
        if exclude_models:
            exclude_dirs.add("models")
        
        for file_path in base_dir.rglob("*"):
            if file_path.is_file():
                # Skip excluded directories
                if any(ex in file_path.parts for ex in exclude_dirs):
                    continue
                
                file_size = file_path.stat().st_size
                
                if file_size >= min_size_bytes:
                    large_files.append({
                        "path": str(file_path.relative_to(base_dir)),
                        "size_bytes": file_size,
                        "size_mb": file_size / 1024 / 1024,
                        "modified": datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        ).isoformat()
                    })
        
        # Sort by size (largest first)
        large_files.sort(key=lambda x: x["size_bytes"], reverse=True)
        
        return large_files
    
    # Private helper methods
    
    def _get_dir_size(self, directory: Path) -> int:
        """Calculate total size of directory."""
        total = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total += file_path.stat().st_size
        return total


def main():
    """Command-line interface for cleanup management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Avatar Studio Cleanup Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Analyze disk usage
    analyze_parser = subparsers.add_parser("analyze", help="Analyze disk usage")
    
    # Cleanup old videos
    videos_parser = subparsers.add_parser("videos", help="Clean old videos")
    videos_parser.add_argument("--days", type=int, default=30, help="Days to keep")
    videos_parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted")
    
    # Cleanup failed generations
    failed_parser = subparsers.add_parser("failed", help="Clean failed generations")
    failed_parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted")
    
    # Cleanup temp files
    temp_parser = subparsers.add_parser("temp", help="Clean temporary files")
    temp_parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted")
    
    # Cleanup cache
    cache_parser = subparsers.add_parser("cache", help="Clean cache files")
    cache_parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted")
    
    # Cleanup logs
    logs_parser = subparsers.add_parser("logs", help="Clean old logs")
    logs_parser.add_argument("--days", type=int, default=30, help="Days to keep")
    logs_parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted")
    
    # Cleanup all
    all_parser = subparsers.add_parser("all", help="Clean everything")
    all_parser.add_argument("--days", type=int, default=30, help="Days to keep")
    all_parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted")
    
    # Find large files
    large_parser = subparsers.add_parser("large", help="Find large files")
    large_parser.add_argument("--min-size", type=int, default=100, help="Minimum size in MB")
    large_parser.add_argument("--include-models", action="store_true", help="Include model files")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    manager = CleanupManager()
    
    if args.command == "analyze":
        print("\n📊 Analyzing disk usage...\n")
        analysis = manager.analyze_disk_usage()
        
        print(f"Total Size: {analysis['total_size_mb']:.2f} MB\n")
        print("Breakdown by category:\n")
        
        for category, data in analysis["categories"].items():
            print(f"  {category.upper()}:")
            print(f"    Path: {data['path']}")
            print(f"    Size: {data['size_mb']:.2f} MB")
            if "file_count" in data:
                print(f"    Files: {data['file_count']}")
            if "video_count" in data:
                print(f"    Videos: {data['video_count']}")
            if "model_count" in data:
                print(f"    Models: {data['model_count']}")
            print()
    
    elif args.command == "videos":
        result = manager.cleanup_old_videos(
            days_old=args.days,
            dry_run=args.dry_run
        )
        if args.dry_run:
            print(f"\n🔍 Would delete {result['deleted_count']} video(s)")
            print(f"   Would free: {result['deleted_size_mb']:.2f} MB")
        else:
            print(f"\n✅ Deleted {result['deleted_count']} video(s)")
            print(f"   Freed: {result['deleted_size_mb']:.2f} MB")
    
    elif args.command == "failed":
        result = manager.cleanup_failed_generations(dry_run=args.dry_run)
        if args.dry_run:
            print(f"\n🔍 Would delete {result['deleted_count']} failed project(s)")
            print(f"   Would free: {result['deleted_size_mb']:.2f} MB")
        else:
            print(f"\n✅ Deleted {result['deleted_count']} failed project(s)")
            print(f"   Freed: {result['deleted_size_mb']:.2f} MB")
    
    elif args.command in ["temp", "cache", "logs"]:
        if args.command == "temp":
            result = manager.cleanup_temp_files(dry_run=args.dry_run)
        elif args.command == "cache":
            result = manager.cleanup_cache_files(dry_run=args.dry_run)
        else:
            result = manager.cleanup_old_logs(
                days_old=args.days,
                dry_run=args.dry_run
            )
        
        if args.dry_run:
            print(f"\n🔍 Would delete {result['deleted_count']} file(s)")
            print(f"   Would free: {result['deleted_size_mb']:.2f} MB")
        else:
            print(f"\n✅ Deleted {result['deleted_count']} file(s)")
            print(f"   Freed: {result['deleted_size_mb']:.2f} MB")
    
    elif args.command == "all":
        result = manager.cleanup_all(
            days_old=args.days,
            dry_run=args.dry_run
        )
        
        print(f"\n{'🔍 CLEANUP PREVIEW' if args.dry_run else '✅ CLEANUP COMPLETE'}\n")
        
        for op_name, op_result in result["operations"].items():
            freed = op_result["deleted_size_mb"]
            count = op_result["deleted_count"]
            print(f"  {op_name.upper()}: {count} items, {freed:.2f} MB")
        
        print(f"\n  TOTAL: {result['total_freed_mb']:.2f} MB")
    
    elif args.command == "large":
        files = manager.find_large_files(
            min_size_mb=args.min_size,
            exclude_models=not args.include_models
        )
        
        if not files:
            print(f"\n📭 No files larger than {args.min_size} MB found")
        else:
            print(f"\n📦 Found {len(files)} large file(s):\n")
            for file_info in files:
                print(f"  • {file_info['path']}")
                print(f"    Size: {file_info['size_mb']:.2f} MB")
                print(f"    Modified: {file_info['modified']}")
                print()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
