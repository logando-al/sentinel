"""
PDF Sentinel - Main Application Window
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
import qtawesome as qta

from components.drop_zone import DropZoneWidget
from components.batch_view import BatchViewWidget
from components.watch_view import WatchViewWidget
from components.verify_view import VerifyViewWidget


# Icon color to match accent
ICON_COLOR = "#88A9C3"


class PDFSentinelApp(QMainWindow):
    """Main application window for PDF Sentinel."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Sentinel")
        self.setMinimumSize(900, 600)
        self.resize(1000, 700)
        
        # Set window icon
        self._set_window_icon()
        
        # Center window on screen
        self._center_window()
        
        # Setup UI
        self._setup_ui()
    
    def _set_window_icon(self):
        """Set the window icon."""
        import sys
        from pathlib import Path
        
        # Get resource path (works for both dev and packaged)
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).parent
        
        icon_path = base_path / "assets" / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
    
    def _center_window(self):
        """Center the window on the primary screen."""
        screen = self.screen().availableGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)
    
    def _setup_ui(self):
        """Initialize the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Content area (stacked widget for views)
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")
        
        # Create views FIRST (before sidebar, so sidebar can reference them)
        self.drop_zone = DropZoneWidget()
        self.batch_view = BatchViewWidget()
        self.watch_view = WatchViewWidget()
        self.verify_view = VerifyViewWidget()
        
        self.content_stack.addWidget(self.drop_zone)
        self.content_stack.addWidget(self.batch_view)
        self.content_stack.addWidget(self.watch_view)
        self.content_stack.addWidget(self.verify_view)
        
        # Sidebar navigation (after views are created)
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_stack, 1)
        
        # Start with drop zone view
        self.content_stack.setCurrentWidget(self.drop_zone)
    
    def _create_sidebar(self) -> QFrame:
        """Create the sidebar navigation."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(8)
        
        # Logo/Title
        title = QLabel("PDF Sentinel")
        title.setObjectName("sidebarTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Navigation buttons with QtAwesome icons
        self.nav_buttons = []
        
        nav_items = [
            ("fa5s.home", "Home", self.drop_zone),
            ("fa5s.layer-group", "Batch", self.batch_view),
            ("fa5s.eye", "Watch Folder", self.watch_view),
            ("fa5s.check-circle", "Verify", self.verify_view),
        ]
        
        for icon_name, label, widget in nav_items:
            btn = QPushButton(f"   {label}")
            btn.setIcon(qta.icon(icon_name, color=ICON_COLOR))
            btn.setIconSize(QSize(18, 18))
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, w=widget: self._switch_view(w))
            layout.addWidget(btn)
            self.nav_buttons.append((btn, widget))
        
        # Set first button as active
        self.nav_buttons[0][0].setChecked(True)
        
        layout.addStretch()
        
        # Settings button at bottom
        settings_btn = QPushButton("   Settings")
        settings_btn.setIcon(qta.icon("fa5s.cog", color=ICON_COLOR))
        settings_btn.setIconSize(QSize(18, 18))
        settings_btn.setObjectName("navButton")
        layout.addWidget(settings_btn)
        
        # Version label
        version = QLabel("v1.0.0")
        version.setObjectName("versionLabel")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        return sidebar
    
    def _switch_view(self, widget: QWidget):
        """Switch to the specified view."""
        self.content_stack.setCurrentWidget(widget)
        
        # Update button states
        for btn, w in self.nav_buttons:
            btn.setChecked(w == widget)
