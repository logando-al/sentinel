"""
PDF Sentinel - Watch View Widget
Configure folder watching for auto-processing.
"""

from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QFrame, QListWidget,
    QListWidgetItem, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot


class WatcherThread(QThread):
    """Background thread for folder watching."""
    
    new_pdf = pyqtSignal(str)  # Emitted when a new PDF is detected
    
    def __init__(self, folder: Path, parent=None):
        super().__init__(parent)
        self.folder = folder
        self._running = False
    
    def run(self):
        """Run the watcher."""
        from core.watcher import FolderWatcher
        
        def on_new_pdf(path: Path):
            self.new_pdf.emit(str(path))
        
        self._watcher = FolderWatcher(self.folder, on_new_pdf)
        self._watcher.start()
        self._running = True
        
        while self._running:
            self.msleep(100)
        
        self._watcher.stop()
    
    def stop(self):
        """Stop the watcher."""
        self._running = False


class WatchViewWidget(QWidget):
    """Folder watch configuration view."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._watcher_thread: WatcherThread | None = None
        self._watch_folder: Path | None = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Folder Watch")
        header.setObjectName("pageHeader")
        layout.addWidget(header)
        
        subtitle = QLabel("Automatically stamp new PDFs dropped into a folder")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)
        
        # Folder selection
        folder_frame = QFrame()
        folder_frame.setObjectName("settingsFrame")
        folder_layout = QHBoxLayout(folder_frame)
        
        folder_label = QLabel("Watch Folder:")
        folder_layout.addWidget(folder_label)
        
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select a folder to watch...")
        self.folder_input.setReadOnly(True)
        folder_layout.addWidget(self.folder_input, 1)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondaryButton")
        browse_btn.clicked.connect(self._select_folder)
        folder_layout.addWidget(browse_btn)
        
        layout.addWidget(folder_frame)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Start Watching")
        self.start_btn.setObjectName("primaryButton")
        self.start_btn.clicked.connect(self._toggle_watching)
        self.start_btn.setEnabled(False)
        control_layout.addWidget(self.start_btn)
        
        control_layout.addStretch()
        
        # Status indicator
        self.status_indicator = QLabel("● Stopped")
        self.status_indicator.setObjectName("statusIndicator")
        control_layout.addWidget(self.status_indicator)
        
        layout.addLayout(control_layout)
        
        # Activity log
        log_label = QLabel("Activity Log")
        log_label.setObjectName("sectionHeader")
        layout.addWidget(log_label)
        
        self.activity_log = QListWidget()
        self.activity_log.setObjectName("activityLog")
        layout.addWidget(self.activity_log, 1)
        
        # Clear log button
        clear_btn = QPushButton("Clear Log")
        clear_btn.setObjectName("textButton")
        clear_btn.clicked.connect(self.activity_log.clear)
        layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)
    
    def _select_folder(self):
        """Select a folder to watch."""
        folder = QFileDialog.getExistingDirectory(self, "Select Watch Folder")
        if folder:
            self._watch_folder = Path(folder)
            self.folder_input.setText(folder)
            self.start_btn.setEnabled(True)
    
    def _toggle_watching(self):
        """Toggle folder watching on/off."""
        if self._watcher_thread and self._watcher_thread.isRunning():
            self._stop_watching()
        else:
            self._start_watching()
    
    def _start_watching(self):
        """Start watching the folder."""
        if not self._watch_folder:
            return
        
        self._watcher_thread = WatcherThread(self._watch_folder)
        self._watcher_thread.new_pdf.connect(self._on_new_pdf)
        self._watcher_thread.start()
        
        self.start_btn.setText("⏹ Stop Watching")
        self.status_indicator.setText("● Watching")
        self.status_indicator.setProperty("active", True)
        self.status_indicator.style().unpolish(self.status_indicator)
        self.status_indicator.style().polish(self.status_indicator)
        
        self._log_activity("Started watching folder")
    
    def _stop_watching(self):
        """Stop watching the folder."""
        if self._watcher_thread:
            self._watcher_thread.stop()
            self._watcher_thread.wait()
            self._watcher_thread = None
        
        self.start_btn.setText("▶ Start Watching")
        self.status_indicator.setText("● Stopped")
        self.status_indicator.setProperty("active", False)
        self.status_indicator.style().unpolish(self.status_indicator)
        self.status_indicator.style().polish(self.status_indicator)
        
        self._log_activity("Stopped watching")
    
    @pyqtSlot(str)
    def _on_new_pdf(self, file_path: str):
        """Handle new PDF detected."""
        from core.stamper import stamp_pdf
        
        path = Path(file_path)
        self._log_activity(f"New PDF detected: {path.name}")
        
        try:
            result = stamp_pdf(path)
            self._log_activity(f"✅ Stamped: {path.name}")
        except Exception as e:
            self._log_activity(f"❌ Error stamping {path.name}: {e}")
    
    def _log_activity(self, message: str):
        """Add a message to the activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        item = QListWidgetItem(f"[{timestamp}] {message}")
        self.activity_log.insertItem(0, item)
