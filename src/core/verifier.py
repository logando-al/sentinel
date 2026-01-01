"""
PDF Sentinel - Verifier
Verifies the integrity of stamped PDF files.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from core.stamper import get_sentinel_metadata, get_current_content_hash


class VerificationStatus(Enum):
    """Possible verification outcomes."""
    VERIFIED = "verified"
    TAMPERED = "tampered"
    NOT_STAMPED = "not_stamped"
    ERROR = "error"


@dataclass
class VerificationResult:
    """Result of a PDF verification."""
    status: VerificationStatus
    message: str
    original_hash: Optional[str] = None
    current_hash: Optional[str] = None
    timestamp: Optional[str] = None
    version: Optional[str] = None


def verify_pdf(pdf_path: str | Path) -> VerificationResult:
    """
    Verify the integrity of a stamped PDF file.
    
    The verification process:
    1. Extract Sentinel metadata from the PDF
    2. Calculate the current content hash
    3. Compare with the stored content hash
    
    Args:
        pdf_path: Path to the PDF file to verify
        
    Returns:
        VerificationResult with status and details
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        return VerificationResult(
            status=VerificationStatus.ERROR,
            message=f"File not found: {pdf_path}"
        )
    
    if not pdf_path.suffix.lower() == ".pdf":
        return VerificationResult(
            status=VerificationStatus.ERROR,
            message="File is not a PDF"
        )
    
    # Extract Sentinel metadata
    metadata = get_sentinel_metadata(pdf_path)
    
    if metadata is None:
        return VerificationResult(
            status=VerificationStatus.NOT_STAMPED,
            message="This PDF has not been stamped by Sentinel"
        )
    
    # Get stored values
    original_hash = metadata.get("sentinel_hash")
    stored_content_hash = metadata.get("sentinel_content_hash")
    timestamp = metadata.get("sentinel_timestamp")
    version = metadata.get("sentinel_version")
    
    if not original_hash:
        return VerificationResult(
            status=VerificationStatus.ERROR,
            message="Sentinel metadata is corrupted (missing hash)"
        )
    
    # If no content hash stored (old version), fall back to metadata-only check
    if not stored_content_hash:
        return VerificationResult(
            status=VerificationStatus.VERIFIED,
            message="Document verified (legacy stamp - no content hash)",
            original_hash=original_hash,
            current_hash=original_hash,
            timestamp=timestamp,
            version=version
        )
    
    # Calculate current content hash
    current_content_hash = get_current_content_hash(pdf_path)
    
    if current_content_hash is None:
        return VerificationResult(
            status=VerificationStatus.ERROR,
            message="Failed to calculate content hash"
        )
    
    # Compare hashes
    if stored_content_hash == current_content_hash:
        return VerificationResult(
            status=VerificationStatus.VERIFIED,
            message="Document integrity verified - No tampering detected",
            original_hash=original_hash,
            current_hash=current_content_hash,
            timestamp=timestamp,
            version=version
        )
    else:
        return VerificationResult(
            status=VerificationStatus.TAMPERED,
            message="TAMPERED - Document content has been modified!",
            original_hash=original_hash,
            current_hash=current_content_hash,
            timestamp=timestamp,
            version=version
        )


def batch_verify(pdf_paths: list[str | Path]) -> list[tuple[Path, VerificationResult]]:
    """
    Verify multiple PDF files.
    
    Args:
        pdf_paths: List of paths to PDF files
        
    Returns:
        List of (path, result) tuples
    """
    results = []
    for path in pdf_paths:
        path = Path(path)
        result = verify_pdf(path)
        results.append((path, result))
    return results
