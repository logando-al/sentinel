"""
PDF Sentinel - PDF Utilities
Helper functions for PDF file handling.
"""

from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF


def is_valid_pdf(file_path: str | Path) -> bool:
    """
    Check if a file is a valid PDF.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file is a valid PDF, False otherwise
    """
    try:
        doc = fitz.open(file_path)
        is_valid = doc.is_pdf
        doc.close()
        return is_valid
    except Exception:
        return False


def get_pdf_info(file_path: str | Path) -> Optional[dict]:
    """
    Get basic information about a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary with PDF info (pages, title, author, etc.) or None on error
    """
    try:
        path = Path(file_path)
        doc = fitz.open(path)
        
        info = {
            "file_name": path.name,
            "file_path": str(path),
            "file_size": path.stat().st_size,
            "page_count": doc.page_count,
            "is_encrypted": doc.is_encrypted,
            "metadata": doc.metadata,
        }
        
        # Get first page dimensions
        if doc.page_count > 0:
            page = doc[0]
            rect = page.rect
            info["page_width"] = rect.width
            info["page_height"] = rect.height
        
        doc.close()
        return info
    except Exception:
        return None


def extract_text_preview(file_path: str | Path, max_chars: int = 500) -> str:
    """
    Extract a text preview from the first page of a PDF.
    
    Args:
        file_path: Path to the PDF file
        max_chars: Maximum characters to extract
        
    Returns:
        Text preview string
    """
    try:
        doc = fitz.open(file_path)
        if doc.page_count == 0:
            return ""
        
        text = doc[0].get_text()[:max_chars]
        doc.close()
        return text.strip()
    except Exception:
        return ""
