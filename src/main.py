#!/usr/bin/env python3
"""
PDF Sentinel - Entry Point
A stealth desktop tool for legal teams to hash, stamp, and verify PDF document integrity.
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app import PDFSentinelApp


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
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Sentinel")
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Load stylesheet
    stylesheet_path = get_resource_path("assets/styles.qss")
    try:
        with open(stylesheet_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Stylesheet not found at: {stylesheet_path}")
    
    # Create and show main window
    window = PDFSentinelApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
