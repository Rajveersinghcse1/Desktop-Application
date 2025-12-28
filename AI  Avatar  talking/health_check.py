#!/usr/bin/env python3
"""
System health checker with auto-fix for AI Avatar Studio.

Diagnoses issues and suggests/applies fixes automatically.

Usage:
    python health_check.py
    python health_check.py --fix
    python health_check.py --detailed
    python health_check.py --export report.json

Author: AI Avatar Studio
Date: 2025-12-22
"""

import os
import sys
import json
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


class HealthCheck:
    """System health checker with auto-fix capabilities."""
    
    def __init__(self):
        """Initialize health checker."""
        self.base_dir = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.passed = []
        self.fixes_applied = []
    
    def add_issue(self, check: str, message: str, fix: str = None):
        """Add critical issue."""
        self.issues.append({
            'check': check,
            'message': message,
            'fix': fix
        })
    
    def add_warning(self, check: str, message: str, fix: str = None):
        """Add warning."""
        self.warnings.append({
            'check': check,
            'message': message,
            'fix': fix
        })
    
    def add_passed(self, check: str, message: str = "OK"):
        """Add passed check."""
        self.passed.append({
            'check': check,
            'message': message
        })
    
    def check_python_version(self) -> bool:
        """Check Python version."""
        version = sys.version_info
        
        if version >= (3, 8) and version < (3, 12):
            self.add_passed(
                "Python Version",
                f"{version.major}.{version.minor}.{version.micro}"
            )
            return True
        else:
            self.add_issue(
                "Python Version",
                f"Python {version.major}.{version.minor} detected. Requires 3.8-3.11",
                "Install Python 3.8-3.11 from python.org"
            )
            return False
    
    def check_required_files(self) -> bool:
        """Check required project files."""
        required_files = [
            "main.py",
            "requirements.txt",
            "config/settings.py",
            "utils/database_manager.py"
        ]
        
        all_exist = True
        
        for file_path in required_files:
            full_path = self.base_dir / file_path
            if full_path.exists():
                self.add_passed(f"File: {file_path}", "Found")
            else:
                self.add_issue(
                    f"File: {file_path}",
                    f"Required file missing: {file_path}",
                    f"Restore {file_path} from backup or repository"
                )
                all_exist = False
        
        return all_exist
    
    def check_directories(self, auto_fix: bool = False) -> bool:
        """Check required directories."""
        required_dirs = [
            "output",
            "models",
            "logs",
            "temp",
            "data/database"
        ]
        
        all_exist = True
        
        for dir_path in required_dirs:
            full_path = self.base_dir / dir_path
            if full_path.exists():
                self.add_passed(f"Directory: {dir_path}", "Found")
            else:
                if auto_fix:
                    try:
                        full_path.mkdir(parents=True, exist_ok=True)
                        self.add_passed(f"Directory: {dir_path}", "Created")
                        self.fixes_applied.append(f"Created directory: {dir_path}")
                    except Exception as e:
                        self.add_issue(
                            f"Directory: {dir_path}",
                            f"Failed to create: {str(e)}",
                            f"Manually create: {dir_path}"
                        )
                        all_exist = False
                else:
                    self.add_warning(
                        f"Directory: {dir_path}",
                        f"Missing directory: {dir_path}",
                        f"Run with --fix to create automatically"
                    )
        
        return all_exist
    
    def check_dependencies(self) -> bool:
        """Check Python package dependencies."""
        required_packages = {
            'torch': 'PyTorch',
            'cv2': 'OpenCV',
            'PIL': 'Pillow',
            'numpy': 'NumPy',
            'librosa': 'librosa'
        }
        
        all_installed = True
        
        for import_name, package_name in required_packages.items():
            try:
                __import__(import_name)
                self.add_passed(f"Package: {package_name}", "Installed")
            except ImportError:
                self.add_warning(
                    f"Package: {package_name}",
                    f"{package_name} not installed",
                    f"pip install {package_name.lower()}"
                )
                all_installed = False
        
        return all_installed
    
    def check_gpu(self) -> bool:
        """Check GPU availability."""
        try:
            import torch
            
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                
                self.add_passed(
                    "GPU",
                    f"{gpu_name} ({gpu_memory:.1f} GB)"
                )
                
                # Check if GPU memory is sufficient
                if gpu_memory < 4:
                    self.add_warning(
                        "GPU Memory",
                        f"Only {gpu_memory:.1f} GB available. Recommend 4GB+",
                        "Consider using CPU mode or upgrade GPU"
                    )
                
                return True
            else:
                self.add_warning(
                    "GPU",
                    "No GPU detected, will use CPU",
                    "Install CUDA-enabled PyTorch for GPU support"
                )
                return False
        
        except ImportError:
            self.add_warning(
                "GPU",
                "PyTorch not installed, cannot check GPU",
                "pip install torch torchvision"
            )
            return False
    
    def check_disk_space(self) -> bool:
        """Check available disk space."""
        try:
            import shutil
            
            total, used, free = shutil.disk_usage(self.base_dir)
            free_gb = free / (1024**3)
            
            if free_gb >= 10:
                self.add_passed(
                    "Disk Space",
                    f"{free_gb:.1f} GB available"
                )
                return True
            elif free_gb >= 5:
                self.add_warning(
                    "Disk Space",
                    f"Only {free_gb:.1f} GB available",
                    "Clean up disk space. Recommend 10GB+ free"
                )
                return True
            else:
                self.add_issue(
                    "Disk Space",
                    f"Critical: Only {free_gb:.1f} GB available",
                    "Free up disk space immediately. Need 5GB minimum"
                )
                return False
        
        except Exception as e:
            self.add_warning(
                "Disk Space",
                f"Cannot check disk space: {str(e)}",
                None
            )
            return True
    
    def check_ffmpeg(self) -> bool:
        """Check FFmpeg installation."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                self.add_passed("FFmpeg", version_line.split()[2])
                return True
            else:
                self.add_issue(
                    "FFmpeg",
                    "FFmpeg not working properly",
                    "Reinstall FFmpeg"
                )
                return False
        
        except FileNotFoundError:
            self.add_issue(
                "FFmpeg",
                "FFmpeg not found in PATH",
                "Install FFmpeg: https://ffmpeg.org/download.html"
            )
            return False
        except Exception as e:
            self.add_warning(
                "FFmpeg",
                f"Cannot check FFmpeg: {str(e)}",
                None
            )
            return True
    
    def check_database(self, auto_fix: bool = False) -> bool:
        """Check database connectivity."""
        try:
            from utils.database_manager import DatabaseManager
            
            db = DatabaseManager()
            
            # Test basic operation
            projects = db.get_all_projects()
            
            self.add_passed(
                "Database",
                f"Connected ({len(projects)} projects)"
            )
            return True
        
        except Exception as e:
            if auto_fix:
                try:
                    # Try to initialize database
                    from utils.database_manager import DatabaseManager
                    db = DatabaseManager()
                    db._create_tables()
                    
                    self.add_passed("Database", "Initialized")
                    self.fixes_applied.append("Initialized database")
                    return True
                except Exception as fix_error:
                    self.add_issue(
                        "Database",
                        f"Cannot initialize database: {str(fix_error)}",
                        "Check database permissions and configuration"
                    )
                    return False
            else:
                self.add_warning(
                    "Database",
                    f"Database error: {str(e)}",
                    "Run with --fix to initialize database"
                )
                return False
    
    def check_models(self) -> bool:
        """Check AI model files."""
        models_dir = self.base_dir / "models"
        
        required_models = [
            "wav2lip.pth",
            "face_detection.dat"
        ]
        
        if not models_dir.exists():
            self.add_warning(
                "Models Directory",
                "Models directory not found",
                "Run: python setup_models.py"
            )
            return False
        
        models_found = []
        models_missing = []
        
        for model_file in required_models:
            model_path = models_dir / model_file
            if model_path.exists():
                size_mb = model_path.stat().st_size / (1024**2)
                models_found.append(f"{model_file} ({size_mb:.1f} MB)")
            else:
                models_missing.append(model_file)
        
        if models_found:
            self.add_passed(
                "Models Found",
                ", ".join(models_found)
            )
        
        if models_missing:
            self.add_warning(
                "Models Missing",
                f"Missing: {', '.join(models_missing)}",
                "Run: python setup_models.py"
            )
            return False
        
        return True
    
    def check_permissions(self) -> bool:
        """Check file permissions."""
        test_dirs = [
            self.base_dir / "output",
            self.base_dir / "logs"
        ]
        
        all_ok = True
        
        for dir_path in test_dirs:
            if not dir_path.exists():
                continue
            
            try:
                # Test write permission
                test_file = dir_path / ".test_write"
                test_file.write_text("test")
                test_file.unlink()
                
                self.add_passed(
                    f"Permissions: {dir_path.name}",
                    "Write OK"
                )
            except Exception as e:
                self.add_issue(
                    f"Permissions: {dir_path.name}",
                    f"Cannot write to {dir_path.name}: {str(e)}",
                    f"Fix permissions on {dir_path}"
                )
                all_ok = False
        
        return all_ok
    
    def run_health_check(self, auto_fix: bool = False, detailed: bool = False):
        """Run complete health check."""
        print("\n" + "="*70)
        print("SYSTEM HEALTH CHECK".center(70))
        print("="*70 + "\n")
        
        if auto_fix:
            print("🔧 Auto-fix enabled\n")
        
        # Run checks
        print("Running checks...\n")
        
        self.check_python_version()
        self.check_required_files()
        self.check_directories(auto_fix)
        self.check_dependencies()
        self.check_gpu()
        self.check_disk_space()
        self.check_ffmpeg()
        self.check_database(auto_fix)
        self.check_models()
        self.check_permissions()
        
        # Display results
        self.display_results(detailed)
    
    def display_results(self, detailed: bool = False):
        """Display check results."""
        print("\n" + "="*70)
        print("RESULTS".center(70))
        print("="*70 + "\n")
        
        # Issues
        if self.issues:
            print(f"❌ ISSUES ({len(self.issues)}):\n")
            for issue in self.issues:
                print(f"  • {issue['check']}: {issue['message']}")
                if issue['fix']:
                    print(f"    Fix: {issue['fix']}")
                print()
        
        # Warnings
        if self.warnings:
            print(f"⚠️  WARNINGS ({len(self.warnings)}):\n")
            for warning in self.warnings:
                print(f"  • {warning['check']}: {warning['message']}")
                if warning['fix']:
                    print(f"    Fix: {warning['fix']}")
                print()
        
        # Passed (only in detailed mode)
        if detailed and self.passed:
            print(f"✅ PASSED ({len(self.passed)}):\n")
            for passed in self.passed:
                print(f"  • {passed['check']}: {passed['message']}")
            print()
        
        # Fixes applied
        if self.fixes_applied:
            print(f"🔧 FIXES APPLIED ({len(self.fixes_applied)}):\n")
            for fix in self.fixes_applied:
                print(f"  • {fix}")
            print()
        
        # Summary
        total = len(self.issues) + len(self.warnings) + len(self.passed)
        
        print("="*70)
        print(f"Total Checks: {total}")
        print(f"  Issues:   {len(self.issues)}")
        print(f"  Warnings: {len(self.warnings)}")
        print(f"  Passed:   {len(self.passed)}")
        print("="*70 + "\n")
        
        # Overall status
        if self.issues:
            print("❌ SYSTEM NOT READY")
            print("   Fix critical issues before running the application.\n")
            return 1
        elif self.warnings:
            print("⚠️  SYSTEM READY WITH WARNINGS")
            print("   Application will run, but consider fixing warnings.\n")
            return 0
        else:
            print("✅ SYSTEM HEALTHY")
            print("   All checks passed!\n")
            return 0
    
    def export_report(self, output_file: str):
        """Export health check report to JSON."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'platform': platform.platform(),
                'python_version': sys.version.split()[0]
            },
            'results': {
                'issues': self.issues,
                'warnings': self.warnings,
                'passed': self.passed,
                'fixes_applied': self.fixes_applied
            },
            'summary': {
                'total_checks': len(self.issues) + len(self.warnings) + len(self.passed),
                'issues_count': len(self.issues),
                'warnings_count': len(self.warnings),
                'passed_count': len(self.passed)
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Report exported to: {output_file}\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="System health check for AI Avatar Studio",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix issues when possible"
    )
    
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed results including passed checks"
    )
    
    parser.add_argument(
        "--export",
        type=str,
        metavar="FILE",
        help="Export report to JSON file"
    )
    
    args = parser.parse_args()
    
    checker = HealthCheck()
    
    try:
        checker.run_health_check(
            auto_fix=args.fix,
            detailed=args.detailed
        )
        
        if args.export:
            checker.export_report(args.export)
        
        sys.exit(checker.display_results(args.detailed) if not args.detailed else 0)
    
    except KeyboardInterrupt:
        print("\n\nHealth check cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
