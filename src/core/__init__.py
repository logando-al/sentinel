"""
PDF Sentinel - Core Module
"""

from core.hasher import calculate_sha256, calculate_content_hash, verify_hash
from core.stamper import stamp_pdf, get_sentinel_metadata, SENTINEL_VERSION
from core.verifier import verify_pdf, batch_verify, VerificationStatus, VerificationResult
from core.watcher import FolderWatcher


__all__ = [
    # Hasher
    "calculate_sha256",
    "calculate_content_hash", 
    "verify_hash",
    # Stamper
    "stamp_pdf",
    "get_sentinel_metadata",
    "SENTINEL_VERSION",
    # Verifier
    "verify_pdf",
    "batch_verify",
    "VerificationStatus",
    "VerificationResult",
    # Watcher
    "FolderWatcher",
]
