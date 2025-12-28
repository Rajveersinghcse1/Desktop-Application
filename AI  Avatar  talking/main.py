#!/usr/bin/env python3
"""
AI Avatar Studio - Main Entry Point
Transform static images into lifelike talking avatars
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

import logging
from config import settings, paths
from utils import setup_logging, check_system_requirements, get_logger

# Setup logging
logger = setup_logging(
    log_level=settings.LOG_LEVEL,
    log_dir=paths.logs_dir,
    console_output=True,
    file_output=True
)


def print_banner():
    """Print application banner"""
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              AI AVATAR STUDIO                                ║
║                                                              ║
║     Transform Images into Lifelike Talking Avatars          ║
║                                                              ║
║                    Version {settings.APP_VERSION}            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def initialize_application():
    """Initialize application environment"""
    logger.info("Initializing AI Avatar Studio...")
    
    # Ensure all directories exist
    logger.debug("Creating directory structure...")
    paths.ensure_all_directories()
    logger.info("[OK] Directory structure ready")
    
    # Initialize database
    logger.debug("Initializing database...")
    try:
        from utils import DatabaseManager
        db = DatabaseManager(settings.DATABASE_PATH)
        logger.info(f"[OK] Database initialized: {settings.DATABASE_PATH}")
        
        # Show database statistics
        stats = db.get_statistics()
        logger.info(
            f"  - Total projects: {stats['total_projects']}"
        )
        logger.info(
            f"  - Total generations: {stats['total_generations']}"
        )
        if stats['total_generations'] > 0:
            logger.info(
                f"  - Success rate: {stats['success_rate']:.2f}%"
            )
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False
    
    # Clean up old temporary files
    logger.debug("Cleaning up old temporary files...")
    try:
        paths.cleanup_temp_files(older_than_hours=24)
        logger.info("[OK] Temporary files cleaned")
    except Exception as e:
        logger.warning(f"Could not clean temporary files: {e}")
    
    logger.info("[OK] Application initialized successfully")
    return True


def run_cli_mode():
    """Run application in CLI mode (for testing)"""
    logger.info("Running in CLI mode...")
    
    print("\nAI Avatar Studio - CLI Mode")
    print("=" * 60)
    print("\nAvailable commands:")
    print("  1. System check")
    print("  2. View statistics")
    print("  3. List projects")
    print("  4. Clean cache")
    print("  0. Exit")
    print()
    
    from utils import DatabaseManager
    db = DatabaseManager()
    
    while True:
        try:
            choice = input("Enter command number: ").strip()
            
            if choice == '0':
                print("Goodbye!")
                break
            
            elif choice == '1':
                print("\nRunning system check...")
                check_system_requirements()
            
            elif choice == '2':
                stats = db.get_statistics()
                print("\n📊 Database Statistics:")
                print(f"  Total Projects: {stats['total_projects']}")
                print(f"  Total Generations: {stats['total_generations']}")
                print(f"  Completed: {stats['completed_generations']}")
                print(f"  Failed: {stats['failed_generations']}")
                print(f"  Success Rate: {stats['success_rate']:.2f}%")
                if stats['average_processing_time_seconds'] > 0:
                    print(f"  Avg Processing Time: {stats['average_processing_time_seconds']:.2f}s")
                print()
            
            elif choice == '3':
                projects = db.get_all_projects()
                if projects:
                    print(f"\n📁 Projects ({len(projects)}):")
                    for proj in projects[:10]:  # Show first 10
                        print(f"  - {proj['name']} ({proj['status']})")
                    if len(projects) > 10:
                        print(f"  ... and {len(projects) - 10} more")
                else:
                    print("\n📁 No projects found")
                print()
            
            elif choice == '4':
                print("\n🧹 Cleaning cache...")
                paths.cleanup_temp_files(older_than_hours=0)  # Clean all
                print("✓ Cache cleaned")
                print()
            
            else:
                print("Invalid choice. Please try again.\n")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}\n")


def run_gui_mode():
    """Run application with GUI"""
    logger.info("Starting GUI mode...")
    
    try:
        # Import GUI components
        from gui import MainWindow, show_splash_screen
        from utils import DatabaseManager, ModelManager
        from core.pipeline import GenerationPipeline
        
        # Show splash screen during initialization
        def init_callback(progress_callback):
            progress_callback(10, "Loading configuration...")
            
            progress_callback(30, "Initializing database...")
            db = DatabaseManager()
            
            progress_callback(50, "Loading model manager...")
            model_manager = ModelManager(str(paths.models_dir))
            
            progress_callback(70, "Creating pipeline...")
            pipeline = GenerationPipeline(settings.to_dict(), db, model_manager)
            
            progress_callback(90, "Preparing GUI...")
            main_window = MainWindow(db, model_manager, pipeline)
            main_window.create()
            
            progress_callback(100, "Ready!")
            return main_window
        
        # Show splash
        splash = show_splash_screen(init_callback, version=settings.APP_VERSION)
        
        if splash:
            splash.close()
        
        # Note: main_window is created in init_callback
        # We need to refactor this slightly
        
        # Create components
        db = DatabaseManager()
        model_manager = ModelManager(str(paths.models_dir))
        pipeline = GenerationPipeline(settings.to_dict(), db, model_manager)
        
        # Create and run main window
        app = MainWindow(db, model_manager, pipeline)
        app.create()
        logger.info("[OK] GUI initialized")
        app.run()
        
    except ImportError as e:
        logger.error(f"Failed to import GUI components: {e}")
        print("\n❌ GUI components not available.")
        print("The GUI requires CustomTkinter to be installed.")
        print("Install with: pip install customtkinter")
        print("\nFalling back to CLI mode...")
        return run_cli_mode()
    
    except Exception as e:
        logger.error(f"GUI error: {e}", exc_info=True)
        print(f"\n❌ GUI failed to start: {e}")
        print("Falling back to CLI mode...")
        return run_cli_mode()


def main():
    """Main entry point"""
    try:
        # Print banner
        print_banner()
        
        # Run system checks
        logger.info("Running system checks...")
        if not check_system_requirements():
            logger.warning("System checks failed, but continuing anyway...")
            print("\n⚠️  Some system requirements are not met.")
            print("The application may not work properly.")
            
            response = input("\nContinue anyway? (yes/no): ").strip().lower()
            if response != 'yes':
                logger.info("User chose to exit")
                return 1
        
        # Initialize application
        if not initialize_application():
            logger.error("Application initialization failed")
            return 1
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] in ['--cli', '-c', 'cli']:
                return run_cli_mode()
            elif sys.argv[1] in ['--help', '-h']:
                print("\nUsage:")
                print("  python main.py          # Start with GUI")
                print("  python main.py --cli    # Start in CLI mode")
                print("  python main.py --help   # Show this help")
                return 0
        
        # Start GUI by default
        run_gui_mode()
        
        logger.info("Application exited normally")
        return 0
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\n\nApplication interrupted. Goodbye!")
        return 0
    
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        print(f"\n❌ Critical error: {e}")
        print("Check logs for details.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
