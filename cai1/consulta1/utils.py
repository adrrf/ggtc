import os
import hmac
import hashlib


def generate_nonce():
    """Generate a random nonce."""
    return os.urandom(16)


def compute_hmac(content, nonce):
    """
    Compute HMAC of content using the provided nonce.
    Uses a fixed key for this demo, in a real application this would be secure.
    """
    # Use a fixed key for demo purposes (in a real app, this would be a secret)
    key = b"this_is_a_demo_key_for_hmac_calculation_only"

    # Convert nonce to bytes if it's a hex string
    if isinstance(nonce, str):
        nonce = bytes.fromhex(nonce)

    # Combine nonce with content
    data = nonce + content

    # Calculate HMAC
    return hmac.new(key, data, hashlib.sha256).digest()


def compare_digests(a, b):
    """Compare two digests in constant time to prevent timing attacks."""
    return hmac.compare_digest(a, b)
