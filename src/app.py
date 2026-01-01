"""
PDF Sentinel - Main Application Window
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QFrame, QFileDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QShortcut, QKeySequence
import qtawesome as qta

from components.drop_zone import DropZoneWidget
from components.batch_view import BatchViewWidget
from components.watch_view import WatchViewWidget
from components.verify_view import VerifyViewWidget
from components.settings_view import SettingsViewWidget


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
        
        # Setup keyboard shortcuts
        self._setup_shortcuts()
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Ctrl+O - Open file
        QShortcut(QKeySequence("Ctrl+O"), self, self._open_file)
        
        # Ctrl+B - Batch view
        QShortcut(QKeySequence("Ctrl+B"), self, lambda: self._switch_view(self.batch_view))
        
        # Ctrl+V - Verify view  
        QShortcut(QKeySequence("Ctrl+Shift+V"), self, lambda: self._switch_view(self.verify_view))
        
        # Ctrl+, - Settings
        QShortcut(QKeySequence("Ctrl+,"), self, lambda: self._switch_view(self.settings_view))
        
        # Escape - Home
        QShortcut(QKeySequence("Escape"), self, lambda: self._switch_view(self.drop_zone))
        
        # Ctrl+W - Watch folder view
        QShortcut(QKeySequence("Ctrl+W"), self, lambda: self._switch_view(self.watch_view))
    
    def _open_file(self):
        """Open file dialog and process selected PDF."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF File",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            self._switch_view(self.drop_zone)
            self.drop_zone._process_file(file_path)
    
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
        self.settings_view = SettingsViewWidget()
        
        self.content_stack.addWidget(self.drop_zone)
        self.content_stack.addWidget(self.batch_view)
        self.content_stack.addWidget(self.watch_view)
        self.content_stack.addWidget(self.verify_view)
        self.content_stack.addWidget(self.settings_view)
        
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
        self.settings_btn = QPushButton("   Settings")
        self.settings_btn.setIcon(qta.icon("fa5s.cog", color=ICON_COLOR))
        self.settings_btn.setIconSize(QSize(18, 18))
        self.settings_btn.setObjectName("navButton")
        self.settings_btn.setCheckable(True)
        self.settings_btn.clicked.connect(lambda: self._switch_view(self.settings_view))
        layout.addWidget(self.settings_btn)
        
        # Version label (clickable for About)
        version = QPushButton("v1.3.2")
        version.setObjectName("versionLabel")
        version.setFlat(True)
        version.setCursor(Qt.CursorShape.PointingHandCursor)
        version.clicked.connect(self._show_about)
        layout.addWidget(version)
        
        return sidebar
    
    def _switch_view(self, widget: QWidget):
        """Switch to the specified view."""
        self.content_stack.setCurrentWidget(widget)
        
        # Update button states
        for btn, w in self.nav_buttons:
            btn.setChecked(w == widget)
    
    def _show_about(self):
        """Show About dialog."""
        from PyQt6.QtWidgets import QMessageBox, QApplication
        
        # Get key fingerprint
        try:
            from core.signer import get_public_key_pem, get_key_fingerprint
            public_key = get_public_key_pem()
            fingerprint = get_key_fingerprint(public_key)
        except:
            fingerprint = "Not available"
        
        # Store for copy button
        self._about_fingerprint = fingerprint
        
        about_text = f"""
<h2>PDF Sentinel</h2>
<p><b>Version:</b> 1.3.2</p>
<p><b>Description:</b> Secure document verification and stamping tool for legal teams.</p>
<p><b>Your Key Fingerprint:</b><br><code>{fingerprint}</code></p>
<p><b>Last Updated:</b> 2026-01-01</p>
<hr>
<p><b>Features:</b></p>
<ul>
<li>SHA256 hash verification</li>
<li>RSA digital signatures</li>
<li>Visual seal stamping</li>
<li>Verification reports</li>
</ul>
<p style='color: gray; font-size: 9pt;'>© 2025-2026 Sentinel</p>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("About PDF Sentinel")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(about_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # Add Copy Key button
        copy_btn = msg.addButton("Copy Key", QMessageBox.ButtonRole.ActionRole)
        
        msg.exec()
        
        if msg.clickedButton() == copy_btn:
            clipboard = QApplication.clipboard()
            clipboard.setText(fingerprint)
            QMessageBox.information(self, "Copied", "Key fingerprint copied to clipboard!")


