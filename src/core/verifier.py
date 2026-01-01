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
    signature_valid: Optional[bool] = None
    key_fingerprint: Optional[str] = None


def verify_pdf(pdf_path: str | Path) -> VerificationResult:
    """
    Verify a Sentinel-stamped PDF file.
    
    This checks:
    1. If the PDF has Sentinel metadata
    2. Recalculates the content hash
    3. Compare with the stored content hash
    4. Verify digital signature (if present)
    
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
    signature = metadata.get("sentinel_signature")
    key_fingerprint = metadata.get("sentinel_key_fingerprint")
    
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
    
    # Verify digital signature if present
    signature_valid = None
    if signature and key_fingerprint:
        try:
            from core.signer import verify_signature, get_public_key_pem, get_key_fingerprint
            public_key = get_public_key_pem()
            local_fingerprint = get_key_fingerprint(public_key)
            
            # Only verify if key fingerprints match (same machine)
            if local_fingerprint == key_fingerprint:
                signature_valid = verify_signature(stored_content_hash, signature, public_key)
            else:
                # Different key - can't verify but document may still be valid
                signature_valid = None
        except Exception:
            signature_valid = None
    
    # Compare hashes
    if stored_content_hash == current_content_hash:
        sig_msg = ""
        if signature_valid is True:
            sig_msg = " | Signature verified"
        elif signature_valid is False:
            sig_msg = " | Signature INVALID"
        
        return VerificationResult(
            status=VerificationStatus.VERIFIED,
            message=f"Document integrity verified - No tampering detected{sig_msg}",
            original_hash=original_hash,
            current_hash=current_content_hash,
            timestamp=timestamp,
            version=version,
            signature_valid=signature_valid,
            key_fingerprint=key_fingerprint
        )
    else:
        return VerificationResult(
            status=VerificationStatus.TAMPERED,
            message="TAMPERED - Document content has been modified!",
            original_hash=original_hash,
            current_hash=current_content_hash,
            timestamp=timestamp,
            version=version,
            signature_valid=False,
            key_fingerprint=key_fingerprint
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
