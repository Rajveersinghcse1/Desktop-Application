"""Dark theme for OpenUP application."""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt


def apply_dark_theme(app: QApplication):
    """
    Apply dark theme to application.
    
    Args:
        app: QApplication instance
    """
    # Create dark palette
    palette = QPalette()
    
    # Base colors
    dark_bg = QColor(30, 30, 30)
    darker_bg = QColor(20, 20, 20)
    light_bg = QColor(45, 45, 45)
    text_color = QColor(220, 220, 220)
    disabled_text = QColor(120, 120, 120)
    highlight = QColor(42, 130, 218)
    highlight_text = QColor(255, 255, 255)
    
    # Set palette colors
    palette.setColor(QPalette.ColorRole.Window, dark_bg)
    palette.setColor(QPalette.ColorRole.WindowText, text_color)
    palette.setColor(QPalette.ColorRole.Base, darker_bg)
    palette.setColor(QPalette.ColorRole.AlternateBase, light_bg)
    palette.setColor(QPalette.ColorRole.ToolTipBase, light_bg)
    palette.setColor(QPalette.ColorRole.ToolTipText, text_color)
    palette.setColor(QPalette.ColorRole.Text, text_color)
    palette.setColor(QPalette.ColorRole.Button, light_bg)
    palette.setColor(QPalette.ColorRole.ButtonText, text_color)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, highlight)
    palette.setColor(QPalette.ColorRole.Highlight, highlight)
    palette.setColor(QPalette.ColorRole.HighlightedText, highlight_text)
    
    # Disabled colors
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_text)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_text)
    
    app.setPalette(palette)
    
    # Apply stylesheet for additional styling
    app.setStyleSheet("""
        QToolTip {
            color: #ffffff;
            background-color: #2d2d2d;
            border: 1px solid #555555;
            padding: 4px;
        }
        
        QMenuBar {
            background-color: #2d2d2d;
            color: #dcdcdc;
        }
        
        QMenuBar::item:selected {
            background-color: #3d3d3d;
        }
        
        QMenu {
            background-color: #2d2d2d;
            color: #dcdcdc;
            border: 1px solid #555555;
        }
        
        QMenu::item:selected {
            background-color: #2a82da;
        }
        
        QPushButton {
            background-color: #3d3d3d;
            color: #dcdcdc;
            border: 1px solid #555555;
            padding: 5px 15px;
            border-radius: 3px;
        }
        
        QPushButton:hover {
            background-color: #4d4d4d;
        }
        
        QPushButton:pressed {
            background-color: #2a82da;
        }
        
        QPushButton:disabled {
            background-color: #2d2d2d;
            color: #787878;
        }
        
        QLineEdit {
            background-color: #141414;
            color: #dcdcdc;
            border: 1px solid #555555;
            padding: 4px;
            border-radius: 2px;
        }
        
        QLineEdit:focus {
            border: 1px solid #2a82da;
        }
        
        QTextEdit, QPlainTextEdit {
            background-color: #141414;
            color: #dcdcdc;
            border: 1px solid #555555;
        }
        
        QTableView {
            background-color: #141414;
            alternate-background-color: #1e1e1e;
            color: #dcdcdc;
            gridline-color: #3d3d3d;
            border: 1px solid #555555;
        }
        
        QTableView::item:selected {
            background-color: #2a82da;
        }
        
        QHeaderView::section {
            background-color: #2d2d2d;
            color: #dcdcdc;
            padding: 4px;
            border: 1px solid #3d3d3d;
        }
        
        QScrollBar:vertical {
            background-color: #2d2d2d;
            width: 14px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #555555;
            min-height: 20px;
            border-radius: 7px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #6d6d6d;
        }
        
        QScrollBar:horizontal {
            background-color: #2d2d2d;
            height: 14px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #555555;
            min-width: 20px;
            border-radius: 7px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #6d6d6d;
        }
        
        QTabWidget::pane {
            border: 1px solid #555555;
        }
        
        QTabBar::tab {
            background-color: #2d2d2d;
            color: #dcdcdc;
            padding: 8px 16px;
            border: 1px solid #555555;
            border-bottom: none;
        }
        
        QTabBar::tab:selected {
            background-color: #3d3d3d;
        }
        
        QTabBar::tab:hover {
            background-color: #4d4d4d;
        }
        
        QProgressBar {
            border: 1px solid #555555;
            border-radius: 3px;
            text-align: center;
            background-color: #141414;
            color: #dcdcdc;
        }
        
        QProgressBar::chunk {
            background-color: #2a82da;
        }
        
        QStatusBar {
            background-color: #2d2d2d;
            color: #dcdcdc;
        }
        
        QSplitter::handle {
            background-color: #3d3d3d;
        }
        
        QSplitter::handle:hover {
            background-color: #4d4d4d;
        }
    """)


def apply_light_theme(app: QApplication):
    """
    Apply light theme to application.
    
    Args:
        app: QApplication instance
    """
    # Reset to default palette
    app.setPalette(QApplication.style().standardPalette())
    app.setStyleSheet("")  # Clear custom stylesheet
