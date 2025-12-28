"""
Comprehensive maintenance script for AI Avatar Studio.

This script provides a unified interface for:
- System diagnostics
- Backup and restore
- Cleanup and optimization
- Database maintenance
- Model management

Usage:
    python maintenance.py [command] [options]

Commands:
    diagnose    - Run complete system diagnostics
    backup      - Create backup
    restore     - Restore from backup
    cleanup     - Clean old files
    optimize    - Optimize performance
    status      - Show system status

Author: AI Avatar Studio
Date: 2025-12-22
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.paths import PathManager
from utils.database_manager import DatabaseManager
from utils.system_checker import SystemChecker
from utils.backup_manager import BackupManager
from utils.cleanup_manager import CleanupManager


class MaintenanceManager:
    """Unified maintenance interface."""
    
    def __init__(self):
        """Initialize maintenance manager."""
        self.paths = PathManager()
        self.db = DatabaseManager()
        self.system = SystemChecker()
        self.backup = BackupManager()
        self.cleanup = CleanupManager()
        self.logger = logging.getLogger(__name__)
    
    def diagnose(self) -> dict:
        """
        Run complete system diagnostics.
        
        Returns:
            Dictionary with diagnostic results
        """
        print("\n🔍 Running System Diagnostics...\n")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # 1. Check Python version
        print("Checking Python version...")
        python_ok = self.system.check_python_version()
        results["checks"]["python"] = {
            "status": "✅ OK" if python_ok else "❌ FAIL",
            "version": sys.version.split()[0]
        }
        
        # 2. Check FFmpeg
        print("Checking FFmpeg...")
        ffmpeg_ok = self.system.check_ffmpeg()
        results["checks"]["ffmpeg"] = {
            "status": "✅ OK" if ffmpeg_ok else "❌ FAIL"
        }
        
        # 3. Check disk space
        print("Checking disk space...")
        disk_info = self.system.check_disk_space()
        disk_ok = disk_info["available_gb"] >= 5
        results["checks"]["disk_space"] = {
            "status": "✅ OK" if disk_ok else "⚠️ LOW",
            "available_gb": disk_info["available_gb"],
            "total_gb": disk_info["total_gb"],
            "used_percent": disk_info["used_percent"]
        }
        
        # 4. Check RAM
        print("Checking RAM...")
        ram_info = self.system.check_ram()
        ram_ok = ram_info["available_gb"] >= 2
        results["checks"]["ram"] = {
            "status": "✅ OK" if ram_ok else "⚠️ LOW",
            "available_gb": ram_info["available_gb"],
            "total_gb": ram_info["total_gb"],
            "used_percent": ram_info["used_percent"]
        }
        
        # 5. Check database
        print("Checking database...")
        try:
            stats = self.db.get_statistics()
            db_ok = True
            results["checks"]["database"] = {
                "status": "✅ OK",
                "projects": stats.get("total_projects", 0),
                "generations": stats.get("total_generations", 0)
            }
        except Exception as e:
            db_ok = False
            results["checks"]["database"] = {
                "status": "❌ FAIL",
                "error": str(e)
            }
        
        # 6. Analyze disk usage
        print("Analyzing disk usage...")
        disk_analysis = self.cleanup.analyze_disk_usage()
        results["disk_usage"] = {
            "total_mb": disk_analysis["total_size_mb"],
            "categories": {
                k: v["size_mb"]
                for k, v in disk_analysis["categories"].items()
            }
        }
        
        # 7. Check for large files
        print("Checking for large files...")
        large_files = self.cleanup.find_large_files(min_size_mb=500)
        results["large_files"] = {
            "count": len(large_files),
            "total_mb": sum(f["size_mb"] for f in large_files)
        }
        
        # Print summary
        print("\n" + "="*60)
        print("DIAGNOSTIC SUMMARY")
        print("="*60 + "\n")
        
        all_ok = all(
            c["status"].startswith("✅")
            for c in results["checks"].values()
        )
        
        for check_name, check_data in results["checks"].items():
            print(f"{check_name.upper()}: {check_data['status']}")
        
        print("\n" + "="*60)
        print(f"Overall Status: {'✅ HEALTHY' if all_ok else '⚠️ NEEDS ATTENTION'}")
        print("="*60 + "\n")
        
        return results
    
    def backup_system(
        self,
        include_models: bool = False,
        include_output: bool = True
    ) -> dict:
        """
        Create system backup.
        
        Args:
            include_models: Include AI models
            include_output: Include generated videos
        
        Returns:
            Backup information
        """
        print("\n💾 Creating System Backup...\n")
        
        info = self.backup.create_backup(
            include_models=include_models,
            include_output=include_output,
            compression="zip"
        )
        
        print("\n✅ Backup Created Successfully!\n")
        print(f"File: {info['file']}")
        print(f"Size: {info['size_bytes'] / 1024 / 1024:.2f} MB")
        print(f"Items: {len(info['items'])}")
        
        return info
    
    def cleanup_system(
        self,
        days_old: int = 30,
        dry_run: bool = False
    ) -> dict:
        """
        Clean up old files.
        
        Args:
            days_old: Remove files older than this
            dry_run: Preview only
        
        Returns:
            Cleanup results
        """
        print(f"\n🧹 {'PREVIEWING' if dry_run else 'PERFORMING'} System Cleanup...\n")
        
        result = self.cleanup.cleanup_all(
            days_old=days_old,
            dry_run=dry_run
        )
        
        print("\n" + "="*60)
        print("CLEANUP SUMMARY")
        print("="*60 + "\n")
        
        for op_name, op_data in result["operations"].items():
            freed = op_data["deleted_size_mb"]
            count = op_data["deleted_count"]
            print(f"{op_name.upper()}: {count} items, {freed:.2f} MB")
        
        print(f"\nTOTAL: {result['total_freed_mb']:.2f} MB")
        print("="*60 + "\n")
        
        return result
    
    def optimize_system(self) -> dict:
        """
        Optimize system performance.
        
        Returns:
            Optimization results
        """
        print("\n⚡ Optimizing System...\n")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "operations": []
        }
        
        # 1. Cleanup temp files
        print("Cleaning temporary files...")
        temp_result = self.cleanup.cleanup_temp_files()
        results["operations"].append({
            "name": "temp_cleanup",
            "freed_mb": temp_result["deleted_size_mb"]
        })
        
        # 2. Cleanup cache
        print("Cleaning cache files...")
        cache_result = self.cleanup.cleanup_cache_files()
        results["operations"].append({
            "name": "cache_cleanup",
            "freed_mb": cache_result["deleted_size_mb"]
        })
        
        # 3. Optimize database (vacuum)
        print("Optimizing database...")
        try:
            db_path = self.paths.get_database_path()
            import sqlite3
            conn = sqlite3.connect(db_path)
            conn.execute("VACUUM")
            conn.close()
            results["operations"].append({
                "name": "database_vacuum",
                "status": "success"
            })
        except Exception as e:
            results["operations"].append({
                "name": "database_vacuum",
                "status": "failed",
                "error": str(e)
            })
        
        # 4. Cleanup old logs
        print("Cleaning old logs...")
        logs_result = self.cleanup.cleanup_old_logs(days_old=30)
        results["operations"].append({
            "name": "logs_cleanup",
            "freed_mb": logs_result["deleted_size_mb"]
        })
        
        total_freed = sum(
            op.get("freed_mb", 0)
            for op in results["operations"]
        )
        
        print(f"\n✅ Optimization Complete!")
        print(f"Total Space Freed: {total_freed:.2f} MB\n")
        
        return results
    
    def show_status(self) -> dict:
        """
        Show system status.
        
        Returns:
            Status information
        """
        print("\n📊 System Status\n")
        print("="*60 + "\n")
        
        # Database statistics
        try:
            stats = self.db.get_statistics()
            print("DATABASE:")
            print(f"  Projects: {stats.get('total_projects', 0)}")
            print(f"  Generations: {stats.get('total_generations', 0)}")
            print(f"  Success Rate: {stats.get('success_rate', 0):.1f}%")
            print()
        except Exception as e:
            print(f"DATABASE: ❌ Error - {str(e)}\n")
        
        # Disk usage
        disk_analysis = self.cleanup.analyze_disk_usage()
        print("DISK USAGE:")
        print(f"  Total: {disk_analysis['total_size_mb']:.2f} MB")
        for category, data in disk_analysis["categories"].items():
            print(f"  {category.capitalize()}: {data['size_mb']:.2f} MB")
        print()
        
        # System resources
        disk_info = self.system.check_disk_space()
        ram_info = self.system.check_ram()
        print("RESOURCES:")
        print(f"  Disk Available: {disk_info['available_gb']:.1f} GB")
        print(f"  RAM Available: {ram_info['available_gb']:.1f} GB")
        print()
        
        # Backups
        backups = self.backup.list_backups()
        print("BACKUPS:")
        if backups:
            latest = backups[0]
            print(f"  Latest: {latest['name']}")
            print(f"  Size: {latest['size_mb']:.2f} MB")
            print(f"  Created: {latest['created']}")
        else:
            print("  No backups found")
        print()
        
        print("="*60 + "\n")
        
        return {
            "database": stats if "stats" in locals() else None,
            "disk_usage": disk_analysis,
            "resources": {
                "disk": disk_info,
                "ram": ram_info
            },
            "backups": len(backups)
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Avatar Studio Maintenance Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python maintenance.py diagnose          # Run diagnostics
  python maintenance.py backup            # Create backup
  python maintenance.py cleanup --days 30 # Clean files older than 30 days
  python maintenance.py optimize          # Optimize system
  python maintenance.py status            # Show system status
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Diagnose command
    diagnose_parser = subparsers.add_parser(
        "diagnose",
        help="Run complete system diagnostics"
    )
    
    # Backup command
    backup_parser = subparsers.add_parser(
        "backup",
        help="Create system backup"
    )
    backup_parser.add_argument(
        "--models",
        action="store_true",
        help="Include AI models (large)"
    )
    backup_parser.add_argument(
        "--no-output",
        action="store_true",
        help="Exclude generated videos"
    )
    
    # Restore command
    restore_parser = subparsers.add_parser(
        "restore",
        help="Restore from backup"
    )
    restore_parser.add_argument(
        "backup",
        help="Backup file to restore"
    )
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser(
        "cleanup",
        help="Clean up old files"
    )
    cleanup_parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Remove files older than this many days"
    )
    cleanup_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview only, don't delete"
    )
    
    # Optimize command
    optimize_parser = subparsers.add_parser(
        "optimize",
        help="Optimize system performance"
    )
    
    # Status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show system status"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    # Create manager
    manager = MaintenanceManager()
    
    try:
        if args.command == "diagnose":
            manager.diagnose()
        
        elif args.command == "backup":
            manager.backup_system(
                include_models=args.models,
                include_output=not args.no_output
            )
        
        elif args.command == "restore":
            print(f"\n🔄 Restoring from: {args.backup}\n")
            manager.backup.restore_backup(args.backup)
            print("\n✅ Restore completed!\n")
        
        elif args.command == "cleanup":
            manager.cleanup_system(
                days_old=args.days,
                dry_run=args.dry_run
            )
        
        elif args.command == "optimize":
            manager.optimize_system()
        
        elif args.command == "status":
            manager.show_status()
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
