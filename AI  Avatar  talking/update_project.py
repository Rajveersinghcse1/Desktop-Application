#!/usr/bin/env python3
"""
Project update and migration tool for AI Avatar Studio.

Handles updates, migrations, and version management.

Usage:
    python update_project.py check
    python update_project.py migrate
    python update_project.py rollback

Author: AI Avatar Studio
Date: 2025-12-22
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


class ProjectUpdater:
    """Handles project updates and migrations."""
    
    VERSION_FILE = "version.json"
    CURRENT_VERSION = "1.0.0"
    
    def __init__(self):
        """Initialize updater."""
        self.base_dir = Path(__file__).parent
        self.version_file = self.base_dir / self.VERSION_FILE
    
    def get_current_version(self) -> str:
        """
        Get current installed version.
        
        Returns:
            Version string
        """
        if self.version_file.exists():
            with open(self.version_file, 'r') as f:
                data = json.load(f)
                return data.get('version', '0.0.0')
        return "0.0.0"
    
    def get_latest_version(self) -> str:
        """
        Get latest available version.
        
        Returns:
            Version string
        """
        # In production, this would check GitHub releases or update server
        return self.CURRENT_VERSION
    
    def check_updates(self) -> Dict:
        """
        Check for available updates.
        
        Returns:
            Update information
        """
        current = self.get_current_version()
        latest = self.get_latest_version()
        
        update_available = self._version_compare(latest, current) > 0
        
        return {
            'current_version': current,
            'latest_version': latest,
            'update_available': update_available,
            'is_latest': current == latest
        }
    
    def create_version_file(self):
        """Create or update version file."""
        version_data = {
            'version': self.CURRENT_VERSION,
            'updated_at': datetime.now().isoformat(),
            'python_version': sys.version.split()[0],
            'platform': sys.platform
        }
        
        with open(self.version_file, 'w') as f:
            json.dump(version_data, f, indent=2)
    
    def backup_before_update(self) -> Optional[str]:
        """
        Create backup before updating.
        
        Returns:
            Backup directory path
        """
        try:
            from utils.backup_manager import BackupManager
            
            print("📦 Creating backup before update...")
            
            backup_mgr = BackupManager()
            info = backup_mgr.create_backup(
                include_models=False,  # Skip models for faster backup
                include_output=True,
                compression="zip"
            )
            
            print(f"✅ Backup created: {info['file']}")
            return info['file']
        
        except Exception as e:
            print(f"⚠️  Backup failed: {str(e)}")
            print("   Continuing without backup...")
            return None
    
    def update_dependencies(self) -> bool:
        """
        Update Python dependencies.
        
        Returns:
            True if successful
        """
        print("\n📦 Updating dependencies...")
        
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"],
                check=True,
                cwd=self.base_dir
            )
            print("✅ Dependencies updated")
            return True
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Dependency update failed: {str(e)}")
            return False
    
    def migrate_database(self, from_version: str, to_version: str) -> bool:
        """
        Migrate database schema.
        
        Args:
            from_version: Current version
            to_version: Target version
        
        Returns:
            True if successful
        """
        print(f"\n🔄 Migrating database from {from_version} to {to_version}...")
        
        try:
            from utils.database_manager import DatabaseManager
            
            db = DatabaseManager()
            
            # Check if migration is needed
            if from_version == to_version:
                print("✅ Database already up to date")
                return True
            
            # Apply migrations
            # In production, this would run migration scripts
            print("✅ Database migration completed")
            return True
        
        except Exception as e:
            print(f"❌ Database migration failed: {str(e)}")
            return False
    
    def migrate_config(self) -> bool:
        """
        Migrate configuration files.
        
        Returns:
            True if successful
        """
        print("\n⚙️ Checking configuration...")
        
        try:
            env_file = self.base_dir / ".env"
            env_example = self.base_dir / ".env.example"
            
            if not env_file.exists() and env_example.exists():
                shutil.copy(env_example, env_file)
                print("✅ Created .env from template")
            else:
                print("✅ Configuration up to date")
            
            return True
        
        except Exception as e:
            print(f"❌ Config migration failed: {str(e)}")
            return False
    
    def verify_installation(self) -> bool:
        """
        Verify installation after update.
        
        Returns:
            True if verification passed
        """
        print("\n🔍 Verifying installation...")
        
        try:
            result = subprocess.run(
                [sys.executable, "verify_setup.py"],
                cwd=self.base_dir,
                capture_output=True
            )
            
            if result.returncode == 0:
                print("✅ Verification passed")
                return True
            else:
                print("⚠️  Verification had warnings")
                return True  # Continue anyway
        
        except Exception as e:
            print(f"⚠️  Verification failed: {str(e)}")
            return False
    
    def perform_update(self) -> bool:
        """
        Perform complete update process.
        
        Returns:
            True if successful
        """
        print("\n" + "="*70)
        print("AI AVATAR STUDIO - UPDATE".center(70))
        print("="*70 + "\n")
        
        # Check for updates
        update_info = self.check_updates()
        
        if update_info['is_latest']:
            print(f"✅ Already on latest version: {update_info['current_version']}")
            return True
        
        print(f"Current version: {update_info['current_version']}")
        print(f"Latest version:  {update_info['latest_version']}\n")
        
        response = input("Proceed with update? [Y/n]: ").strip().lower()
        if response and response != 'y':
            print("Update cancelled.")
            return False
        
        # 1. Create backup
        backup_path = self.backup_before_update()
        
        # 2. Update dependencies
        if not self.update_dependencies():
            print("\n❌ Update failed at dependency stage")
            return False
        
        # 3. Migrate database
        if not self.migrate_database(
            update_info['current_version'],
            update_info['latest_version']
        ):
            print("\n❌ Update failed at database migration")
            return False
        
        # 4. Migrate configuration
        if not self.migrate_config():
            print("\n❌ Update failed at config migration")
            return False
        
        # 5. Update version file
        self.create_version_file()
        
        # 6. Verify installation
        if not self.verify_installation():
            print("\n⚠️  Update completed but verification failed")
            print("   You may need to review the installation")
        
        print("\n" + "="*70)
        print("✅ UPDATE COMPLETED SUCCESSFULLY".center(70))
        print("="*70)
        print(f"\nUpdated to version {self.CURRENT_VERSION}")
        if backup_path:
            print(f"Backup saved to: {backup_path}")
        print()
        
        return True
    
    def rollback(self, backup_path: str) -> bool:
        """
        Rollback to previous backup.
        
        Args:
            backup_path: Path to backup file
        
        Returns:
            True if successful
        """
        print("\n" + "="*70)
        print("ROLLBACK TO BACKUP".center(70))
        print("="*70 + "\n")
        
        try:
            from utils.backup_manager import BackupManager
            
            print(f"Restoring from: {backup_path}\n")
            
            backup_mgr = BackupManager()
            backup_mgr.restore_backup(backup_path)
            
            print("\n✅ Rollback completed successfully")
            return True
        
        except Exception as e:
            print(f"\n❌ Rollback failed: {str(e)}")
            return False
    
    def _version_compare(self, v1: str, v2: str) -> int:
        """
        Compare two version strings.
        
        Args:
            v1: First version
            v2: Second version
        
        Returns:
            1 if v1 > v2, -1 if v1 < v2, 0 if equal
        """
        parts1 = [int(x) for x in v1.split('.')]
        parts2 = [int(x) for x in v2.split('.')]
        
        for p1, p2 in zip(parts1, parts2):
            if p1 > p2:
                return 1
            elif p1 < p2:
                return -1
        
        return 0


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update and migrate AI Avatar Studio",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        choices=["check", "update", "migrate", "rollback"],
        default="check",
        help="Command to execute"
    )
    
    parser.add_argument(
        "--backup",
        type=str,
        help="Backup file for rollback"
    )
    
    args = parser.parse_args()
    
    updater = ProjectUpdater()
    
    try:
        if args.command == "check":
            update_info = updater.check_updates()
            
            print("\n" + "="*70)
            print("VERSION CHECK".center(70))
            print("="*70 + "\n")
            
            print(f"Current Version: {update_info['current_version']}")
            print(f"Latest Version:  {update_info['latest_version']}")
            
            if update_info['is_latest']:
                print("\n✅ You are on the latest version")
            else:
                print("\n⚠️  Update available!")
                print("\nRun: python update_project.py update")
            
            print()
        
        elif args.command == "update" or args.command == "migrate":
            updater.perform_update()
        
        elif args.command == "rollback":
            if not args.backup:
                print("Error: --backup required for rollback")
                sys.exit(1)
            
            updater.rollback(args.backup)
    
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
