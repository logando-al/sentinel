"""
PDF Sentinel - Splash Screen
Shows a loading screen during app initialization.
"""

from PyQt6.QtWidgets import QSplashScreen, QProgressBar, QVBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient
import sys
from pathlib import Path


class SplashScreen(QSplashScreen):
    """Splash screen with progress bar."""
    
    def __init__(self):
        # Create a custom pixmap for the splash
        pixmap = self._create_splash_pixmap()
        super().__init__(pixmap)
        
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
        
        # Progress bar
        self.progress = QProgressBar(self)
        self.progress.setGeometry(50, 320, 300, 8)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #1a1a1a;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #88A9C3;
                border-radius: 4px;
            }
        """)
        self.progress.setValue(0)
        
        # Status label
        self.status_label = QLabel("Initializing...", self)
        self.status_label.setGeometry(50, 335, 300, 20)
        self.status_label.setStyleSheet("color: #888888; font-size: 10pt;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def _create_splash_pixmap(self) -> QPixmap:
        """Create a custom splash screen pixmap."""
        width, height = 400, 380
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor("#0d0d0d"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw gradient border
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, QColor("#88A9C3"))
        gradient.setColorAt(1, QColor("#5a7a8a"))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(0, 0, width, height, 16, 16)
        
        # Inner background
        painter.setBrush(QColor("#0d0d0d"))
        painter.drawRoundedRect(3, 3, width - 6, height - 6, 14, 14)
        
        # Draw shield icon from file
        if getattr(sys, 'frozen', False):
            icon_path = Path(sys._MEIPASS) / "assets" / "icon.png"
        else:
            icon_path = Path(__file__).parent.parent / "assets" / "icon.png"
            
        if icon_path.exists():
            icon_pixmap = QPixmap(str(icon_path))
            # Scale to reasonable size
            target_size = 100
            icon_pixmap = icon_pixmap.scaled(target_size, target_size, 
                                           Qt.AspectRatioMode.KeepAspectRatio, 
                                           Qt.TransformationMode.SmoothTransformation)
            
            # Center horizontally
            x = (width - icon_pixmap.width()) // 2
            y = 60
            painter.drawPixmap(x, y, icon_pixmap)
        else:
            # Fallback if icon missing
            painter.setBrush(QColor("#88A9C3"))
            painter.drawRect(width // 2 - 25, 60, 50, 60)
        
        # App name
        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 28, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(0, 200, width, 50, Qt.AlignmentFlag.AlignCenter, "PDF Sentinel")
        
        # Tagline
        painter.setPen(QColor("#888888"))
        font = QFont("Segoe UI", 11)
        painter.setFont(font)
        painter.drawText(0, 250, width, 30, Qt.AlignmentFlag.AlignCenter, 
                        "Secure Document Verification")
        
        # Version
        from core.version import __version__
        painter.setPen(QColor("#88A9C3"))
        font = QFont("Segoe UI", 10)
        painter.setFont(font)
        painter.drawText(0, 280, width, 20, Qt.AlignmentFlag.AlignCenter, f"v{__version__}")
        
        painter.end()
        return pixmap
    
    def set_progress(self, value: int, status: str = None):
        """Update progress bar and status text."""
        self.progress.setValue(value)
        if status:
            self.status_label.setText(status)
        self.repaint()
