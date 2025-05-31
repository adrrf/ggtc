from phe import paillier


def generate_keys():
    """Generate a pair of public and private keys for homomorphic encryption."""
    public_key, private_key = paillier.generate_paillier_keypair()
    return public_key, private_key


def encrypt_value(public_key, value):
    """Encrypt a numeric value using the public key."""
    return public_key.encrypt(value)


def decrypt_value(private_key, encrypted_value):
    """Decrypt an encrypted value using the private key."""
    return private_key.decrypt(encrypted_value)
