"""
PDF Sentinel - SHA256 Hasher
Handles hash generation for PDF files.
"""

import hashlib
from pathlib import Path
from typing import Optional


def calculate_sha256(file_path: str | Path) -> str:
    """
    Calculate the SHA256 hash of a file.
    
    Args:
        file_path: Path to the file to hash
        
    Returns:
        SHA256 hash as a hex string with 'sha256:' prefix
    """
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        # Read in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    
    return f"sha256:{sha256_hash.hexdigest()}"


def calculate_content_hash(content: bytes) -> str:
    """
    Calculate the SHA256 hash of raw bytes.
    
    Args:
        content: Raw bytes to hash
        
    Returns:
        SHA256 hash as a hex string with 'sha256:' prefix
    """
    sha256_hash = hashlib.sha256(content)
    return f"sha256:{sha256_hash.hexdigest()}"


def verify_hash(file_path: str | Path, expected_hash: str) -> bool:
    """
    Verify a file's hash against an expected value.
    
    Args:
        file_path: Path to the file to verify
        expected_hash: Expected hash value (with or without 'sha256:' prefix)
        
    Returns:
        True if hashes match, False otherwise
    """
    actual_hash = calculate_sha256(file_path)
    
    # Normalize expected hash
    if not expected_hash.startswith("sha256:"):
        expected_hash = f"sha256:{expected_hash}"
    
    return actual_hash == expected_hash
