#!/usr/bin/env python3
"""
PDF Sentinel - Entry Point
A stealth desktop tool for legal teams to hash, stamp, and verify PDF document integrity.
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


def get_resource_path(relative_path: str) -> Path:
    """Get the absolute path to a resource, works for dev and PyInstaller."""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        base_path = Path(sys._MEIPASS)
    else:
        # Running in development
        base_path = Path(__file__).parent
    
    return base_path / relative_path


def main():
    """Initialize and run the PDF Sentinel application."""
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Sentinel")
    app.setApplicationVersion("1.3.0")
    app.setOrganizationName("Sentinel")
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Show splash screen
    from components.splash_screen import SplashScreen
    splash = SplashScreen()
    splash.show()
    app.processEvents()
    
    # Progress: Loading settings
    splash.set_progress(20, "Loading settings...")
    app.processEvents()
    
    # Load stylesheet based on saved theme preference
    from core.settings_manager import settings
    theme = settings.theme
    if theme == "light":
        stylesheet_path = get_resource_path("assets/styles_light.qss")
    else:
        stylesheet_path = get_resource_path("assets/styles.qss")
    
    splash.set_progress(40, "Applying theme...")
    app.processEvents()
    
    try:
        with open(stylesheet_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Stylesheet not found at: {stylesheet_path}")
    
    splash.set_progress(60, "Loading components...")
    app.processEvents()
    
    # Import main app (this loads all components)
    from app import PDFSentinelApp
    
    splash.set_progress(80, "Initializing application...")
    app.processEvents()
    
    # Create main window
    window = PDFSentinelApp()
    
    splash.set_progress(100, "Ready!")
    app.processEvents()
    
    # Short delay to show 100% complete
    QTimer.singleShot(500, splash.close)
    QTimer.singleShot(500, window.show)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

