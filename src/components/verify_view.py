"""
PDF Sentinel - Verify View Widget
Verify the integrity of stamped PDFs.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QFrame, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
import qtawesome as qta


ICON_COLOR = "#88A9C3"
SUCCESS_COLOR = "#4ade80"
ERROR_COLOR = "#ff6b6b"
WARNING_COLOR = "#fbbf24"


class VerifyViewWidget(QWidget):
    """Verification view for checking stamped PDFs."""
    
    verification_completed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._last_result = None
        self._last_file_path = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Verify PDF")
        header.setObjectName("pageHeader")
        layout.addWidget(header)
        
        subtitle = QLabel("Check if a stamped PDF has been tampered with")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)
        
        layout.addStretch()
        
        # Drop/select area
        self.verify_area = QFrame()
        self.verify_area.setObjectName("verifyZone")
        self.verify_area.setMinimumSize(400, 200)
        
        verify_layout = QVBoxLayout(self.verify_area)
        verify_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Search icon
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon("fa5s.search", color=ICON_COLOR).pixmap(QSize(48, 48)))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        verify_layout.addWidget(icon_label)
        
        drop_label = QLabel("Drop PDF to Verify")
        drop_label.setObjectName("dropLabel")
        drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        verify_layout.addWidget(drop_label)
        
        browse_btn = QPushButton("  Select File")
        browse_btn.setIcon(qta.icon("fa5s.file", color=ICON_COLOR))
        browse_btn.setIconSize(QSize(14, 14))
        browse_btn.setObjectName("secondaryButton")
        browse_btn.clicked.connect(self._browse_file)
        verify_layout.addWidget(browse_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.verify_area, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Result display
        self.result_frame = QFrame()
        self.result_frame.setObjectName("resultFrame")
        self.result_frame.setVisible(False)
        
        result_layout = QVBoxLayout(self.result_frame)
        
        self.result_icon = QLabel()
        self.result_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(self.result_icon)
        
        self.result_title = QLabel()
        self.result_title.setObjectName("resultTitle")
        self.result_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(self.result_title)
        
        self.result_details = QTextEdit()
        self.result_details.setObjectName("resultDetails")
        self.result_details.setReadOnly(True)
        self.result_details.setMaximumHeight(150)
        result_layout.addWidget(self.result_details)
        
        # Button row
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.setSpacing(12)
        
        # Copy Hash button
        self.copy_btn = QPushButton("  Copy Hash")
        self.copy_btn.setIcon(qta.icon("fa5s.copy", color=ICON_COLOR))
        self.copy_btn.setIconSize(QSize(14, 14))
        self.copy_btn.setObjectName("secondaryButton")
        self.copy_btn.clicked.connect(self._copy_hash)
        btn_layout.addWidget(self.copy_btn)
        
        # Generate Report button
        self.report_btn = QPushButton("  Generate Report")
        self.report_btn.setIcon(qta.icon("fa5s.file-alt", color="#000000"))
        self.report_btn.setIconSize(QSize(14, 14))
        self.report_btn.setObjectName("primaryButton")
        self.report_btn.clicked.connect(self._generate_report)
        btn_layout.addWidget(self.report_btn)
        
        result_layout.addLayout(btn_layout)
        
        layout.addWidget(self.result_frame)
        
        layout.addStretch()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().lower().endswith('.pdf') for url in urls):
                event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events."""
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.pdf'):
                self._verify_file(file_path)
                break
    
    def _browse_file(self):
        """Open file dialog to select a PDF."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF to Verify",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            self._verify_file(file_path)
    
    def _verify_file(self, file_path: str):
        """Verify a PDF file."""
        from core.verifier import verify_pdf, VerificationStatus
        
        path = Path(file_path)
        result = verify_pdf(path)
        
        # Store for report generation
        self._last_result = result
        self._last_file_path = path
        
        self.result_frame.setVisible(True)
        
        if result.status == VerificationStatus.VERIFIED:
            self.result_icon.setPixmap(qta.icon("fa5s.check-circle", color=SUCCESS_COLOR).pixmap(QSize(64, 64)))
            self.result_title.setText("Document Verified")
            self.result_title.setProperty("status", "success")
        elif result.status == VerificationStatus.TAMPERED:
            self.result_icon.setPixmap(qta.icon("fa5s.times-circle", color=ERROR_COLOR).pixmap(QSize(64, 64)))
            self.result_title.setText("TAMPERED - Hash Mismatch!")
            self.result_title.setProperty("status", "error")
        elif result.status == VerificationStatus.NOT_STAMPED:
            self.result_icon.setPixmap(qta.icon("fa5s.exclamation-triangle", color=WARNING_COLOR).pixmap(QSize(64, 64)))
            self.result_title.setText("Not a Sentinel PDF")
            self.result_title.setProperty("status", "warning")
        else:
            self.result_icon.setPixmap(qta.icon("fa5s.question-circle", color=ERROR_COLOR).pixmap(QSize(64, 64)))
            self.result_title.setText("Error")
            self.result_title.setProperty("status", "error")
        
        # Update styling
        self.result_title.style().unpolish(self.result_title)
        self.result_title.style().polish(self.result_title)
        
        # Show details
        details = f"File: {path.name}\n"
        details += f"Status: {result.message}\n"
        if result.original_hash:
            details += f"Hash: {result.original_hash}\n"
        if result.timestamp:
            details += f"Stamped: {result.timestamp}\n"
        if result.version:
            details += f"Version: {result.version}\n"
        
        # Signature status
        if result.signature_valid is True:
            details += f"\n✓ SIGNATURE VERIFIED\n"
            if result.key_fingerprint:
                details += f"Key: {result.key_fingerprint}"
        elif result.signature_valid is False:
            details += f"\n✗ SIGNATURE INVALID"
        elif result.key_fingerprint:
            details += f"\n⚠ Signature present (different key)\nKey: {result.key_fingerprint}"
        
        self.result_details.setText(details)
        
        self.verification_completed.emit({
            "file": file_path,
            "status": result.status.value,
            "message": result.message
        })
    
    def _generate_report(self):
        """Generate a verification report PDF."""
        if self._last_result is None or self._last_file_path is None:
            return
        
        from utils.report import generate_verification_report
        
        # Ask where to save the report
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Verification Report",
            f"{self._last_file_path.stem}_verification_report.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not output_path:
            return
        
        try:
            report_path = generate_verification_report(
                file_name=self._last_file_path.name,
                verification_status=self._last_result.message,
                hash_value=self._last_result.original_hash or "N/A",
                timestamp=self._last_result.timestamp or "N/A",
                output_path=output_path
            )
            
            QMessageBox.information(
                self,
                "Report Generated",
                f"Verification report saved to:\n{report_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to generate report:\n{str(e)}"
            )
    
    def _copy_hash(self):
        """Copy the hash to clipboard."""
        if self._last_result and self._last_result.original_hash:
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(self._last_result.original_hash)
            
            # Show brief confirmation
            QMessageBox.information(
                self,
                "Copied",
                "Hash copied to clipboard!"
            )

