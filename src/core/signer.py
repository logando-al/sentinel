"""
PDF Sentinel - Digital Signer
Provides RSA-based digital signature functionality for PDF documents.
"""

import os
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import base64
import hashlib


def get_keys_dir() -> Path:
    """Get the directory for storing keys."""
    # Store in user's app data
    if os.name == 'nt':  # Windows
        base = Path(os.environ.get('APPDATA', Path.home()))
    else:
        base = Path.home() / '.config'
    
    keys_dir = base / 'PDFSentinel' / 'keys'
    keys_dir.mkdir(parents=True, exist_ok=True)
    return keys_dir


def generate_key_pair() -> tuple[bytes, bytes]:
    """
    Generate a new RSA key pair.
    
    Returns:
        Tuple of (private_key_pem, public_key_pem)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem, public_pem


def get_or_create_keys() -> tuple[bytes, bytes]:
    """
    Get existing keys or create new ones.
    
    Returns:
        Tuple of (private_key_pem, public_key_pem)
    """
    keys_dir = get_keys_dir()
    private_path = keys_dir / 'private_key.pem'
    public_path = keys_dir / 'public_key.pem'
    
    if private_path.exists() and public_path.exists():
        with open(private_path, 'rb') as f:
            private_pem = f.read()
        with open(public_path, 'rb') as f:
            public_pem = f.read()
    else:
        private_pem, public_pem = generate_key_pair()
        with open(private_path, 'wb') as f:
            f.write(private_pem)
        with open(public_path, 'wb') as f:
            f.write(public_pem)
    
    return private_pem, public_pem


def get_key_fingerprint(public_key_pem: bytes) -> str:
    """
    Get a short fingerprint of the public key.
    
    Args:
        public_key_pem: Public key in PEM format
        
    Returns:
        Short hex fingerprint (last 16 chars of SHA256)
    """
    key_hash = hashlib.sha256(public_key_pem).hexdigest()
    return key_hash[-16:].upper()


def sign_hash(content_hash: str, private_key_pem: bytes = None) -> str:
    """
    Sign a content hash using RSA private key.
    
    Args:
        content_hash: The hash string to sign
        private_key_pem: Private key in PEM format (uses stored key if None)
        
    Returns:
        Base64-encoded signature
    """
    if private_key_pem is None:
        private_key_pem, _ = get_or_create_keys()
    
    private_key = serialization.load_pem_private_key(
        private_key_pem,
        password=None,
        backend=default_backend()
    )
    
    signature = private_key.sign(
        content_hash.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    return base64.b64encode(signature).decode('utf-8')


def verify_signature(content_hash: str, signature_b64: str, public_key_pem: bytes) -> bool:
    """
    Verify a signature against a content hash.
    
    Args:
        content_hash: The hash string that was signed
        signature_b64: Base64-encoded signature
        public_key_pem: Public key in PEM format
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        public_key = serialization.load_pem_public_key(
            public_key_pem,
            backend=default_backend()
        )
        
        signature = base64.b64decode(signature_b64)
        
        public_key.verify(
            signature,
            content_hash.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False
    except Exception:
        return False


def get_public_key_pem() -> bytes:
    """Get the public key for embedding in documents."""
    _, public_pem = get_or_create_keys()
    return public_pem
