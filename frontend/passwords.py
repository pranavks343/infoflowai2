"""Salted password storage for the original local account flow."""
import hashlib
import hmac
import secrets


def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 600000)
    return f"pbkdf2_sha256$600000${salt}${digest.hex()}"


def verify_password(password, stored):
    if not isinstance(stored, str):
        return False
    if not stored.startswith("pbkdf2_sha256$"):
        return hmac.compare_digest(password.encode(), stored.encode())
    try:
        _, iterations, salt, expected = stored.split("$")
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(iterations))
        return hmac.compare_digest(digest.hex(), expected)
    except (ValueError, OverflowError):
        return False
