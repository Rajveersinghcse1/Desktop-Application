"""
OpenUP - Universal File Preview & Visualization Application
Main entry point for the desktop application.
"""

import sys
import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QIcon

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.config import Config
from src.core.logger import setup_logging
from src.ui.main_window import MainWindow
from src.utils.helpers import ensure_directories


def setup_application():
    """Initialize application settings and directories."""
    # Set application metadata
    QCoreApplication.setApplicationName("OpenUP")
    QCoreApplication.setOrganizationName("OpenUP")
    QCoreApplication.setApplicationVersion("1.0.0")
    
    # Enable high DPI scaling (PyQt6 handles this automatically)
    # Note: AA_EnableHighDpiScaling is deprecated in Qt6
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Ensure required directories exist
    ensure_directories()
    
    # Setup logging
    setup_logging()
    
    logging.info("=" * 80)
    logging.info("OpenUP Application Starting")
    logging.info("=" * 80)


def main():
    """Main application entry point."""
    try:
        # Setup application
        setup_application()
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Modern cross-platform style
        
        # Set application icon
        icon_path = Path(__file__).parent / 'resources' / 'icons' / 'openup.png'
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
        
        # Load configuration
        config = Config()
        
        # Apply theme
        if config.get('theme') == 'dark':
            from src.ui.themes import apply_dark_theme
            apply_dark_theme(app)
        
        # Create and show main window
        main_window = MainWindow(config)
        main_window.show()
        
        # Handle command line arguments (file to open)
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            if os.path.isfile(file_path):
                main_window.open_file(file_path)
        
        logging.info("Application initialized successfully")
        
        # Start event loop
        exit_code = app.exec()
        
        logging.info(f"Application exiting with code {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logging.critical(f"Fatal error during application startup: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
