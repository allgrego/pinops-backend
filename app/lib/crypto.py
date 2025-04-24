import hashlib
import binascii
import os


def generate_salt() -> bytes:
    """Generates a random salt."""
    return os.urandom(16)  # 16 bytes of random data

def hash_password(password: str, salt: bytes) -> str:
    """Hashes the password using SHA-256 with the provided salt."""
    salted_password = salt + password.encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    return f"{salt.hex()}:{hashed_password}"

def verify_password(plain_password: str, hashed_password_with_salt: str) -> bool:
    """Verifies the plain password against the hashed password and salt."""
    try:
        salt_hex, stored_hash = hashed_password_with_salt.split(':')
        salt = bytes.fromhex(salt_hex)
        hashed_attempt = hashlib.sha256(salt + plain_password.encode('utf-8')).hexdigest()
        return hashed_attempt == stored_hash
    except (ValueError, binascii.Error):
        # Handle cases where the stored hash is malformed
        return False