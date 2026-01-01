"""
PDF Sentinel - Drop Zone Widget
Drag-and-drop area for instant PDF stamping.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QFrame, QHBoxLayout, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
import qtawesome as qta


ICON_COLOR = "#88A9C3"


class DropZoneWidget(QWidget):
    """Main drop zone for single file processing."""
    
    # Signals
    file_dropped = pyqtSignal(str)  # Emitted when a file is dropped
    stamp_completed = pyqtSignal(dict)  # Emitted when stamping completes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Stamp a PDF")
        header.setObjectName("pageHeader")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        subtitle = QLabel("Secure your documents with SHA256 verification")
        subtitle.setObjectName("pageSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addStretch()
        
        # Drop zone area
        self.drop_area = QFrame()
        self.drop_area.setObjectName("dropZone")
        self.drop_area.setMinimumSize(500, 300)
        self.drop_area.setAcceptDrops(True)
        
        drop_layout = QVBoxLayout(self.drop_area)
        drop_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Drop icon (using QtAwesome)
        drop_icon = QLabel()
        drop_icon.setPixmap(qta.icon("fa5s.file-pdf", color=ICON_COLOR).pixmap(QSize(64, 64)))
        drop_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(drop_icon)
        
        # Drop text
        self.drop_label = QLabel("Drag & Drop PDF Here")
        self.drop_label.setObjectName("dropLabel")
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(self.drop_label)
        
        # Or separator
        or_label = QLabel("- or -")
        or_label.setObjectName("orLabel")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(or_label)
        
        # Browse button
        self.browse_btn = QPushButton("  Browse Files")
        self.browse_btn.setIcon(qta.icon("fa5s.folder-open", color="#000000"))
        self.browse_btn.setIconSize(QSize(16, 16))
        self.browse_btn.setObjectName("primaryButton")
        self.browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_btn.clicked.connect(self._browse_file)
        drop_layout.addWidget(self.browse_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.drop_area, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Progress bar (hidden by default)
        self.progress = QProgressBar()
        self.progress.setObjectName("stampProgress")
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Status message
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().lower().endswith('.pdf') for url in urls):
                event.acceptProposedAction()
                self.drop_area.setProperty("dragOver", True)
                self.drop_area.style().unpolish(self.drop_area)
                self.drop_area.style().polish(self.drop_area)
    
    def dragLeaveEvent(self, event):
        """Handle drag leave events."""
        self.drop_area.setProperty("dragOver", False)
        self.drop_area.style().unpolish(self.drop_area)
        self.drop_area.style().polish(self.drop_area)
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events."""
        self.drop_area.setProperty("dragOver", False)
        self.drop_area.style().unpolish(self.drop_area)
        self.drop_area.style().polish(self.drop_area)
        
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.pdf'):
                self._process_file(file_path)
                break  # Process only the first PDF in single mode
    
    def _browse_file(self):
        """Open file dialog to select a PDF."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF File",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            self._process_file(file_path)
    
    def _process_file(self, file_path: str):
        """Process a dropped/selected PDF file."""
        from core.stamper import stamp_pdf
        
        self.status_label.setText(f"Processing: {Path(file_path).name}")
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # Indeterminate
        
        try:
            result = stamp_pdf(file_path)
            self.progress.setVisible(False)
            self.status_label.setText(
                f"Stamped Successfully!\n"
                f"Output: {Path(result['output_path']).name}"
            )
            self.status_label.setProperty("status", "success")
            self.stamp_completed.emit(result)
        except Exception as e:
            self.progress.setVisible(False)
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setProperty("status", "error")
        
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
