"""
PDF Sentinel - Stamper
Embeds hash metadata and visual seal into PDF files.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF

from core.hasher import calculate_sha256


# Sentinel metadata keys
SENTINEL_METADATA_KEY = "sentinel_data"
SENTINEL_VERSION = "1.0.0"


def _calculate_content_hash(doc: fitz.Document) -> str:
    """
    Calculate a hash of the PDF's text content across all pages.
    This hash will be used to detect tampering.
    
    Args:
        doc: PyMuPDF document object
        
    Returns:
        SHA256 hash of the text content
    """
    hasher = hashlib.sha256()
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        # Get text content
        text = page.get_text("text")
        hasher.update(text.encode("utf-8"))
        
        # Also hash image positions and sizes (detect image swaps)
        images = page.get_images()
        for img in images:
            hasher.update(str(img).encode("utf-8"))
    
    return f"sha256:{hasher.hexdigest()}"


def stamp_pdf(
    input_path: str | Path,
    output_path: Optional[str | Path] = None,
    add_visual_seal: bool = True,
    seal_position: str = "top-right"
) -> dict:
    """
    Stamp a PDF with SHA256 hash metadata and optional visual seal.
    
    Args:
        input_path: Path to the input PDF
        output_path: Path for the stamped PDF (defaults to input with '_stamped' suffix)
        add_visual_seal: Whether to add a visible seal on the first page
        seal_position: Position of seal ('top-right', 'top-left', 'bottom-right', 'bottom-left')
        
    Returns:
        Dictionary with stamping details (hash, timestamp, output_path)
    """
    input_path = Path(input_path)
    
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_stamped.pdf"
    else:
        output_path = Path(output_path)
    
    # Calculate hash of original file
    file_hash = calculate_sha256(input_path)
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Open the PDF
    doc = fitz.open(input_path)
    
    # Calculate content hash BEFORE adding seal (for tamper detection)
    content_hash = _calculate_content_hash(doc)
    
    # Create sentinel metadata
    sentinel_data = {
        "sentinel_hash": file_hash,
        "sentinel_content_hash": content_hash,  # NEW: content-based hash for verification
        "sentinel_timestamp": timestamp,
        "sentinel_version": SENTINEL_VERSION
    }
    
    # Embed metadata
    metadata = doc.metadata or {}
    metadata["keywords"] = json.dumps(sentinel_data)
    doc.set_metadata(metadata)
    
    # Add visual seal if requested
    if add_visual_seal and doc.page_count > 0:
        _add_visual_seal(doc[0], file_hash, timestamp, seal_position)
    
    # Save the stamped PDF
    doc.save(str(output_path))
    doc.close()
    
    return {
        "hash": file_hash,
        "content_hash": content_hash,
        "timestamp": timestamp,
        "input_path": str(input_path),
        "output_path": str(output_path),
        "version": SENTINEL_VERSION
    }


def _add_visual_seal(
    page: fitz.Page,
    file_hash: str,
    timestamp: str,
    position: str
):
    """
    Add a visual seal/badge to a PDF page.
    
    Args:
        page: PyMuPDF page object
        file_hash: The SHA256 hash to display (truncated)
        timestamp: The timestamp to display
        position: Position of the seal
    """
    # Seal dimensions
    seal_width = 150
    seal_height = 50
    margin = 20
    
    # Get page dimensions
    rect = page.rect
    
    # Calculate position
    positions = {
        "top-right": fitz.Rect(
            rect.width - seal_width - margin,
            margin,
            rect.width - margin,
            margin + seal_height
        ),
        "top-left": fitz.Rect(
            margin,
            margin,
            margin + seal_width,
            margin + seal_height
        ),
        "bottom-right": fitz.Rect(
            rect.width - seal_width - margin,
            rect.height - seal_height - margin,
            rect.width - margin,
            rect.height - margin
        ),
        "bottom-left": fitz.Rect(
            margin,
            rect.height - seal_height - margin,
            margin + seal_width,
            rect.height - margin
        )
    }
    
    seal_rect = positions.get(position, positions["top-right"])
    
    # Draw seal background
    shape = page.new_shape()
    shape.draw_rect(seal_rect)
    shape.finish(color=(0.53, 0.66, 0.76), fill=(0.2, 0.2, 0.2), width=1.5)  # #88A9C3 accent
    shape.commit()
    
    # Add text
    short_hash = file_hash[-12:]  # Last 12 chars
    
    # "VERIFIED" header
    page.insert_text(
        (seal_rect.x0 + 10, seal_rect.y0 + 18),
        "SENTINEL VERIFIED",
        fontsize=9,
        fontname="helv",
        color=(0.53, 0.66, 0.76)  # #88A9C3
    )
    
    # Hash snippet
    page.insert_text(
        (seal_rect.x0 + 10, seal_rect.y0 + 32),
        f"Hash: ...{short_hash}",
        fontsize=7,
        fontname="helv",
        color=(0.7, 0.7, 0.7)
    )
    
    # Date
    date_str = timestamp[:10]
    page.insert_text(
        (seal_rect.x0 + 10, seal_rect.y0 + 44),
        f"Date: {date_str}",
        fontsize=7,
        fontname="helv",
        color=(0.7, 0.7, 0.7)
    )


def get_sentinel_metadata(pdf_path: str | Path) -> Optional[dict]:
    """
    Extract Sentinel metadata from a stamped PDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Sentinel metadata dict if found, None otherwise
    """
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        doc.close()
        
        if metadata and "keywords" in metadata:
            try:
                data = json.loads(metadata["keywords"])
                if "sentinel_hash" in data:
                    return data
            except json.JSONDecodeError:
                pass
        
        return None
    except Exception:
        return None


def get_current_content_hash(pdf_path: str | Path) -> Optional[str]:
    """
    Calculate the current content hash of a PDF for verification.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Content hash string or None on error
    """
    try:
        doc = fitz.open(pdf_path)
        
        # We need to calculate hash EXCLUDING our seal text
        # The seal adds: "SENTINEL VERIFIED", "Hash: ...", "Date: ..."
        hasher = hashlib.sha256()
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text = page.get_text("text")
            
            # Filter out our seal text from page 0
            if page_num == 0:
                lines = text.split('\n')
                filtered_lines = []
                for line in lines:
                    # Skip our seal text
                    if line.strip().startswith("SENTINEL VERIFIED"):
                        continue
                    if line.strip().startswith("Hash: ..."):
                        continue
                    if line.strip().startswith("Date: 20"):  # Date format check
                        continue
                    filtered_lines.append(line)
                text = '\n'.join(filtered_lines)
            
            hasher.update(text.encode("utf-8"))
            
            # Also hash image positions and sizes
            images = page.get_images()
            for img in images:
                hasher.update(str(img).encode("utf-8"))
        
        doc.close()
        return f"sha256:{hasher.hexdigest()}"
    except Exception:
        return None
