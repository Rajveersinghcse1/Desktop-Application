#!/usr/bin/env python3
"""
Master launcher for AI Avatar Studio.

Provides unified entry point for all major operations.

Usage:
    python start.py                  # Launch GUI
    python start.py --cli            # CLI mode
    python start.py --setup          # Run setup wizard
    python start.py --health         # Health check
    python start.py --generate ...   # Generate video

Author: AI Avatar Studio
Date: 2025-12-22
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def print_banner():
    """Print application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              AI Avatar Studio v1.0.0                          ║
║                                                               ║
║         Create Talking Avatar Videos with AI Magic           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def check_first_run():
    """Check if this is the first run."""
    env_file = Path(__file__).parent / ".env"
    models_dir = Path(__file__).parent / "models"
    
    if not env_file.exists() or not models_dir.exists():
        return True
    
    return False


def run_gui():
    """Launch GUI application."""
    print("\n🚀 Launching GUI...\n")
    import subprocess
    subprocess.run([sys.executable, "main.py"])


def run_cli():
    """Launch CLI mode."""
    print("\n💻 Launching CLI mode...\n")
    import subprocess
    subprocess.run([sys.executable, "main.py", "--cli"])


def run_setup():
    """Run setup wizard."""
    print("\n⚙️  Starting setup wizard...\n")
    from quick_start import main as setup_main
    setup_main()


def run_health_check(fix=False):
    """Run health check."""
    print("\n🏥 Running health check...\n")
    from health_check import main as health_main
    
    sys.argv = ['health_check.py']
    if fix:
        sys.argv.append('--fix')
    
    health_main()


def run_generate(args):
    """Run video generation."""
    print("\n🎥 Starting video generation...\n")
    from generate_video import main as generate_main
    
    # Pass through arguments
    sys.argv = ['generate_video.py'] + args
    generate_main()


def run_monitor():
    """Run generation monitor."""
    print("\n📊 Launching monitor...\n")
    from monitor_generation import main as monitor_main
    monitor_main()


def run_maintenance():
    """Run maintenance tool."""
    print("\n🔧 Launching maintenance tool...\n")
    from maintenance import main as maintenance_main
    maintenance_main()


def run_benchmark():
    """Run benchmark."""
    print("\n⚡ Running benchmark...\n")
    from benchmark import main as benchmark_main
    benchmark_main()


def show_status():
    """Show system status."""
    print("\n📋 System Status\n")
    print("="*70 + "\n")
    
    # Check key components
    checks = {
        'Python': sys.version.split()[0],
        'Working Directory': os.getcwd(),
        'Config File': '✅' if Path('.env').exists() else '❌',
        'Models Directory': '✅' if Path('models').exists() else '❌',
        'Database': '✅' if Path('data/database').exists() else '❌',
    }
    
    for key, value in checks.items():
        print(f"  {key:20s} {value}")
    
    print("\n" + "="*70)
    
    # Check GPU
    try:
        import torch
        if torch.cuda.is_available():
            print(f"\n  GPU: ✅ {torch.cuda.get_device_name(0)}")
        else:
            print("\n  GPU: ❌ Not available (will use CPU)")
    except ImportError:
        print("\n  GPU: ⚠️  PyTorch not installed")
    
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Avatar Studio - Master Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch GUI (default)
  python start.py
  
  # Run setup wizard (first time)
  python start.py --setup
  
  # Generate video from CLI
  python start.py --generate -i photo.jpg -t "Hello world"
  
  # Check system health
  python start.py --health
  
  # Run maintenance
  python start.py --maintenance
  
  # Show status
  python start.py --status

For more information, see USAGE_GUIDE.md
        """
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch GUI application (default)'
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Launch in CLI mode'
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Run setup wizard'
    )
    
    parser.add_argument(
        '--health',
        action='store_true',
        help='Run health check'
    )
    
    parser.add_argument(
        '--health-fix',
        action='store_true',
        help='Run health check with auto-fix'
    )
    
    parser.add_argument(
        '--generate',
        action='store_true',
        help='Generate video (provide additional arguments)'
    )
    
    parser.add_argument(
        '--monitor',
        action='store_true',
        help='Launch generation monitor'
    )
    
    parser.add_argument(
        '--maintenance',
        action='store_true',
        help='Launch maintenance tool'
    )
    
    parser.add_argument(
        '--benchmark',
        action='store_true',
        help='Run performance benchmark'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show system status'
    )
    
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information'
    )
    
    # Parse known args to separate our args from pass-through args
    args, remaining = parser.parse_known_args()
    
    print_banner()
    
    # Handle version
    if args.version:
        from version import get_version_info
        import json
        print(json.dumps(get_version_info(), indent=2))
        return
    
    # Handle status
    if args.status:
        show_status()
        return
    
    # Check first run
    if check_first_run() and not args.setup and not args.health:
        print("\n⚠️  First run detected!\n")
        print("It looks like this is your first time running AI Avatar Studio.")
        print("Would you like to run the setup wizard?\n")
        
        response = input("Run setup wizard? [Y/n]: ").strip().lower()
        if response != 'n':
            run_setup()
            return
        else:
            print("\nYou can run setup later with: python start.py --setup\n")
    
    try:
        # Route to appropriate function
        if args.setup:
            run_setup()
        elif args.health or args.health_fix:
            run_health_check(fix=args.health_fix)
        elif args.generate:
            run_generate(remaining)
        elif args.monitor:
            run_monitor()
        elif args.maintenance:
            run_maintenance()
        elif args.benchmark:
            run_benchmark()
        elif args.cli:
            run_cli()
        else:
            # Default: GUI
            run_gui()
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        print("For help, run: python start.py --help")
        print("Or check health: python start.py --health\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
