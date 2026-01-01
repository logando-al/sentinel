"""
PDF Sentinel - Batch View Widget
Process multiple PDF files at once.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QHeaderView, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
import qtawesome as qta


ICON_COLOR = "#88A9C3"


class BatchViewWidget(QWidget):
    """Batch processing view for multiple PDFs."""
    
    batch_completed = pyqtSignal(list)  # Emitted when batch processing completes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._files: list[Path] = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        header = QLabel("Batch Processing")
        header.setObjectName("pageHeader")
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        # Add files button
        add_btn = QPushButton("  Add Files")
        add_btn.setIcon(qta.icon("fa5s.plus", color=ICON_COLOR))
        add_btn.setIconSize(QSize(14, 14))
        add_btn.setObjectName("secondaryButton")
        add_btn.clicked.connect(self._add_files)
        header_layout.addWidget(add_btn)
        
        # Add folder button
        folder_btn = QPushButton("  Add Folder")
        folder_btn.setIcon(qta.icon("fa5s.folder", color=ICON_COLOR))
        folder_btn.setIconSize(QSize(14, 14))
        folder_btn.setObjectName("secondaryButton")
        folder_btn.clicked.connect(self._add_folder)
        header_layout.addWidget(folder_btn)
        
        layout.addLayout(header_layout)
        
        # File table
        self.table = QTableWidget()
        self.table.setObjectName("batchTable")
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["File Name", "Size", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # Bottom controls
        bottom_layout = QHBoxLayout()
        
        # File count
        self.count_label = QLabel("0 files selected")
        self.count_label.setObjectName("countLabel")
        bottom_layout.addWidget(self.count_label)
        
        bottom_layout.addStretch()
        
        # Clear button
        clear_btn = QPushButton("Clear All")
        clear_btn.setObjectName("dangerButton")
        clear_btn.clicked.connect(self._clear_files)
        bottom_layout.addWidget(clear_btn)
        
        # Process button
        self.process_btn = QPushButton("  Stamp All")
        self.process_btn.setIcon(qta.icon("fa5s.bolt", color="#000000"))
        self.process_btn.setIconSize(QSize(14, 14))
        self.process_btn.setObjectName("primaryButton")
        self.process_btn.clicked.connect(self._process_all)
        bottom_layout.addWidget(self.process_btn)
        
        layout.addLayout(bottom_layout)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setObjectName("batchProgress")
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
    
    def _add_files(self):
        """Add files via file dialog."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF Files",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        for f in files:
            self._add_file(Path(f))
    
    def _add_folder(self):
        """Add all PDFs from a folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            for pdf in Path(folder).glob("*.pdf"):
                self._add_file(pdf)
    
    def _add_file(self, path: Path):
        """Add a file to the table."""
        if path in self._files:
            return
        
        self._files.append(path)
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # File name
        self.table.setItem(row, 0, QTableWidgetItem(path.name))
        
        # Size
        size_kb = path.stat().st_size / 1024
        size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
        self.table.setItem(row, 1, QTableWidgetItem(size_str))
        
        # Status
        self.table.setItem(row, 2, QTableWidgetItem("Pending"))
        
        self._update_count()
    
    def _clear_files(self):
        """Clear all files from the table."""
        self._files.clear()
        self.table.setRowCount(0)
        self._update_count()
    
    def _update_count(self):
        """Update the file count label."""
        count = len(self._files)
        self.count_label.setText(f"{count} file{'s' if count != 1 else ''} selected")
    
    def _process_all(self):
        """Process all files in the batch."""
        if not self._files:
            return
        
        from core.stamper import stamp_pdf
        
        self.progress.setVisible(True)
        self.progress.setRange(0, len(self._files))
        self.progress.setValue(0)
        self.process_btn.setEnabled(False)
        
        results = []
        
        for i, path in enumerate(self._files):
            try:
                self.table.item(i, 2).setText("Processing...")
                result = stamp_pdf(path)
                self.table.item(i, 2).setText("Done")
                results.append(result)
            except Exception as e:
                self.table.item(i, 2).setText("Error")
            
            self.progress.setValue(i + 1)
        
        self.progress.setVisible(False)
        self.process_btn.setEnabled(True)
        self.batch_completed.emit(results)
