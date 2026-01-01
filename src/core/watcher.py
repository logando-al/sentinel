"""
PDF Sentinel - Folder Watcher
Monitors a folder for new PDF files and auto-processes them.
"""

import time
from pathlib import Path
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent


class PDFWatchHandler(FileSystemEventHandler):
    """Handler for PDF file creation events."""
    
    def __init__(
        self,
        on_new_pdf: Callable[[Path], None],
        output_folder: Optional[Path] = None
    ):
        """
        Initialize the watch handler.
        
        Args:
            on_new_pdf: Callback function when a new PDF is detected
            output_folder: Optional folder for stamped output
        """
        super().__init__()
        self.on_new_pdf = on_new_pdf
        self.output_folder = output_folder
        self._processed = set()  # Track processed files to avoid duplicates
    
    def on_created(self, event: FileCreatedEvent):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        path = Path(event.src_path)
        
        # Only process PDF files
        if path.suffix.lower() != ".pdf":
            return
        
        # Skip already processed files
        if str(path) in self._processed:
            return
        
        # Skip stamped files (avoid infinite loop)
        if "_stamped" in path.stem:
            return
        
        # Wait a moment for file to be fully written
        time.sleep(0.5)
        
        # Mark as processed and trigger callback
        self._processed.add(str(path))
        self.on_new_pdf(path)


class FolderWatcher:
    """Watches a folder for new PDF files."""
    
    def __init__(
        self,
        watch_folder: str | Path,
        on_new_pdf: Callable[[Path], None],
        output_folder: Optional[str | Path] = None
    ):
        """
        Initialize the folder watcher.
        
        Args:
            watch_folder: Folder to monitor for new PDFs
            on_new_pdf: Callback when a new PDF is detected
            output_folder: Optional folder for stamped output
        """
        self.watch_folder = Path(watch_folder)
        self.output_folder = Path(output_folder) if output_folder else None
        self.on_new_pdf = on_new_pdf
        
        self._observer: Optional[Observer] = None
        self._running = False
    
    @property
    def is_running(self) -> bool:
        """Check if the watcher is currently running."""
        return self._running
    
    def start(self):
        """Start watching the folder."""
        if self._running:
            return
        
        # Ensure watch folder exists
        self.watch_folder.mkdir(parents=True, exist_ok=True)
        
        # Create and start observer
        handler = PDFWatchHandler(self.on_new_pdf, self.output_folder)
        self._observer = Observer()
        self._observer.schedule(handler, str(self.watch_folder), recursive=False)
        self._observer.start()
        self._running = True
    
    def stop(self):
        """Stop watching the folder."""
        if not self._running or self._observer is None:
            return
        
        self._observer.stop()
        self._observer.join(timeout=5)
        self._observer = None
        self._running = False
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False
